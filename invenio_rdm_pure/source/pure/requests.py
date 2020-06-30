import json
import requests
from datetime import date, datetime
from requests.auth import HTTPBasicAuth
from setup import (
    pure_username,
    pure_password,
    temporary_files_name,
    pure_rest_api_url,
    pure_api_key,
    log_files_name,
)
from source.reports import Reports

reports = Reports()


def get_pure_metadata(endpoint, identifier="", parameters={}, review=True):
    headers = {
        "api-key": pure_api_key,
        "Accept": "application/json",
    }
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
