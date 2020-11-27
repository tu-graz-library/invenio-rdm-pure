# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

import json

from ..general_functions_source import add_spaces
from ..reports import Reports
from .general_functions import GeneralFunctions
from .record_manager import RecordManager
from .requests_rdm import Requests


class Versioning:
    """Description."""

    def __init__(self):
        """Description."""
        self.report = Reports()
        self.rdm_requests = Requests()
        self.general_functions = GeneralFunctions()

    def get_uuid_version(self, uuid):
        """Gives the version to use for a new record and old versions of the same uuid."""
        # Request
        response = self.rdm_requests.get_metadata_by_query(uuid)

        resp_json = json.loads(response.content)

        message = f"\tRDM metadata version  - {response} - "

        total_recids = resp_json["hits"]["total"]
        all_metadata_versions = []

        if total_recids == 0:
            # If there are no records with the same uuid means it is the first one (version 1)
            new_version = 1
            self.report.add(f"{message}Record NOT found    - Metadata version: 1")
            return [new_version, all_metadata_versions]

        new_version = None

        # Iterates over all records in response
        for item in resp_json["hits"]["hits"]:
            rdm_metadata = item["metadata"]

            # If a record has a differnt uuid than it will be ignored
            if uuid != rdm_metadata["uuid"]:
                self.report.add(f" VERSIONING - Different uuid {rdm_metadata['uuid']}")
                continue

            # Get the latest version
            if "metadataVersion" in rdm_metadata and not new_version:
                new_version = rdm_metadata["metadataVersion"] + 1

            # Add data to listed versions (old versions)
            recid = item["id"]
            creation_date = item["created"].split("T")[0]
            version = str(rdm_metadata["metadataVersion"])
            all_metadata_versions.append([recid, version, creation_date])

        # In case the record has no metadataVersion
        if not new_version:
            message += f"Vers. not specified - New metadata version: 1"
            new_version = 1
        else:
            count_old_versions = add_spaces(len(all_metadata_versions))
            message += (
                f"Older versions{count_old_versions} - New version: {new_version}"
            )

        self.report.add(message)

        return [new_version, all_metadata_versions]

    def update_all_uuid_versions(self, uuid):
        """Description."""
        # Request
        response = self.rdm_requests.get_metadata_by_query(uuid)

        resp_json = json.loads(response.content)
        total_recids = resp_json["hits"]["total"]

        if total_recids == 0:
            self.report.add("There are no records with this uuid")
            return

        all_metadata_versions = []
        for item in resp_json["hits"]["hits"]:
            # Add data to listed versions
            recid = item["id"]
            creation_date = item["created"].split("T")[0]
            version = str(item["metadata"]["metadataVersion"])
            all_metadata_versions.append([recid, version, creation_date])

        self.report.add(f"\tUpdate uuid versions")

        for item in resp_json["hits"]["hits"]:

            recid = item["id"]
            item = item["metadata"]

            if item["metadataOtherVersions"] == all_metadata_versions:
                self.report.add(f"\tRecord update @ Up to date @ {recid}")
                continue

            item["metadataOtherVersions"] = all_metadata_versions

            # Update record
            RecordManager.instance().update_record(recid, item)
