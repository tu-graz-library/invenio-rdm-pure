import os
from datetime import date, datetime
from pathlib import Path

from setup import data_files_name, pure_uuid_length


def add_spaces(value: str, max_length=5):
    # 5 is the standard maximum length of the given value
    spaces = max_length - len(str(value))
    if max_length > 5:
        return str(value) + "".ljust(spaces)
    return "".ljust(spaces) + str(value)  # ljust -> adds spaces after a string


def initialize_counters():
    """ Initialize variables that will count through the whole task the success of each process """

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
    return datetime.now().strftime("%H:%M:%S")


def current_date():
    return datetime.today().strftime("%Y-%m-%d")


def check_if_directory_exists(full_path: str):
    # If full_path does not exist creates the folder
    Path(full_path).mkdir(parents=True, exist_ok=True)


def check_if_file_exists(file_name: str):
    if not os.path.isfile(file_name):
        open(file_name, "a")


def file_read_lines(file_name: str):

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
    """ Checks if lenght of the uuid is correct """
    if len(uuid) != pure_uuid_length:
        return False
    return True


def shorten_file_name(name: str):

    max_length = 60
    if len(name) > max_length:
        return name[0:max_length] + "..."

    return name


def get_value(item, path: list):
    """ Goes through the json item to get the information of the specified path """
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
