# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

import json
import os

from source.general_functions import add_spaces
from source.pure.requests import get_pure_metadata
from source.rdm.database import RdmDatabase
from source.rdm.general_functions import GeneralFunctions
from source.rdm.requests import Requests
from source.reports import Reports


class RdmGroups:
    """Description."""

    def __init__(self):
        """Description."""
        self.rdm_db = RdmDatabase()
        self.report = Reports()
        self.rdm_requests = Requests()
        self.general_functions = GeneralFunctions()
        self.report_files = ["console", "groups"]

    def _general_report_and_variables(func):
        """Description."""
        def _wrapper(self, old_group_externalId, new_groups_externalIds):
            self.report.add_template(
                self.report_files, ["general", "title"], ["GROUP SPLIT"]
            )
            self.report.add(
                f"\nOld group: {old_group_externalId} @ New groups: {new_groups_externalIds}\n",
                self.report_files,
            )

            # Get name and uuid of new groups
            self.new_groups_data = []

            # Decorated function
            func(self, old_group_externalId, new_groups_externalIds)

        return _wrapper

    @_general_report_and_variables
    def rdm_group_split(self, old_group_externalId: str, new_groups_externalIds: list):
        """
        1 - Create new groups.

        2 - Add users to new groups.

        3 - Remove users from old group.

        4 - Delete old group.

        5 - Modify RDM record:.

            . group_restrictions
            . managingOrganisationUnit (if necessary)
            . organisationUnits
        """
        for externalId in new_groups_externalIds:
            # Get group information
            group_name = self._get_pure_group_metadata(externalId)
            if not group_name:
                return False

            # Create new group
            response = self.rdm_create_group(externalId, group_name)

        # Get old group id
        old_group_id = self._get_rdm_group_id(old_group_externalId)
        if not old_group_id:
            return False

        # Removes users from old group and adds to new groups
        self._rdm_split_users_from_old_to_new_group(
            old_group_id, old_group_externalId, new_groups_externalIds
        )

        # Modify all related records
        self._rdm_split_modify_record(old_group_externalId, new_groups_externalIds)

    def _general_report_and_variables(func):
        """Description."""
        def _wrapper(self, old_groups_externalId, new_group_externalId):
            self.report.add_template(
                self.report_files, ["general", "title"], ["GROUP MERGE"]
            )
            report = f"\nOld groups: {old_groups_externalId} @ New group: {new_group_externalId}\n"
            self.report.add(report, self.report_files)

            # Get new group information
            self.new_groups_data = []

            # Decorated function
            func(self, old_groups_externalId, new_group_externalId)

        return _wrapper

    @_general_report_and_variables
    def rdm_group_merge(self, old_groups_externalId: list, new_group_externalId: str):
        """
        1 - Create new group.

        2 - Add users to new group.

        3 - Remove users from old groups.

        4 - Delete old groups.

        5 - Modify RDM records:.

            . group_restrictions
            . managingOrganisationUnit (if necessary)
            . organisationUnits.
        """
        group_name = self._get_pure_group_metadata(new_group_externalId)
        if not group_name:
            return False

        # Create new group
        response = self.rdm_create_group(new_group_externalId, group_name)

        # Adds users to new group and removes them from the old ones
        self._merge_users_from_old_to_new_group(
            old_groups_externalId, new_group_externalId
        )

        # Modify all related records
        self._rdm_merge_modify_records(
            old_groups_externalId, self.new_groups_data[0], new_group_externalId
        )

    def _get_rdm_group_id(self, externalId: str):
        """Description."""
        response = self.rdm_db.select_query(
            "id, description", "accounts_role", {"name": f"'{externalId}'"}
        )

        if not response:
            return False

        group_id = response[0][0]
        group_name = response[0][1]

        report = f"\tOld group info @ ExtId: {add_spaces(externalId)} @ RDM id: {add_spaces(group_id)} @ {group_name}"
        self.report.add(report, self.report_files)
        return group_id

    def _rdm_split_modify_record(self, old_group_externalId: str, new_groups_externalIds: list):
        """Description."""
        # Get from RDM all old group's records
        response = self.rdm_requests.get_metadata_by_query(old_group_externalId)

        resp_json = json.loads(response.content)
        total_items = resp_json["hits"]["total"]

        report = f"\tModify old g. records @ ExtId: {add_spaces(old_group_externalId)} @ Num. of records: {total_items}"
        self.report.add(report, self.report_files)

        if total_items == 0:
            self.report.add("\tNothing to modify @ End", self.report_files)
            return True

        # Iterates over all old group records
        for item in resp_json["hits"]["hits"]:
            item = item["metadata"]

            # Change group restrictions
            if old_group_externalId in item["group_restrictions"]:
                item["group_restrictions"].remove(old_group_externalId)
            for i in new_groups_externalIds:
                item["group_restrictions"].append(i)

            # Change managingOrganisationalUnit
            item = self._process_managing_organisational_unit(
                item, old_group_externalId
            )

            # When updating a record it is not possible to specify _communities field
            del item["_communities"]

            # Update record
            recid = item["recid"]
            response = self.general_functions.update_rdm_record(recid, item)

        return True

    def _process_managing_organisational_unit(self, item: object, old_group_externalId: str):
        """Description."""
        managing_org_unit_externalid_value = item["extensions"][
            "tug:managingOrganisationalUnit_externalId"
        ]
        if managing_org_unit_externalid_value == old_group_externalId:
            item["extensions"][
                "tug:managingOrganisationalUnit_name"
            ] = self.new_groups_data[0]["name"]
            item["extensions"][
                "tug:managingOrganisationalUnit_uuid"
            ] = self.new_groups_data[0]["uuid"]
            item["extensions"][
                "tug:managingOrganisationalUnit_externalId"
            ] = self.new_groups_data[0]["externalId"]
        return item

    def _rdm_split_users_from_old_to_new_group(self, old_group_id: str, old_group_externalId: str, new_groups_externalIds: list):
        """Description."""
        # Get all users in old group
        response = self.rdm_db.select_query(
            "user_id", "accounts_userrole", {"role_id": old_group_id}
        )

        report = "Old group @@ Num. of users:  "
        if not response:
            self.report.add(f"\t{report} 0", self.report_files)
            return

        self.report.add(f"\t{report} {len(response)}", self.report_files)

        for i in response:
            user_id = i[0]

            # Get user email
            user_email = self.rdm_db.select_query(
                "email", "accounts_user", {"id": user_id}
            )[0][0]

            for new_group_externalId in new_groups_externalIds:
                # Add user to new groups
                self._group_add_user(user_email, new_group_externalId, user_id)

            # Remove user from old group
            response = self._group_remove_user(user_email, old_group_externalId)

    # def _rdm_merge_modify_records(
    #     self,
    #     old_groups_externalId: list,
    #     new_group_data: dict,
    #     new_group_externalId: str,
    # ):
    # """Description."""
    #     # Get from RDM all records with old groups
    #     for old_group_externalId in old_groups_externalId:

    #         self._rdm_check_if_group_exists(old_group_externalId)

    #         # Get record metadata
    #         response = self.rdm_requests.get_metadata_by_query(old_group_externalId)

    #         resp_json = json.loads(response.content)
    #         total_items = resp_json["hits"]["total"]

    #         report = f"\tModify records @ Group: {add_spaces(old_group_externalId)} @ Num. of records: {total_items}"
    #         self.report.add(report, self.report_files)

    #         if total_items == 0:
    #             continue

    #         # Iterates over all old group records
    #         for item in resp_json["hits"]["hits"]:

    #             item = item["metadata"]

    #             # Organisational units
    #             item = self._process_organisational_units(
    #                 item, new_group_data, old_groups_externalId
    #             )

    #             # Group restrictions
    #             self._process_group_restrictions(
    #                 item, old_group_externalId, new_group_externalId
    #             )

    #             # Managing Organisational Unit
    #             if (
    #                 "managingOrganisationalUnit_externalId" in item
    #                 and item["managingOrganisationalUnit_externalId"]
    #                 == old_group_externalId
    #             ):
    #                 item["managingOrganisationalUnit_name"] = new_group_data["name"]
    #                 item["managingOrganisationalUnit_uuid"] = new_group_data["uuid"]
    #                 item["managingOrganisationalUnit_externalId"] = new_group_data[
    #                     "externalId"
    #                 ]

    #             # When updating a record it is not possible to specify _communities field
    #             del item["_communities"]

    #             # Update record
    #             response = self.general_functions.update_rdm_record(item["recid"], item)

    # def _process_organisational_units(
    #     self, item, new_group_data, old_groups_externalId
    # ):
    # """Description."""
    #     new_organisationalUnits_data = [new_group_data]

    #     if "organisationalUnits" not in item:
    #         return item

    #     for i in item["organisationalUnits"]:
    #         if (
    #             i["externalId"] in old_groups_externalId
    #             or i["externalId"] == new_group_data["externalId"]
    #         ):
    #             continue

    #         new_organisationalUnits_data.append(i)

    #     item["organisationalUnits"] = new_organisationalUnits_data
    #     return item

    # def _process_group_restrictions(
    #     self, item, old_group_externalId, new_group_externalId
    # ):
    # """Description."""
    #     if "group_restrictions" not in item:
    #         return item

    #     # Remove old group
    #     if old_group_externalId in item["group_restrictions"]:
    #         item["group_restrictions"].remove(old_group_externalId)
    #     # Add new group
    #     if new_group_externalId not in item["group_restrictions"]:
    #         item["group_restrictions"].append(new_group_externalId)
    #     return item

    # def _merge_users_from_old_to_new_group(
    #     self, old_groups_externalId: list, new_group_externalId: str
    # ):
    # """Description."""
    #     # Iterate over old groups
    #     for old_group_externalId in old_groups_externalId:

    #         # Get group id
    #         response = self.rdm_db.select_query(
    #             "id, description",
    #             "accounts_role",
    #             {"name": f"'{old_group_externalId}'"},
    #         )

    #         if not response:
    #             self.report.add(
    #                 "\nWarning @ Old group ({old_groups_externalId}) not in database @ END TASK\n"
    #             )
    #             return False

    #         old_group_id = response[0][0]
    #         old_group_name = response[0][1]

    #         # Get all users id that are in this group
    #         old_group_users = self.rdm_db.select_query(
    #             "user_id", "accounts_userrole", {"role_id": old_group_id}
    #         )

    #         if not old_group_users:
    #             old_group_users = []

    #         report = f"\tOld group @ ExtId:     {add_spaces(old_group_externalId)} @ Num. users:  {add_spaces(len(old_group_users))} @ {old_group_name}"
    #         self.report.add(report, self.report_files)

    #         for i in old_group_users:
    #             user_id = i[0]

    #             # Get user email
    #             user_email = self.rdm_db.select_query(
    #                 "email", "accounts_user", {"id": user_id}
    #             )[0][0]

    #             # - - Add user to new group - -
    #             self._group_add_user(user_email, new_group_externalId, user_id)

    #             # - - Remove user from old group - -
    #             response = self._group_remove_user(user_email, old_group_externalId)

    #         # Delete old group

    # def _get_pure_group_metadata(self, externalId: str):
    #     """Get organisationalUnit name and uuid."""
    #     # PURE REQUEST
    #     response = get_pure_metadata(
    #         "organisational-units",
    #         f"{externalId}/research-outputs",
    #         {"page": 1, "pageSize": 100},
    #     )

    #     report = f"\tNew group info @ ExtId:     {add_spaces(externalId)} @ "

    #     # Check response
    #     if response.status_code >= 300:
    #         report += "Not in pure - END TASK\n"
    #         self.report.add(report, self.report_files)
    #         self.report.add(response.content, self.report_files)
    #         return False

    #     # Load json
    #     data = json.loads(response.content)
    #     data = data["items"][0]["organisationalUnits"]

    #     for organisationalUnit in data:
    #         if organisationalUnit["externalId"] == externalId:

    #             organisationalUnit_data = {}
    #             organisationalUnit_data["externalId"] = externalId
    #             organisationalUnit_data["uuid"] = organisationalUnit["uuid"]
    #             organisationalUnit_data["name"] = organisationalUnit["names"][0][
    #                 "value"
    #             ]

    #             report += f"{organisationalUnit_data['uuid']} @ {organisationalUnit_data['name']}"
    #             self.report.add(report, self.report_files)

    #             self.new_groups_data.append(organisationalUnit_data)
    #             return organisationalUnit_data["name"]
    #     return False

    # def _rdm_check_if_group_exists(self, group_externalId: str):
    #     """Checks if the group already exists."""

    #     response = self.rdm_db.select_query(
    #         "*", "accounts_role", {"name": f"'{group_externalId}'"}
    #     )

    #     if response:
    #         report = f"\tNew group check @@ ExtId:        {add_spaces(group_externalId)} @ Already exists"
    #         self.report.add(report)
    #         return True
    #     return False

    # def rdm_create_group(self, externalId: str, group_name: str):
    #     """Description."""
    #     # Checks if the group already exists
    #     response = self._rdm_check_if_group_exists(externalId)
    #     if response:
    #         return True

    #     group_name = group_name.replace("(", "\(")
    #     group_name = group_name.replace(")", "\)")
    #     group_name = group_name.replace(" ", "_")

    #     # Run command
    #     command = f"pipenv run invenio roles create {externalId} -d {group_name}"
    #     response = os.system(command)

    #     report = f"\tNew group check @@"

    #     if response != 0:
    #         self.report.add(f"{report} Error: {response}")
    #         return False

    #     self.report.add(f"{report} Group created @ External id: {externalId}")
    #     return True

    # def _rdm_add_user_to_group(
    #     self, user_id: int, group_externalId: str, group_name: str
    # ):
    # """Description."""

    #     # Get user's rdm email
    #     user_email = self.rdm_db.select_query(
    #         "email", "accounts_user", {"id": user_id}
    #     )[0][0]

    #     # Get group id
    #     response = self.rdm_db.select_query(
    #         "id", "accounts_role", {"name": f"'{group_externalId}'"}
    #     )

    #     if not response:
    #         # If the group does not exist then creates it
    #         self.rdm_create_group(group_externalId, group_name)
    #         # Repeats the query to get the group id
    #         response = self.rdm_db.select_query(
    #             "id", "accounts_role", {"name": f"'{group_externalId}'"}
    #         )

    #     group_id = response[0][0]

    #     # Checks if match already exists
    #     response = self.rdm_db.select_query(
    #         "*", "accounts_userrole", {"user_id": user_id, "role_id": group_id}
    #     )

    #     if response:
    #         report = f"\tRDM user in group @ User id: {add_spaces(user_id)} @@ Already belongs to group {group_externalId} (id {group_id})"
    #         self.report.add(report)
    #         return True

    #     # Adds user to group
    #     command = f"pipenv run invenio roles add {user_email} {group_externalId}"
    #     response = os.system(command)
    #     if response != 0:
    #         self.report.add(f"Warning @ Creating group response: {response}")

    # def _group_add_user(self, user_email: str, new_group_externalId: str, user_id: str):
    #     """Description."""
    #     # Get group id
    #     group_id = self.rdm_db.select_query(
    #         "id", "accounts_role", {"name": f"'{new_group_externalId}'"}
    #     )[0][0]

    #     # Check if the user is already in the group
    #     response = self.rdm_db.select_query(
    #         "*", "accounts_userrole", {"user_id": user_id, "role_id": group_id}
    #     )

    #     if response:
    #         return True

    #     command = f"pipenv run invenio roles add {user_email} {new_group_externalId}"
    #     response = os.system(command)

    #     report = f"\tAdd user to group @ ExtId:     {add_spaces(new_group_externalId)} @ User id:     {add_spaces(user_id)}"
    #     if response != 0:
    #         self.report.add(f"{report} @ Error: {response}", self.report_files)
    #         return False

    #     self.report.add(f"{report} @ Success", self.report_files)
    #     return True

    # def _group_remove_user(self, user_email: str, group_name: str):
    #     """Description."""
    #     # Get user id
    #     user_id = self.rdm_db.select_query(
    #         "id", "accounts_user", {"email": f"'{user_email}'"}
    #     )[0][0]

    #     # Get group id
    #     group_id = self.rdm_db.select_query(
    #         "id", "accounts_role", {"name": f"'{group_name}'"}
    #     )[0][0]

    #     # Check if the user is already in the group
    #     response = self.rdm_db.select_query(
    #         "*", "accounts_userrole", {"user_id": user_id, "role_id": group_id}
    #     )

    #     report = f"Remove user fromGroup @ ExtId:     {add_spaces(group_name)} @ User id:     {add_spaces(user_id)}"

    #     if not response:
    #         self.report.add(
    #             f"\t{report} @ Not in group (already removed)", self.report_files
    #         )
    #         return True

    #     # Remove user from old group
    #     command = f"pipenv run invenio roles remove {user_email} {group_name}"
    #     response = os.system(command)

    #     if response != 0:
    #         self.report.add(f"\t{report} @ Error: {response}", self.report_files)
    #         return False

    #     self.report.add(f"\t{report} @ Success", self.report_files)
    #     return True
