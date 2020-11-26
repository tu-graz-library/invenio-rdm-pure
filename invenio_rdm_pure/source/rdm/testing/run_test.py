# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

import json
import os

from ....setup import dirpath
from ...reports import Reports
from ..record_manager import RecordManager
from ..requests_rdm import Requests


class Testing:
    """Module to test the functionalities of the Addon."""

    def __init__(self):
        """Description."""
        self.report = Reports()
        self.rdm_requests = Requests()

    def run_tests(self):
        """Runs the tests."""
        # Sets logging variables (FIXME: implement proper logging)
        self.report.add_template(["console"], ["general", "title"], ["TESTING"])
        # Record CRUD Test
        self._run_record_crud_test()
        # Users (FIXME: implement proper user tests)
        # self._rdm_user_test()

    def _run_record_crud_test(self):
        """CRUD Test for Records implementing invenio's internal API."""
        # CREATE record from example data
        data = json.loads(
            open(f"{dirpath}/source/rdm/testing/example_data.json", "r").read()
        )
        record = RecordManager.instance().create_record(data=data)

        # UPDATE record from example data
        updated_data = json.loads(
            open(f"{dirpath}/source/rdm/testing/example_data_update.json", "r").read()
        )
        updated_record = RecordManager.instance().update_record(record.id, updated_data)

        # Check whether record creation was successful
        if record is not None:
            if RecordManager.instance().is_newest_record(record):
                # DELETE record from example data
                RecordManager.instance().delete_record(record.id)
        else:
            raise RuntimeError("Couldn't create record: Test failed.")

    def _response_check_post(self, response, message: str):
        """Description."""
        if response.status_code >= 300:
            self.report.add(f"{message} - Error: {response.content}")
            return False
        self.report.add(f"{message} - Successful")
        return True

    def _rdm_user_test(self):
        """Description."""
        test_user = "testing9@tugraz.at"

        # Create user
        command = f"pipenv run invenio users create {test_user} --password 123456"
        response = os.system(command)
        response = self._response_check_user(response, "RDM user creation")
        if not response:
            self.report.add("(can be related to the fact that the user already exists)")

        # Activate role
        command = f"pipenv run invenio users activate {test_user}"
        response = os.system(command)
        self._response_check_user(response, "RDM activate user")

        # Assign role
        command = f"pipenv run invenio roles add {test_user} admin"
        response = os.system(command)
        self._response_check_user(response, "RDM user assign role")

        # Remove role
        command = f"pipenv run invenio roles remove {test_user} admin"
        response = os.system(command)
        self._response_check_user(response, "RDM user remove role")

        # Deactivate user
        command = f"pipenv run invenio users deactivate {test_user}"
        response = os.system(command)
        self._response_check_user(response, "RDM deactivate user")

    def _response_check_user(self, response, message: str):
        """Description."""
        if response != 0:
            self.report.add(f"{message} - Error code: {response}")
            return False
        self.report.add(f"{message} - Successful")
        return True
