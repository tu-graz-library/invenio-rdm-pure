import json
import time

import requests
from flask import current_app
from source.reports import Reports

from setup import push_dist_sec, temporary_files_name, wait_429


class Requests:
    def __init__(self):
        self.report = Reports()

    def _request_headers(self, parameters: list):
        headers = {}
        if "content_type" in parameters:
            headers["Content-Type"] = "application/json"
        if "file" in parameters:
            headers["Content-Type"] = "application/octet-stream"
        return headers

    def _request_params(self):
        return (("prettyprint", "1"),)

    def get_metadata(self, additional_parameters: str, recid=""):

        headers = self._request_headers(["content_type"])
        params = self._request_params()

        rdm_record_url = current_app.config.get("RDM_RECORD_URL")
        url = rdm_record_url.format(recid)

        # Add parameters to url
        if len(additional_parameters) > 0:
            url += "?"
            for key in additional_parameters:
                url += f"{key}={additional_parameters[key]}&"
            # Remove last character
            url = url[:-1]

        # Sending request
        response = requests.get(url, headers=headers, params=params, verify=False)
        open(temporary_files_name["get_rdm_metadata"], "wb").write(response.content)

        self._check_response(response)
        return response

    def post_metadata(self, data: str):
        """ Used to create a new record """

        open(temporary_files_name["post_rdm_metadata"], "w").write(data)

        headers = self._request_headers(["content_type"])
        params = self._request_params()

        data_utf8 = data.encode("utf-8")

        rdm_records_url = current_app.config.get("RDM_RECORDS_URL")

        response = requests.post(
            rdm_records_url,
            headers=headers,
            params=params,
            data=data_utf8,
            verify=False,
        )

        open(temporary_files_name["post_rdm_response"], "wb").write(response.content)

        self._check_response(response)
        return response

    def put_metadata(self, recid: str, data: object):
        """ Used to update an existing record """

        data = json.dumps(data).encode("utf-8")

        headers = self._request_headers(["content_type"])
        params = self._request_params()

        rdm_record_url = current_app.config.get("RDM_RECORD_URL")
        url = rdm_record_url.format(recid)

        response = requests.put(
            url, headers=headers, params=params, data=data, verify=False
        )

        self._check_response(response)
        return response

    def put_file(self, file_path_name: str, recid: str):

        headers = self._request_headers(["file"])
        data = open(file_path_name, "rb").read()

        # Get only the file name
        file_name = file_path_name.split("/")[-1]

        rdm_record_url = current_app.config.get("RDM_RECORD_URL")
        url = rdm_record_url.format(recid)

        url += "/files/{file_name}"

        return requests.put(url, headers=headers, data=data, verify=False)

    def delete_metadata(self, recid: str):

        headers = self._request_headers(["content_type"])
        rdm_record_url = current_app.config.get("RDM_RECORD_URL")
        url = rdm_record_url.format(recid)

        response = requests.delete(url, headers=headers, verify=False)

        self._check_response(response)
        return response

    def _check_response(self, response):
        http_code = response.status_code
        if http_code >= 300 and http_code != 429:
            self.report.add(str(response.content))
            return False

        # Checks if too many requests are submitted to RDM (more then 5000 / hour)
        if response.status_code == 429:
            report = f"{response.content}\nToo many RDM requests.. wait {wait_429 / 60} minutes\n"
            self.report.add(report)
            time.sleep(wait_429)
            return False

        # RDM accepts 5000 records per hour (one record every ~ 1.4 sec.)
        time.sleep(push_dist_sec)

        return True

    def get_metadata_by_query(self, query_value: str):
        """ Query RDM record metadata """

        params = {"sort": "mostrecent", "size": 250, "page": 1, "q": f'"{query_value}"'}
        response = self.get_metadata(params)

        self._check_response(response)
        return response

    def get_metadata_by_recid(self, recid: str):
        """ Having the record recid gets from RDM its metadata """

        if len(recid) != 11:
            report = f"\nERROR - The recid must have 11 characters. Given: {recid}\n"
            self.report.add(report)
            return False

        # RDM request
        response = self.get_metadata({}, recid)

        self._check_response(response)
        return response
