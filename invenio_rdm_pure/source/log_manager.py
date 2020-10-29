import os
from datetime import date, datetime, timedelta

from source.general_functions import check_if_file_exists, current_time
from source.reports import Reports

from setup import (
    data_files_name,
    days_keep_log,
    dirpath,
    lines_successful_changes,
    reports_full_path,
)

reports = Reports()


def delete_old_log_files():
    """
    Deletes from reports/ directory all log files that exceed the
    maximum days permanence (days_keep_log)
    """

    reports.add_template(
        ["console"], ["general", "title"], ["DELETE OLD LOGS", current_time() + "\n"]
    )

    # DELETE OLD LOG FILES
    date_limit = str(date.today() - timedelta(days=days_keep_log))

    # Get file names from directory
    isfile = os.path.isfile
    join = os.path.join
    onlyfiles = [
        f for f in os.listdir(reports_full_path) if isfile(join(reports_full_path, f))
    ]

    for file_name in onlyfiles:
        file_date = file_name.split("_")[0]

        if file_date <= date_limit:
            # Delete file
            os.remove(reports_full_path + file_name)
            align_response(file_name, "Deleted")
        else:
            align_response(file_name, "Keep")

    # SHORTEN SUCCESSFUL_CHANGES.TXT
    file_path_name = data_files_name["successful_changes"]
    file_name = file_path_name.split("/")[-1]

    check_if_file_exists(file_path_name)

    # Count file lines
    file_data = open(file_path_name)
    num_lines = sum(1 for line in file_data)

    if num_lines > lines_successful_changes:

        # Remove older lines from file
        data = ""
        file_data = open(file_path_name)
        lines = file_data.read().splitlines()
        for i in range(lines_successful_changes, 0, -1):
            last_line = lines[-i]
            data += f"{last_line}\n"
        open(file_path_name, "w").close()
        open(file_path_name, "w").write(data)

        action = f"Reduced from {num_lines} to {lines_successful_changes} lines\n"
        align_response(file_name, action)
        return
    align_response(file_name, f"{num_lines} lines - ok")


def align_response(file_name, action):

    max_length = 35
    spaces = max_length - len(str(file_name))
    file_with_spaces = str(file_name) + "".ljust(spaces)
    reports.add(f"{file_with_spaces}{action}")
