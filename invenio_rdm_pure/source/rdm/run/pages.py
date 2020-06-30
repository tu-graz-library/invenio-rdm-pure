import json
from source.general_functions import initialize_counters
from source.pure.requests import get_pure_metadata
from source.rdm.add_record import RdmAddRecord
from source.reports import Reports


class RunPages:
    def __init__(self):
        self.report = Reports()
        self.rdm_add_record = RdmAddRecord()

    def get_pure_by_page(self, page_begin: int, page_end: int, page_size: int):
        """ Gets records from Pure 'research-outputs' endpoint by page and submit them to RDM. """

        for page in range(page_begin, page_end):

            self.global_counters = initialize_counters()

            # Report intro
            self.report.add_template(["console"], ["general", "title"], ["PAGES"])
            self.report.add_template(
                ["console"], ["pages", "page_and_size"], [page, page_size]
            )

            # Pure get request
            response = get_pure_metadata(
                "research-outputs", "", {"page": page, "pageSize": page_size}
            )

            # Load json response
            resp_json = json.loads(response.content)

            # Creates data to push to RDM
            for item in resp_json["items"]:
                self.report.add("")  # adds new line in the console
                self.rdm_add_record.create_invenio_data(self.global_counters, item)

            self.report_summary(page, page_size)

    def report_summary(self, pag, page_size):
        # Global counters
        self.report.summary_global_counters(["console"], self.global_counters)
        # Summary pages.log
        self.report.pages_single_line(self.global_counters, pag, page_size)
