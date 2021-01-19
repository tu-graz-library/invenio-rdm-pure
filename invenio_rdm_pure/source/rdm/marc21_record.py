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

    def __init__(self, tag: str = "", ind1: str = "", ind2: str = ""):
        """Default constructor of the class."""
        self.tag = tag
        self.ind1 = ind1
        self.ind2 = ind2
        self.subfields = list()


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
        self.controlfields = list()
        self.datafields = list()

    def print_to_xml(self, indent: int = 4) -> str:
        """Method to pretty-print the record as XML."""
        pass

    def contains(self, ref_df: DataField, ref_sf: SubField) -> bool:
        """Return True if record contains reference datafield, which contains reference subfield."""
        for df in self.datafields:
            if (
                df.tag == ref_df.tag
                and df.ind1 == ref_df.ind1
                and df.ind2 == ref_df.ind2
            ):
                for sf in df.subfields:
                    if sf.code == ref_sf.code and sf.value == ref_sf.value:
                        return True
        return False

    def add_value(
        self,
        tag: str = "",
        ind1: str = "",
        ind2: str = "",
        code: str = "",
        value: str = "",
    ) -> None:
        """Add value to record at for given datafield and subfield."""
        datafield = DataField(tag, ind1, ind2)
        subfield = SubField(code, value)
        datafield.subfields.append(subfield)
        self.datafields.append(datafield)

    def add_unique_value(
        self,
        tag: str = "",
        ind1: str = "",
        ind2: str = "",
        code: str = "",
        value: str = "",
    ) -> None:
        """Add value to record if it doesn't already contain it."""
        datafield = DataField(tag, ind1, ind2)
        subfield = SubField(code, value)
        if not self.contains(datafield, subfield):
            datafield.subfields.append(subfield)
            self.datafields.append(datafield)
