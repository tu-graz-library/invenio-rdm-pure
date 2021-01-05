# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Converter Module to facilitate conversion of metadata."""
from enum import Enum

from .marc21_record import Marc21Record


class MetadataFormat(Enum):
    """Enum select metadata types."""
    PURE_JSON = 0
    PURE_XML = 1
    MARC21_XML = 2


class Converter(object):
    """Converter Class to facilitate conversion of metadata."""

    def __init__(self):
        """Default Constructor of the class."""
        pass

    def convert_metadata(self, output_format: MetadataFormat, input_data: dict) -> dict:
        """Converts metadata from/to given format."""
        pass
