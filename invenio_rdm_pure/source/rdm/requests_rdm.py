# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

import json
import time
from os import makedirs, path

import requests
from flask import current_app
from requests import Response

from ...setup import push_dist_sec, temporary_files_name, wait_429
from ..reports import Reports


class Requests:
    """Description."""

    report = Reports()

    @staticmethod
    def _request_headers(parameters: list):
        """Description."""
        headers = {}
        if "content_type" in parameters:
            headers["Content-Type"] = "application/json"
        if "file" in parameters:
            headers["Content-Type"] = "application/octet-stream"
        return headers

    @staticmethod
    def _request_params():
        """Description."""
        return (("prettyprint", "1"),)

    @classmethod
    def get_metadata(cls, additional_parameters: dict, recid: str = "") -> Response:
        """Retrieves metadata from Invenio via its REST API."""
        headers = dict()
        headers["Content-Type"] = "application/json"
        params = cls._request_params()
        if not recid:
            url = str(current_app.config.get("INVENIO_PURE_RECORDS_URL"))
        else:
            rdm_record_url: str = str(current_app.config.get("INVENIO_PURE_RECORD_URL"))
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

        # Write response to file
        get_response_file = temporary_files_name["get_rdm_metadata"]
        if not path.exists(path.dirname(get_response_file)):
            makedirs(path.dirname(get_response_file))
        with open(get_response_file, "wb") as fp:
            fp.write(response.content)

        cls._check_response(response)
        return response

    def post_metadata(self, data: str):
        """Used to create a new record."""
        open(temporary_files_name["post_rdm_metadata"], "w").write(data)

        headers = self._request_headers(["content_type"])
        params = self._request_params()

        data_utf8 = data.encode("utf-8")

        rdm_records_url = current_app.config.get("INVENIO_PURE_RECORDS_URL")

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

    @classmethod
    def put_metadata(cls, recid: str, data: object) -> Response:
        """Used to update an existing record."""
        data = json.dumps(data).encode("utf-8")

        headers = cls._request_headers(["content_type"])
        params = cls._request_params()

        rdm_record_url = str(current_app.config.get("INVENIO_PURE_RECORD_URL"))
        url = rdm_record_url.format(recid)

        response = requests.put(
            url, headers=headers, params=params, data=data, verify=False
        )

        cls._check_response(response)
        return response

    def put_file(self, file_path_name: str, recid: str):
        """Description."""
        headers = self._request_headers(["file"])
        data = open(file_path_name, "rb").read()

        # Get only the file name
        file_name = file_path_name.split("/")[-1]

        rdm_record_url = current_app.config.get("INVENIO_PURE_RECORD_URL")
        url = rdm_record_url.format(recid)

        url += "/files/{file_name}"

        return requests.put(url, headers=headers, data=data, verify=False)

    def delete_metadata(self, recid: str):
        """Description."""
        headers = self._request_headers(["content_type"])
        rdm_record_url = current_app.config.get("INVENIO_PURE_RECORD_URL")
        url = rdm_record_url.format(recid)

        response = requests.delete(url, headers=headers, verify=False)

        self._check_response(response)
        return response

    @classmethod
    def _check_response(cls, response):
        """Description."""
        http_code = response.status_code
        if http_code >= 300 and http_code != 429:
            cls.report.add(str(response.content))
            return False

        # Checks if too many requests are submitted to RDM (more then 5000 / hour)
        if response.status_code == 429:
            report = f"{response.content}\nToo many RDM requests.. wait {wait_429 / 60} minutes\n"
            cls.report.add(report)
            time.sleep(wait_429)
            return False

        # RDM accepts 5000 records per hour (one record every ~ 1.4 sec.)
        time.sleep(push_dist_sec)

        return True

    def get_metadata_by_query(self, query_value: str):
        """Query RDM record metadata."""
        params = {"sort": "mostrecent", "size": 250, "page": 1, "q": f'"{query_value}"'}
        response = self.get_metadata(params)

        self._check_response(response)
        return response

    def get_metadata_by_recid(self, recid: str):
        """Having the record recid gets from RDM its metadata."""
        if len(recid) != 11:
            report = f"\nERROR - The recid must have 11 characters. Given: {recid}\n"
            self.report.add(report)
            return False

        # RDM request
        response = self.get_metadata({}, recid)

        self._check_response(response)
        return response
