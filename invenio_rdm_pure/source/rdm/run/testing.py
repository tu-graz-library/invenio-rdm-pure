import os
import json
from setup import dirpath
from source.reports import Reports
from source.rdm.requests import Requests


class Testing:
    def __init__(self):
        self.report = Reports()
        self.rdm_requests = Requests()

    def run(self):
        # Title
        self.report.add_template(["console"], ["general", "title"], ["TESTING"])
        # Records
        self._post_get_rdm_record()
        # Users
        self._rdm_user_test()

    def _post_get_rdm_record(self):
        # RDM post metadata
        data = open(f"{dirpath}/data/testing.json", "r").read()
        response = self.rdm_requests.post_metadata(data)
        response = self._response_check_post(response, "RDM post metadata")
        if not response:
            return False

        # Delete RDM record
        params = {"sort": "mostrecent", "size": 1, "page": 1}
        response = self.rdm_requests.get_metadata(params)
        resp_json = json.loads(response.content)
        recid = resp_json["hits"]["hits"][0]["metadata"]["recid"]
        print(f"\nRecid: {recid}")
        response = self.rdm_requests.delete_metadata(recid)
        self._response_check_post(response, "RDM record delete")

    def _response_check_post(self, response, message: str):
        if response.status_code >= 300:
            self.report.add(f"{message} - Error: {response.content}")
            return False
        self.report.add(f"{message} - Successful")
        return True

    def _rdm_user_test(self):

        test_user = "testing@tugraz.at"

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
        self._response_check_user(response, "RDM user assign role")

        # Deactivate user
        command = f"pipenv run invenio users deactivate {test_user}"
        response = os.system(command)
        self._response_check_user(response, "RDM activate user")

    def _response_check_user(self, response, message: str):
        if response != 0:
            self.report.add(f"{message} - Error code: {response}")
            return False
        self.report.add(f"{message} - Successful")
        return True
