# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""MARC21 Record Module to facilitate storage of records in MARC21 format."""


class ControlField(object):
    """ControlField class representing the controlfield HTML tag in MARC21 XML."""

    def __init__(self, tag: str = "", value: str = ""):
        """Default constructor of the class."""
        self.tag = tag
        self.value = value


class DataField(object):
    """DataField class representing the datafield HTML tag in MARC21 XML."""

    def __init__(self, tag: str = "", ind1: str = "", ind2: str = "", value: str = ""):
        """Default constructor of the class."""
        self.tag = tag
        self.ind1 = ind1
        self.ind2 = ind2
        self.subfields = [SubField]


class SubField(object):
    """SubField class representing the subfield HTML tag in MARC21 XML."""

    def __init__(self, code: str = "", value: str = ""):
        """Default constructor of the class."""
        self.code = code
        self.value = value


class Marc21Record(object):
    """MARC21 Record class to facilitate storage of records in MARC21 format."""

    def __init__(self, leader: str = ""):
        """Default constructor of the class."""
        self.leader = leader
        self.controlfields = [ControlField]
        self.datafields = [DataField]

    def print_to_xml(self, indent: int = 4) -> str:
        """Method to pretty-print the record as XML."""
        pass
