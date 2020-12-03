# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module responsible for logging."""

import datetime
import os
from datetime import date, timedelta

from ..setup import (
    data_files_name,
    days_keep_log,
    dirpath,
    lines_successful_changes,
    log_files_name,
    reports_full_path,
)
from .utils import (
    add_spaces,
    check_if_directory_exists,
    check_if_file_exists,
    current_time,
)

report_templates = {
    # GENERAL       ***
    "general": {
        # Intro                     Arguments -> title, current time
        "title": """
--   --   --
-- {} -- {}""",
        # Summary global counters
        "summary": """
Successful      -> metadata: {} - files: {} - delete: {}
Errors          -> metadata: {} - files: {} - delete: {}
""",
    },
    # PAGES       ***
    "pages": {
        "page_and_size": "\nPage: {} - page size: {}",
        #   --      --
        "summary_single_line": """\
{} - Page{} - Size{} - \
Metadata (ok{}, error {}) - \
File (ok{}, error{}) - \
{}""",
    },
    # CHANGES       ***
    "changes": {
        "summary": """
Pure changes:
Update:     {} - Create:     {} - Delete:    {}
Incomplete: {} - Duplicated: {} - Irrelevant:{}
"""
    },
}


class Reports:
    """It is the responsible for giving a feedback to the user regarding.

    the steps performed during each task and the relative success.
    This information is available in the reports/ directory.
    """

    def add_template(self, files, template, arguments):
        """Description."""
        if template == ["general", "title"]:
            arguments.append(current_time())
        report = report_templates[template[0]][template[1]].format(*arguments)
        self.add(report, files)

    def add(self, report, files=["console"]):
        """Description."""
        report = self._report_columns_spaces(report)
        check_if_directory_exists(f"{dirpath}/reports")
        # For each log file
        for file in files:
            # Prints in console only when saving in console file
            if file == "console":
                print(report)
            # Get file name
            file_name = log_files_name[file]
            # Adds report to file
            open(file_name, "a").write(f"{report}\n")

    def _report_columns_spaces(self, report: str):
        """Sets the spacing between columns in a report line."""
        count = 0
        result = ""

        # Split report
        report = report.split("@")

        columns_length = {
            1: 23,
            2: 18,
            3: 21,
            4: 38,
        }
        for column in report:
            count += 1

            if count < 5:
                column_length = columns_length[count]
                # Increaes column space in case of new line
                if "\n" in column:
                    column_length += 1
                # Add spaces
                result += add_spaces(column, column_length) + "-"
                continue
            result += column

        # Removes the dash from the last column
        if len(report) < 5:
            result = result[:-1]
        return result

    def summary_global_counters(self, report_files, global_counters):
        """Description."""
        arguments = []
        arguments.append(add_spaces(global_counters["metadata"]["success"]))
        arguments.append(add_spaces(global_counters["file"]["success"]))
        arguments.append(add_spaces(global_counters["delete"]["success"]))
        arguments.append(add_spaces(global_counters["metadata"]["error"]))
        arguments.append(add_spaces(global_counters["file"]["error"]))
        arguments.append(add_spaces(global_counters["delete"]["error"]))
        self.add_template(report_files, ["general", "summary"], arguments)

        if global_counters["http_responses"]:
            http_response_str = self.metadata_http_responses(global_counters)
            self.add(http_response_str, report_files)

    def pages_single_line(self, global_counters, pag, pag_size):
        """Adds to pages report log a summary of the page submission to RDM."""
        current_time = datetime.now().strftime("%H:%M:%S")
        arguments = []
        arguments.append(add_spaces(current_time))
        arguments.append(add_spaces(pag))
        arguments.append(add_spaces(pag_size))
        arguments.append(add_spaces(global_counters["metadata"]["success"]))
        arguments.append(add_spaces(global_counters["metadata"]["error"]))
        arguments.append(add_spaces(global_counters["file"]["success"]))
        arguments.append(add_spaces(global_counters["file"]["error"]))
        if global_counters["http_responses"]:
            arguments.append(self.metadata_http_responses(global_counters))

        self.add_template(["pages"], ["pages", "summary_single_line"], arguments)
        return

    def metadata_http_responses(self, global_counters):
        """Description."""
        if not global_counters["http_responses"]:
            return
        http_response_str = "Metadata HTTP responses -> "
        for key in global_counters["http_responses"]:
            http_response_str += f"{key}: {global_counters['http_responses'][key]}, "
        return http_response_str[:-2]

    def delete_old_log_files(self):
        """
        Deletes from reports/ directory all log files that exceed the.

        maximum days permanence (days_keep_log).
        """
        self.add_template(
            ["console"],
            ["general", "title"],
            ["DELETE OLD LOGS", current_time() + "\n"],
        )

        # DELETE OLD LOG FILES
        date_limit = str(date.today() - timedelta(days=days_keep_log))

        # Get file names from directory
        isfile = os.path.isfile
        join = os.path.join
        onlyfiles = [
            f
            for f in os.listdir(reports_full_path)
            if isfile(join(reports_full_path, f))
        ]

        for file_name in onlyfiles:
            file_date = file_name.split("_")[0]

            if file_date <= date_limit:
                # Delete file
                os.remove(reports_full_path + file_name)
                self.align_response(file_name, "Deleted")
            else:
                self.align_response(file_name, "Keep")

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
            self.align_response(file_name, action)
            return
        self.align_response(file_name, f"{num_lines} lines - ok")

    def align_response(self, file_name, action):
        """Description."""
        max_length = 35
        spaces = max_length - len(str(file_name))
        file_with_spaces = str(file_name) + "".ljust(spaces)
        self.add(f"{file_with_spaces}{action}")
