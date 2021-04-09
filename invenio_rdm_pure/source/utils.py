# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

import smtplib
from datetime import datetime
from os.path import dirname, isabs, isfile, join
from pathlib import Path
from typing import List

from flask import current_app

from ..setup import (
    data_files_name,
    email_message,
    email_smtp_port,
    email_smtp_server,
    pure_uuid_length,
)


def load_file_as_string(path):
    """Open a file and return the content as UTF-8 encoded string."""
    if not isabs(path):
        path = join(dirname(__file__), path)

    if not isfile(path):
        return ""

    with open(path, "rb") as fp:
        input = fp.read()
        return input.decode("utf-8")


def add_spaces(value: str, max_length=5):
    """Description."""
    # 5 is the standard maximum length of the given value
    spaces = max_length - len(str(value))
    if max_length > 5:
        return str(value) + "".ljust(spaces)
    return "".ljust(spaces) + str(value)  # ljust -> adds spaces after a string


def initialize_counters():
    """Initialize variables that will count through the whole task the success of each process."""
    global_counters = {
        "metadata": {
            "success": 0,
            "error": 0,
        },
        "file": {
            "success": 0,
            "error": 0,
        },
        "delete": {
            "success": 0,
            "error": 0,
        },
        "total": 0,
        "http_responses": {},
    }
    return global_counters


def current_time():
    """Description."""
    return datetime.now().strftime("%H:%M:%S")


def current_date():
    """Description."""
    return datetime.today().strftime("%Y-%m-%d")


def get_dates_in_span(
    start: datetime.date, stop: datetime.date, step: int
) -> List[datetime.date]:
    """Returns an ascending list of dates with given step between the two endpoints of the span."""
    dates = []
    if start == stop:
        return [start]
    elif step == 0:
        return []
    elif step < 0:
        if start < stop:
            return []
        else:
            while start >= stop:
                dates.append(start)
                start += datetime.timedelta(step)
            dates.reverse()
    elif step > 0:
        if stop < start:
            return []
        else:
            while start <= stop:
                dates.append(start)
                start += datetime.timedelta(step)
    return dates


def check_if_directory_exists(full_path: str):
    """Description."""
    # If full_path does not exist creates the folder
    Path(full_path).mkdir(parents=True, exist_ok=True)


def check_if_file_exists(file_name: str):
    """Description."""
    if not isfile(file_name):
        open(file_name, "a")


def file_read_lines(file_name: str):
    """Description."""
    file_full_name = data_files_name[file_name]

    # Get file path
    index = file_full_name.rfind("/")
    full_path = file_full_name[:index]

    # It creates the directory if it does not exist
    check_if_directory_exists(full_path)

    # Checks if file exists
    check_if_file_exists(file_full_name)

    # Used to get, when available, the contributor's RDM userid
    return open(file_full_name).readlines()


def check_uuid_authenticity(uuid: str):
    """Checks if lenght of the uuid is correct."""
    if len(uuid) != pure_uuid_length:
        return False
    return True


def shorten_file_name(name: str):
    """Description."""
    max_length = 60
    if len(name) > max_length:
        return name[0:max_length] + "..."

    return name


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


def get_userid_from_list_by_externalid(self, external_id: str, file_data: list):
    """Given a user external_id, it checks if it is listed in data/user_ids_match.txt.

    If it is found it returns its relative user id.
    """
    for line in file_data:
        line = line.split("\n")[0]
        line = line.split(" ")

        # Checks if at least one of the ids match
        if external_id == line[2]:
            user_id = line[0]
            user_id_spaces = add_spaces(user_id)

            report = f"\tRDM owner list @@ User id:     {user_id_spaces} @ externalId: {external_id}"
            self.reports.add(report)

            return user_id


def send_email(
    uuid: str,
    file_name: str,
    email_sender: str,
    email_sender_password: str,
    email_receiver: str,
):
    """Send an email."""
    # EMAIL     -------- TO REVIEW ------------------
    email_smtp_server = "smtp.gmail.com"
    email_smtp_port = 587
    email_subject = "Delete Pure file"
    email_message = (
        """Subject: """
        + email_subject
        + """Please remove from pure uuid {} the file {}."""
    )
    # create SMTP session
    session = smtplib.SMTP(email_smtp_server, email_smtp_port)

    # start TLS for security
    session.starttls()

    # Authentication
    session.login(email_sender, email_sender_password)

    # sending the mail
    message = email_message.format(uuid, file_name)
    session.sendmail(email_sender, email_receiver, message)

    # terminating the session
    session.quit()
