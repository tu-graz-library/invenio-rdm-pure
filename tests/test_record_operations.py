# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record operation tests."""

import json

from invenio_records_resources.services.records.results import RecordItem

from invenio_rdm_pure.source.rdm.record_manager import RecordManager


def run_record_crud_test(app) -> None:
    """CRUD Test for Records implementing invenio's internal API."""
    data = json.loads(open(f"/data/example_data.json", "r").read())
    updated_data = json.loads(open(f"/data/example_data.json", "r").read())

    record = run_record_create_test(data)
    updated_record = run_record_update_test(record.id, updated_data)
    run_newest_record_test(updated_record)
    run_record_delete_test(updated_record)


def run_record_create_test(data: dict) -> RecordItem:
    """Tests record creation from JSON data."""
    record = RecordManager.instance().create_record(data=data)
    if record is None:
        raise RuntimeError("Couldn't create record: Test failed.")
    return record


def run_record_update_test(recid: str, updated_data: dict) -> RecordItem:
    """Tests record update from JSON data."""
    updated_record = RecordManager.instance().update_record(recid, updated_data)
    if updated_record is None:
        raise RuntimeError("Couldn't update record: Test failed.")
    return updated_record


def run_newest_record_test(record: RecordItem) -> None:
    """Tests whether the given record is the newest."""
    if not RecordManager.instance().is_newest_record(record=record):
        raise RuntimeError("Record is not the newest record: Test failed.")


def run_record_delete_test(record: RecordItem) -> None:
    """Tests record deletion."""
    RecordManager.instance().delete_record(record.id)
