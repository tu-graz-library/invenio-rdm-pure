# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Synchronizer module to facilitate record synchronization between Invenio and Pure."""

import datetime
import os
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from os.path import dirname, isabs, isfile, join
from pathlib import Path
from typing import List

from flask import current_app
from flask_principal import Identity
from invenio_access.permissions import any_user
from invenio_records_marc21.services import Marc21RecordService, Metadata, RecordItem

from ...pure.requests_pure import (
    download_pure_file,
    get_research_output_count,
    get_research_outputs,
)
from ...utils import get_dates_in_span
from ..converter import Converter, Marc21Record
from ..database import RdmDatabase


class Synchronizer(object):
    """Synchronizer class to facilitate record synchronization between Invenio and Pure."""

    def __init__(
        self,
        pure_api_url: str = "",
        pure_api_key: str = "",
        pure_username: str = "",
        pure_password: str = "",
    ):
        """Default Constructor of the Synchronizer class."""
        if not pure_api_url:
            pure_api_url = str(current_app.config.get("PURE_API_URL"))
        if not pure_api_key:
            pure_api_key = str(current_app.config.get("PURE_API_KEY"))
        if not pure_username:
            pure_username = str(current_app.config.get("PURE_USERNAME"))
        if not pure_password:
            pure_password = str(current_app.config.get("PURE_PASSWORD"))
        self.pure_api_url = pure_api_url
        self.pure_api_key = pure_api_key
        self.pure_username = pure_username
        self.pure_password = pure_password

        database = RdmDatabase()
        invenio_pure_user_email = str(current_app.config.get("INVENIO_PURE_USER_EMAIL"))
        invenio_pure_user_password = str(
            current_app.config.get("INVENIO_PURE_USER_PASSWORD")
        )
        self.pure_user_id = database.get_user_id(invenio_pure_user_email, invenio_pure_user_password)

    def run_initial_synchronization(self) -> None:
        """Run the initial synchronization.

        In this case the database is empty.
        """
        self.run_initial_research_output_synchronization()

    def run_initial_research_output_synchronization(
        self, granularity: int = 100
    ) -> None:
        """Run initial synchronization for all research outputs."""
        research_count = get_research_output_count(self.pure_api_key, self.pure_api_url)
        assert research_count != -1, "Failed to get research output count"
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            for job_counter in range(0, (research_count // granularity) + 1):
                if job_counter == (research_count // granularity):
                    executor.submit(
                        self.synchronize_research_outputs,
                        current_app._get_current_object(),
                        research_count - job_counter * granularity,
                        job_counter * granularity,
                    )
                else:
                    executor.submit(
                        self.synchronize_research_outputs,
                        current_app._get_current_object(),
                        granularity,
                        job_counter * granularity,
                    )

    def synchronize_research_outputs(self, app, size: int, offset: int) -> None:
        """Synchronize a series of research outputs.

        Pure API identifies a series by the following parameters:
        The *size* parameter defines the length of the series.
        The *offset* parameter defines the offset of the series.
        """
        while True:
            research_outputs = get_research_outputs(
                self.pure_api_key,
                self.pure_api_url,
                size,
                offset,
            )  # Fetch research outputs from Pure
            if research_outputs:
                break
            else:
                time.sleep(0.001)
        converter = Converter()
        for research_output in research_outputs:
            try:
                record_xml = converter.convert_pure_json_to_marc21_xml(research_output)
                if Marc21Record.is_valid_marc21_xml_string(record_xml):
                    # Store record with the help of marc21 module
                    with app.app_context():
                        record = self.create_record(record_xml)
                        files = self.download_record_files(research_output)
                        self.attach_files_to_record(files, record)
                        self.delete_record_files(files)
            except RuntimeError:
                traceback.print_exc()

    def create_record(self, record_xml: str) -> RecordItem:
        """Create Invenio record from Marc21XML string."""
        identity = Identity(self.pure_user_id)
        identity.provides.add(any_user)
        metadata = Metadata()
        metadata.xml = record_xml
        service = Marc21RecordService()
        draft = service.create(metadata=metadata, identity=identity)
        record = service.publish(id_=draft.id, identity=identity)
        return record

    def download_record_files(
        self, record: dict, destination_path: str = "temp"
    ) -> List:
        """Download files associated with record into path defined in destination path."""
        file_paths = []
        if not isabs(destination_path):
            destination_path = join(dirname(__file__), destination_path)
        Path(destination_path).mkdir(parents=True, exist_ok=True)
        if "electronicVersions" in record:
            for electronic_version in record["electronicVersions"]:
                if "file" in electronic_version:
                    while True:
                        file_path = download_pure_file(
                            electronic_version["file"]["fileURL"],
                            self.pure_username,
                            self.pure_password,
                            destination_path,
                            electronic_version["file"]["fileName"],
                        )
                        if file_path:
                            break
                        else:
                            time.sleep(0.001)
                    file_paths.append(file_path)
        return file_paths

    def attach_files_to_record(self, files: List[str], record_item: RecordItem) -> None:
        """Attach files to given record."""
        resolver = Resolver()
        for file in files:
            with open(file, "rb") as fp:
                # pid, record = resolver.resolve(record_item.id)
                # record.files[str(basename(file))] = fp
                pass

    def delete_record_files(self, file_paths: List[str]) -> None:
        """Delete files with given path."""
        for file_path in file_paths:
            Path.unlink(file_path)

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

    def _get_synchronization_history(
        self, path: str = "../../../data/synchronization_history.txt"
    ) -> List[str]:
        """Open the synchronization history file and return an ascending list of dates the synchronization ran on."""
        path = join(dirname(__file__), path)
        sync_history = []
        if isfile(path):
            with open(path) as fp:
                lines = fp.readlines()
                for line in lines:
                    sync_history.append(
                        datetime.datetime.strptime(date_string=line, format="%Y-%m-%d")
                    )
                sync_history = fp.readlines()
        return sync_history
