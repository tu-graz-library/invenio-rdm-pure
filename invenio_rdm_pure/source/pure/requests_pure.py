# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

import json
from datetime import date, datetime

import requests
from flask import current_app
from requests.auth import HTTPBasicAuth

from ...setup import log_files_name, temporary_files_name
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