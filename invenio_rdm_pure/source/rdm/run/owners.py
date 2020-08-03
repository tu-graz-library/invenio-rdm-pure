import json
from datetime import date, datetime
from setup import (
    pure_rest_api_url,
    rdm_host_url,
    token_rdm,
    data_files_name,
    pure_uuid_length,
)
from source.general_functions import (
    initialize_counters,
    add_spaces,
    shorten_file_name,
    file_read_lines,
)
from source.pure.general_functions import get_next_page
from source.pure.requests import get_pure_metadata
from source.rdm.general_functions import GeneralFunctions
from source.rdm.add_record import RdmAddRecord
from source.rdm.database import RdmDatabase
from source.rdm.requests import Requests
from source.reports import Reports


class RdmOwners:
    def __init__(self):
        self.rdm_requests = Requests()
        self.rdm_db = RdmDatabase()
        self.report = Reports()
        self.rdm_add_record = RdmAddRecord()
        self.general_functions = GeneralFunctions()
        self.report_files = ["console", "owners"]

    def _set_counters_and_title(func):
        def _wrapper(self, identifier, identifier_value):

            self.report.add_template(
                ["console"], ["general", "title"], ["OWNERS CHECK"]
            )
            self.global_counters = initialize_counters()

            # Decorated function
            func(self, identifier, identifier_value)

        return _wrapper

    @_set_counters_and_title
    def run_owners(self, identifier: str, identifier_value: str):
        """ Gets from pure all the records related to a certain user (based on orcid or externalId),
            afterwards it modifies/create RDM records accordingly. """

        self.report.add(f"\n{identifier}: {identifier_value}\n")

        # Gets the ID and IP of the logged in user
        self.user_id = self._get_user_id_from_rdm()
        # If the user was not found in RDM then there is no owner to add to the record.
        if not self.user_id:
            return

        # Get from pure user_uuid
        self.user_uuid = self._get_user_uuid_from_pure(identifier, identifier_value)
        if not self.user_uuid:
            return False

        # Add user to user_ids_match.txt
        if identifier == "externalId":
            self._add_user_ids_match(identifier_value)

        next_page = True
        page = 1
        self.local_counters = {"create": 0, "in_record": 0, "to_update": 0}

        while next_page:

            # Pure request
            params = {"sort": "modified", "page": page, "pageSize": 100}
            response = get_pure_metadata(
                "persons", f"{self.user_uuid}/research-outputs", params
            )
            if response.status_code >= 300:
                return False

            # Initial response proceses and json load
            pure_json = self._process_response(response, page)
            # In case the user has no records
            if not pure_json:
                return True

            # Checks if there is a 'next' page to be processed
            next_page = get_next_page(pure_json)

            # Iterates over all items in the page
            for item in pure_json["items"]:

                uuid = item["uuid"]
                title = shorten_file_name(item["title"])

                self.report.add(f"\n\tRecord uuid  @ {uuid} @ {title}")

                # Get from RDM the recid
                recid = self.general_functions.get_recid(uuid, self.global_counters)

                # Record NOT in RDM, create it
                if recid == False:
                    self._create_rdm_record(item)
                    continue

                # Gets record metadata from RDM and checks if the user is already a record owner
                self._process_record_owners(recid)

            page += 1

        self._final_report()

    def _process_record_owners(self, recid):
        """ Gets record metadata from RDM and checks if the user is already a record owner """

        response = self.rdm_requests.get_metadata_by_recid(recid)
        rdm_json = json.loads(response.content)["metadata"]

        self.report.add(
            f"\tRDM get metadata @ {response} @ Current owners: @ {rdm_json['_owners']}"
        )

        if self.user_id not in rdm_json["_owners"]:
            # The record is in RDM but the logged in user is not among the recod owners
            self._add_user_as_owner(rdm_json, recid)
        else:
            # The record is in RDM and the user is an owner
            self.report.add("\tRDM record status @@ Owner IN record")
            self.local_counters["in_record"] += 1

    def _add_user_as_owner(self, data, recid):
        """ Adds the current logged in user as record owner """

        # When updating a record it is not possible to specify _communities field
        del data["_communities"]

        data["_owners"].append(self.user_id)

        self.report.add(
            f"\tRDM record status @ ADDING owner @ New owners: @ {data['_owners']}"
        )

        # Add owner to an existing RDM record
        self.general_functions.update_rdm_record(recid, data)

        self.local_counters["to_update"] += 1

    def _create_rdm_record(self, item: dict):
        """ If a record of the processed user is not in RDM creates it """
        item["_owners"] = [self.user_id]

        self.report.add("\tRDM record status @@ CREATE record")
        self.local_counters["create"] += 1

        # Creates record metadata and pushes it to RDM
        self.rdm_add_record.create_invenio_data(self.global_counters, item)

    def _final_report(self):
        # Final report
        create = self.local_counters["create"]
        update = self.local_counters["to_update"]
        in_rec = self.local_counters["in_record"]
        report = f"\nCreate: {create} - To update: {update} - In record: {in_rec}"
        self.report.add(report, self.report_files)
        self.report.summary_global_counters(self.report_files, self.global_counters)

    def _process_response(self, response: object, page: int):
        """ Checks if there are records to process """

        # Load response json
        resp_json = json.loads(response.content)

        total_items = resp_json["count"]

        if page == 1:
            self.report.add(f"Total records: {total_items}")

        if page == 1 and total_items == 0:
            self.report.add("\nThe user has no records @ End task\n")
            return False

        self.report.add(f"\nPag {page} - Get person records    - {response}")
        return resp_json

    def _get_user_uuid_from_pure(self, key_name: str, key_value: str):
        """ Given the user's external id it return the relative user uuid  """

        # If the uuid is not found in the first x items then it will continue with the next page
        page = 1
        page_size = 10
        next_page = True

        while next_page:

            params = {"page": page, "pageSize": page_size, "q": f'"{key_value}"'}
            response = get_pure_metadata("persons", "", params)

            if response.status_code >= 300:
                self.report.add(response.content, self.report_files)
                return False

            record_json = json.loads(response.content)

            total_items = record_json["count"]

            for item in record_json["items"]:

                if item[key_name] == key_value:
                    first_name = item["name"]["firstName"]
                    lastName = item["name"]["lastName"]
                    uuid = item["uuid"]

                    self.report.add(
                        f"Name:    {first_name} {lastName}\nUuid:    {uuid}",
                        self.report_files,
                    )

                    if len(uuid) != pure_uuid_length:
                        self.report.add(
                            "\n- Warning! Incorrect user_uuid length -\n",
                            self.report_files,
                        )
                        return False
                    return uuid

            # Checks if there is a 'next' page to be processed
            next_page = get_next_page(record_json)

            page += 1

        self.report.add(f"Uuid NOT FOUND - End task\n", self.report_files)
        return False

    #   ---         ---         ---
    def _get_user_id_from_rdm(self):
        """ Gets the ID and IP of the logged in user """

        table_name = "accounts_user_session_activity"

        # SQL query
        response = self.rdm_db.select_query("user_id, ip", table_name)

        if not response:
            self.report.add(
                f"\n- {table_name}: No user is logged in -\n", self.report_files
            )
            return False

        elif len(response) > 1:
            self.report.add(
                f"\n- {table_name}: Multiple users logged in \n", self.report_files
            )
            return False

        self.report.add(
            f"user IP: {response[0][1]}\nUser id: {response[0][0]}", self.report_files
        )

        return response[0][0]

    def _add_user_ids_match(self, external_id: str):
        """ Add user to user_ids_match.txt, where are specified:
            rdm_user_id, user_uuid and user_external_id """
        file_name = data_files_name["user_ids_match"]

        needs_to_add = self._check_user_ids_match("user_ids_match", external_id)

        if needs_to_add:
            open(file_name, "a").write(
                f"{self.user_id} {self.user_uuid} {external_id}\n"
            )
            report = f"user_ids_match @ Adding id toList @ {self.user_id}, {self.user_uuid}, {external_id}"
            self.report.add(report, self.report_files)

    def _check_user_ids_match(self, file_name: str, external_id: str):

        lines = file_read_lines(file_name)
        for line in lines:
            line = line.split("\n")[0]
            line = line.split(" ")

            # Checks if at least one of the ids match
            if (
                str(self.user_id) == line[0]
                or self.user_uuid == line[1]
                or external_id == line[2]
            ):

                if line == [str(self.user_id), self.user_uuid, external_id]:
                    self.report.add("Ids list:   user in list", self.report_files)
                    return False
        return True
