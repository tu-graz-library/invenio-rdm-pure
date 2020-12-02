# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

from ..general_functions_source import add_spaces
from ..reports import Reports
from .delete_record import Delete
from .requests_rdm import Requests


class GeneralFunctions:
    """Description."""

    def __init__(self):
        """Description."""
        self.rdm_requests = Requests()
        self.reports = Reports()
        self.delete = Delete()

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
