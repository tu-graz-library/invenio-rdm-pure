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
from requests.auth import HTTPBasicAuth

from ...setup import temporary_files_name
from ..reports import Reports

reports = Reports()


def get_pure_metadata(endpoint, identifier="", parameters={}, review=True):
    """Description."""
    pure_api_key = current_app.config.get("PURE_API_KEY")
    headers = {
        "api-key": pure_api_key,
        "Accept": "application/json",
    }
    pure_rest_api_url = current_app.config.get("PURE_API_URL")
    url = f"{pure_rest_api_url}{endpoint}/"

    # Identifies a person, research_output or date
    if len(identifier) > 0:
        url += f"{identifier}/"

    # Add parameters to url
    if len(parameters) > 0:
        url = url[:-1]  # Removes the last character
        url += "?"
        for key in parameters:
            url += f"{key}={parameters[key]}&"

    # Removes the last character
    url = url[:-1]

    # Sending request
    response = requests.get(url, headers=headers)

    if response.status_code >= 300 and review:
        reports.add(response.content)

    # Add response content to pure_get_uuid_metadata.json
    open(temporary_files_name["get_pure_metadata"], "wb").write(response.content)

    return response


def get_pure_file(file_url: str, file_name: str):
    """Description."""
    # Get request to Pure
    pure_username = current_app.config.get("PURE_USERNAME")
    pure_password = current_app.config.get("PURE_PASSWORD")
    response = requests.get(file_url, auth=HTTPBasicAuth(pure_username, pure_password))

    if response.status_code >= 300:
        reports.add(f"Error getting the file {file_url} from Pure")
        return False

    # Save file
    base_path = temporary_files_name["base_path"]
    open(f"{base_path}/{file_name}", "wb").write(response.content)

    return response


def get_pure_record_metadata_by_uuid(uuid: str):
    """Method used to get from Pure record's metadata."""
    # PURE REQUEST
    response = get_pure_metadata("research-outputs", uuid)

    report = f"\tPure get metadata     - {response}"
    if response.status_code == 404:
        report += f" - Metadata not found in Pure for record {uuid}"
    elif response.status_code >= 300:
        report += f" - Error: {response.content}"
    else:
        report += f"                       - {uuid}"
    reports.add(report)

    # Check response
    if response.status_code >= 300:
        report = f"Get Pure metadata      - {response.content}\n"
        reports.add(report["console", "records"])
        return False

    return json.loads(response.content)


def get_next_page(resp_json):
    """Description."""
    if "navigationLinks" in resp_json:
        if "next" in resp_json["navigationLinks"][0]["ref"]:
            return resp_json["navigationLinks"][0]["href"]
        else:
            if len(resp_json["navigationLinks"]) == 2:
                if "next" in resp_json["navigationLinks"][1]["ref"]:
                    return resp_json["navigationLinks"][1]["href"]
    return False
