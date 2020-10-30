import time

from source.general_functions import current_time, file_read_lines
from source.rdm.requests import Requests
from source.reports import Reports

from setup import data_files_name, push_dist_sec


class Delete:
    def __init__(self):
        self.rdm_requests = Requests()
        self.report = Reports()

    def record(self, recid: str):
        """ Deletes record from RDM """

        # NOTE: the user ACCOUNT related to the used TOKEN must be ADMIN

        # Delete record request
        response = self.rdm_requests.delete_metadata(recid)

        report = f"\tRDM delete record @ {response} @ Deleted recid:        {recid}"
        self.report.add(report)

        # 410 -> "PID has been deleted"
        if response.status_code >= 300 and response.status_code != 410:
            return response

        # Remove deleted recid from to_delete.txt
        self._remove_recid_from_delete_list(recid)

        # remove record from all_rdm_records.txt
        self._remove_recid_from_records_list(recid)

        return response

    def _set_counters_and_title(func):
        def _wrapper(self):
            self.report.add_template(
                ["console"], ["general", "title"], ["DELETE FROM LIST"]
            )
            self.counters = {"total": 0, "success": 0, "error": 0}
            # Decorated function
            func(self)

            report = f"\nTotal: {self.counters['total']} @ Success: {self.counters['success']} @ Error: {self.counters['error']}"
            self.report.add(report)

        return _wrapper

    @_set_counters_and_title
    def from_list(self):
        """ Deletes all recids that are listed into data/to_delete.txt """

        recids = self._read_file_recids()
        if not recids:
            return

        for recid in recids:

            recid = recid.strip("\n")

            # Ignore empty lines
            if len(recid) == 0:
                continue

            self.counters["total"] += 1

            if len(recid) != 11:
                self.report.add(f"\n{recid} -> Wrong recid lenght! \n")
                continue

            # -- REQUEST --
            response = self.record(recid)

            # 410 -> "PID has been deleted"
            if response.status_code < 300 or response.status_code == 410:
                self.counters["success"] += 1
            else:
                self.counters["error"] += 1

    def all_records(self):
        """ Delete all RDM records """
        file_data = open(data_files_name["all_rdm_records"]).readlines()
        for line in file_data:
            recid = line.split(" ")[1].strip("\n")
            self.record(recid)

    def _read_file_recids(self):
        """ Reads from to_delete.txt all recids to be deleted """
        file_name = data_files_name["delete_recid_list"]
        recids = open(file_name, "r").readlines()
        if len(recids) == 0:
            self.report.add("\nNothing to delete.\n")
            return False
        return recids

    def _remove_recid_from_delete_list(self, recid):
        file_name = "delete_recid_list"
        lines = file_read_lines(file_name)
        with open(data_files_name[file_name], "w") as f:
            for line in lines:
                if line.strip("\n") != recid:
                    f.write(line)

    def _remove_recid_from_records_list(self, recid):
        file_name = "all_rdm_records"
        lines = file_read_lines(file_name)
        with open(data_files_name[file_name], "w") as f:
            for line in lines:
                if line.strip("\n").split(" ")[1] != recid:
                    f.write(line)
