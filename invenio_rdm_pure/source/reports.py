from datetime import date, datetime

from source.general_functions import add_spaces, check_if_directory_exists, \
    current_time

from setup import dirpath, log_files_name

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
    """
    It is the responsible for giving a feedback to the user regarding
    the steps performed during each task and the relative success.
    This information is available in the reports/ directory.
    """

    def add_template(self, files, template, arguments):
        if template == ["general", "title"]:
            arguments.append(current_time())
        report = report_templates[template[0]][template[1]].format(*arguments)
        self.add(report, files)

    def add(self, report, files=["console"]):

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
        """ Sets the spacing between columns in a report line """
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
        """ Adds to pages report log a summary of the page submission to RDM """
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
        if not global_counters["http_responses"]:
            return
        http_response_str = "Metadata HTTP responses -> "
        for key in global_counters["http_responses"]:
            http_response_str += f"{key}: {global_counters['http_responses'][key]}, "
        return http_response_str[:-2]
