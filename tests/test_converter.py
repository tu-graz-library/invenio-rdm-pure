# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Converter tests."""
import json
from os.path import dirname, join

from invenio_rdm_pure.converter import Converter, Marc21Record


def load_json(filename):
    """Load JSON file as dict."""
    with open(join(dirname(__file__), filename), "rb") as fp:
        return json.load(fp)


def test_conversion():
    """Test conversion of a Pure record with all attributes."""
    converter = Converter()
    marc21_xml = converter.convert_pure_json_to_marc21_xml(
        load_json(join("data", "pure_record_fake.json"))
    )
    assert Marc21Record.is_valid_marc21_xml_string(marc21_xml)
