# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module containing requests for Pure."""

import json
from os.path import join
from typing import List

import requests
from flask import current_app
from requests.auth import HTTPBasicAuth


def get_research_output_count(pure_api_key: str, pure_api_url: str) -> int:
    """Get the amount of available research outputs at /research-outputs endpoint.

    Return -1 if the GET request is not OK.
    """
    headers = {
        "api-key": pure_api_key,
        "accept": "application/json",
    }
    url = pure_api_url + "research-outputs"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return int(json.loads(response.text)["count"])
    else:
        return -1


def get_research_outputs(
    pure_api_key: str, pure_api_url: str, size: int, offset: int
) -> List[dict]:
    """Get a list of research outputs.

    Pure API identifies a series by the following parameters:
    The *size* parameter defines the length of the series.
    The *offset* parameter defines the offset of the series.
    Return [] if the GET request is not OK.
    """
    headers = {
        "api-key": pure_api_key,
        "accept": "application/json",
    }
    url = pure_api_url + "research-outputs?size={}&offset={}".format(
        str(size), str(offset)
    )
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_json = json.loads(response.text)
        items = response_json["items"]
        return items
    else:
        return []


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

    return response


def download_pure_file(
    file_url: str,
    pure_username: str,
    pure_password: str,
    destination_path: str,
    file_name: str,
) -> str:
    """Download a file from Pure to given destination path with given file name.

    Return path to the downloaded file upon success, empty string upon failure.
    """
    response = requests.get(file_url, auth=HTTPBasicAuth(pure_username, pure_password))
    if response.status_code != 200:
        return ""
    path = join(destination_path, file_name)
    with open(path, "wb") as fp:
        fp.write(response.content)
    return path


def get_pure_record_metadata_by_uuid(uuid: str):
    """Method used to get from Pure record's metadata."""
    # PURE REQUEST
    response = get_pure_metadata("research-outputs", uuid)

    # Check response
    if response.status_code >= 300:
        report = f"Get Pure metadata      - {response.content}\n"
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


def get_value(item, path: list):
    """Goes through the json item to get the information of the specified path."""
    child = item
    count = 0
    # Iterates over the given path
    for i in path:
        # If the child (step in path) exists or is equal to zero
        if i in child or i == 0:
            # Counts if the iteration took place over every path element
            count += 1
            child = child[i]
        else:
            return False

    # If the full path is not available (missing field)
    if len(path) != count:
        return False

    value = str(child)

    # REPLACEMENTS
    value = value.replace("\t", " ")  # replace \t with ' '
    value = value.replace("\\", "\\\\")  # adds \ before \
    value = value.replace('"', '\\"')  # adds \ before "
    value = value.replace("\n", "")  # removes new lines
    return value
