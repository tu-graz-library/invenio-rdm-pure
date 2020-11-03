# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

import json

import requests
from flask import current_app

from invenio_rdm_pure.setup import versioning_running
from invenio_rdm_pure.source.general_functions_source import add_spaces
from invenio_rdm_pure.source.rdm.delete_record import Delete
from invenio_rdm_pure.source.rdm.requests_rdm import Requests
from invenio_rdm_pure.source.reports import Reports


class GeneralFunctions:
    """Description."""

    def __init__(self):
        """Description."""
        self.rdm_requests = Requests()
        self.reports = Reports()
        self.delete = Delete()

    def get_recid(self, uuid: str, global_counters: object):
        """
        Given a records' uuid, it returns all relative recids.

        It if needed to:
        1 - check if there are duplicates
        2 - delete duplicates
        3 - add the record uuid and recid to all_rdm_records.txt.
        """
        response = self.rdm_requests.get_metadata_by_query(uuid)

        resp_json = json.loads(response.content)

        total_recids = resp_json["hits"]["total"]
        if total_recids == 0:
            # If there are no records with the same uuid means it is the first one (version 1)
            return False

        # Iterate over all records with the same uuid
        # The first record is the most recent (they are sorted)
        count = 0
        for item in resp_json["hits"]["hits"]:
            count += 1

            recid = item["metadata"]["recid"]

            if count == 1:
                # URLs to be transmitted to Pure if the record is successfuly added in RDM      # TODO TODO TODO TODO TODO
                rdm_host_url = current_app.config.get("RDM_HOST_URL")
                api_url = f"{rdm_host_url}api/records/{recid}"
                landing_page_url = f"{rdm_host_url}records/{recid}"
                newest_recid = recid

                report = f"\tRDM get recid @ {response} @ Total: {add_spaces(total_recids)} @ {api_url}"
                self.reports.add(report)

            else:
                # If versioning is running then it is not necessary to delete older versions of the record
                if not versioning_running:
                    # Duplicate records are deleted
                    response = self.delete.record(recid)

                    if response:
                        global_counters["delete"]["success"] += 1
                    else:
                        global_counters["delete"]["error"] += 1

        return newest_recid

    #   ---         ---         ---
    def get_userid_from_list_by_externalid(self, external_id: str, file_data: list):
        """Given a user external_id, it checks if it is listed in data/user_ids_match.txt.

        If it is found it returns its relative user id.
        """
        for line in file_data:
            line = line.split("\n")[0]
            line = line.split(" ")

            # Checks if at least one of the ids match
            if external_id == line[2]:
                user_id = line[0]
                user_id_spaces = add_spaces(user_id)

                report = f"\tRDM owner list @@ User id:     {user_id_spaces} @ externalId: {external_id}"
                self.reports.add(report)

                return user_id

    #   ---         ---         ---
    def update_rdm_record(self, recid: str, data: object):
        """Description."""
        response = self.rdm_requests.put_metadata(recid, data)

        rdm_host_url = current_app.config.get("RDM_HOST_URL")
        url = f"{rdm_host_url}api/records/{recid}"
        self.reports.add(f"\tRecord update @ {response} @ {url}")

        return response
