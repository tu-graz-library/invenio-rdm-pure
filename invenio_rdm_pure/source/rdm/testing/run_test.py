# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module to test the functionalities of the Addon."""

import os

from ...reports import Reports
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
        # Users (FIXME: implement proper user tests)
        # self._rdm_user_test()

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
