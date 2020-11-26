# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module to test the functionalities of the Addon."""

import json
import os

from invenio_records_resources.services.records.results import RecordItem

from ....setup import dirpath
from ...reports import Reports
from ..record_manager import RecordManager
from ..requests_rdm import Requests


class Testing:
    """Class to test the functionalities of the Addon."""

    def __init__(self):
        """Constructor of class Testing."""
        self.report = Reports()
        self.rdm_requests = Requests()

    def run_tests(self) -> None:
        """Runs the tests."""
        # Sets logging variables (FIXME: implement proper logging)
        self.report.add_template(["console"], ["general", "title"], ["TESTING"])
        # Record CRUD Test
        self._run_record_crud_test()
        # Users (FIXME: implement proper user tests)
        # self._rdm_user_test()

    def _run_record_crud_test(self) -> None:
        """CRUD Test for Records implementing invenio's internal API."""
        data = json.loads(
            open(f"{dirpath}/source/rdm/testing/example_data.json", "r").read()
        )
        updated_data = json.loads(
            open(f"{dirpath}/source/rdm/testing/example_data_update.json", "r").read()
        )

        record = self._run_record_create_test(data)
        updated_record = self._run_record_update_test(record.id, updated_data)
        self._run_newest_record_test(updated_record)
        self._run_record_delete_test(updated_record)

    def _run_record_create_test(self, data: dict) -> RecordItem:
        """Tests record creation from JSON data."""
        record = RecordManager.instance().create_record(data=data)
        if record is None:
            raise RuntimeError("Couldn't create record: Test failed.")
        return record

    def _run_record_update_test(self, recid: str, updated_data: dict) -> RecordItem:
        """Tests record update from JSON data."""
        updated_record = RecordManager.instance().update_record(recid, updated_data)
        if updated_record is None:
            raise RuntimeError("Couldn't update record: Test failed.")
        return updated_record

    def _run_newest_record_test(self, record: RecordItem) -> None:
        """Tests whether the given record is the newest."""
        if not RecordManager.instance().is_newest_record(record=record):
            raise RuntimeError("Record is not the newest record: Test failed.")

    def _run_record_delete_test(self, record: RecordItem) -> None:
        """Tests record deletion."""
        RecordManager.instance().delete_record(record.id)

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
