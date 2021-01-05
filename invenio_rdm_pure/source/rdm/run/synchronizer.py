# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Synchronizer module to facilitate record synchronization between Invenio and Pure."""

import datetime
import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List

from flask import current_app

from ...pure.requests_pure import (
    get_pure_metadata,
    get_research_output_count,
    get_research_outputs,
)
from ...utils import get_dates_in_span


class Synchronizer(object):
    """Synchronizer class to facilitate record synchronization between Invenio and Pure."""

    def __init__(self):
        """Default Constructor of the class Synchronizer."""

    def run_initial_synchronization(self) -> None:
        """Run the initial synchronization.

        In this case the database is empty.
        """
        # Get values necessary for the Pure REST API.
        pure_api_key = str(current_app.config.get("PURE_API_KEY"))
        pure_api_url = str(current_app.config.get("PURE_API_URL"))

        self.run_initial_research_output_synchronization(pure_api_key, pure_api_url)

    def run_initial_research_output_synchronization(
        self, pure_api_key: str, pure_api_url: str, granularity: int = 100
    ) -> None:
        """Run initial synchronization for all research outputs.

        There are ca. 65300 research output entries in Pure (15.12.2020).
        """
        research_count = get_research_output_count(pure_api_key, pure_api_url)
        assert research_count != -1, "Failed to get research output count"
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            for job_counter in range(0, research_count // granularity):
                executor.submit(
                    self.synchronize_research_outputs,
                    pure_api_key,
                    pure_api_url,
                    granularity,
                    job_counter * granularity,
                )

    def synchronize_research_outputs(
        self, pure_api_key: str, pure_api_url: str, size: int, offset: int
    ) -> None:
        """Synchronize a series of research outputs.

        Pure API identifies a series by the following parameters:
        The *size* parameter defines the length of the series.
        The *offset* parameter defines the offset of the series."""
        research_outputs = get_research_outputs(
            pure_api_key,
            pure_api_url,
            size,
            offset,
        )  # Fetch research outputs from Pure

        for research_output in research_outputs:
            pass  # TODO: Convert research outputs to marc21 record

        # TODO: Store record with the help of marc21 module
        pass

    def run_scheduled_synchronization(self) -> None:
        """Run scheduled synchronization.

        In this case the invenio datawarehouse already contains entries.
        """

    def run_user_synchronization(self, userid: str) -> None:
        """Run on-demand synchronization for a user."""

    def _get_missing_synchronization_dates(self, days_span: int = 7) -> List[str]:
        """Gets the dates, on which Pure changes have not been synchronized."""
        missing_dates = []
        sync_dates = self._get_synchronization_history()
        date_today = datetime.date.today()
        dates_to_check = get_dates_in_span(
            date_today, date_today - datetime.timedelta(days_span), -1
        )

        for date in dates_to_check:
            if date not in sync_dates:
                missing_dates.append(date)

        return missing_dates

    def _get_synchronization_history(self) -> List[str]:
        """Open the synchronization history file and return an ascending list of dates the synchronization ran on."""
        path = os.path.join(
            os.path.dirname(__file__), "../../../data/synchronization_history.txt"
        )
        sync_history = []
        if os.path.isfile(path):
            with open(path) as fp:
                lines = fp.readlines()
                for line in lines:
                    sync_history.append(
                        datetime.datetime.strptime(date_string=line, format="%Y-%m-%d")
                    )
                sync_history = fp.readlines()
        return sync_history
