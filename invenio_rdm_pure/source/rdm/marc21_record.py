# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""MARC21 Record Module to facilitate storage of records in MARC21 format."""

from io import StringIO
from os import linesep
from os.path import dirname, join

from lxml import etree


class ControlField(object):
    """ControlField class representing the controlfield HTML tag in MARC21 XML."""

    def __init__(self, tag: str = "", value: str = ""):
        """Default constructor of the class."""
        self.tag = tag
        self.value = value

    def to_xml_tag(self, tagsep: str = linesep, indent: int = 4) -> str:
        """Get the Marc21 Controlfield XML tag as string."""
        controlfield_tag = " " * indent
        controlfield_tag += f'<controlfield tag="{self.tag}">{self.value}'
        controlfield_tag += " " * indent
        controlfield_tag += "</controlfield>"
        controlfield_tag += tagsep
        return controlfield_tag


class DataField(object):
    """DataField class representing the datafield HTML tag in MARC21 XML."""

    def __init__(self, tag: str = "", ind1: str = " ", ind2: str = " "):
        """Default constructor of the class."""
        self.tag = tag
        self.ind1 = ind1
        self.ind2 = ind2
        self.subfields = list()

    def to_xml_tag(self, tagsep: str = linesep, indent: int = 4) -> str:
        """Get the Marc21 Datafield XML tag as string."""
        datafield_tag = " " * indent
        datafield_tag += (
            f'<datafield tag="{self.tag}" ind1="{self.ind1}" ind2="{self.ind2}">'
        )
        datafield_tag += tagsep
        for subfield in self.subfields:
            datafield_tag += subfield.to_xml_tag(tagsep, indent)
        datafield_tag += " " * indent
        datafield_tag += "</datafield>"
        datafield_tag += tagsep
        return datafield_tag


class SubField(object):
    """SubField class representing the subfield HTML tag in MARC21 XML."""

    def __init__(self, code: str = "", value: str = ""):
        """Default constructor of the class."""
        self.code = code
        self.value = value

    def to_xml_tag(self, tagsep: str = linesep, indent: int = 4) -> str:
        """Get the Marc21 Subfield XML tag as string."""
        subfield_tag = 2 * " " * indent
        subfield_tag += f'<subfield code="{self.code}">{self.value}'
        subfield_tag += f"</subfield>"
        subfield_tag += tagsep
        return subfield_tag


class Marc21Record(object):
    """MARC21 Record class to facilitate storage of records in MARC21 format."""

    LEADER_PLACEHOLDER = (
        "00000nam a2200000zca4500"  # TODO: find a way to generate proper leaders
    )

    def __init__(self, leader: str = LEADER_PLACEHOLDER):
        """Default constructor of the class."""
        self.leader = leader
        self.controlfields = list()
        self.datafields = list()

    def to_xml_string(self, tagsep: str = linesep, indent: int = 4) -> str:
        """Get a pretty-printed XML string of the record."""
        record = "<?xml version='1.0' ?>"
        record += '<record xmlns="http://www.loc.gov/MARC21/slim" xsi:schemaLocation="http://www.loc.gov/MARC21/slim schema.xsd" type="Bibliographic" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        record += tagsep
        if self.leader:
            record += self.get_leader_xml_tag(tagsep, indent)
        for controlfield in self.controlfields:
            record += controlfield.to_xml_tag(tagsep, indent)
        for datafield in self.datafields:
            record += datafield.to_xml_tag(tagsep, indent)
        record += "</record>"
        return Marc21Record.validate_marc21_xml_string(record)

    def get_leader_xml_tag(self, tagsep: str = linesep, indent: int = 4) -> str:
        """Get the leader XML tag of the Marc21Record as string."""
        leader_tag = " " * indent
        leader_tag += "<leader>"
        leader_tag += self.leader
        leader_tag += "</leader>"
        leader_tag += tagsep
        return leader_tag

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
        ind1: str = " ",
        ind2: str = " ",
        code: str = "",
        value: str = "",
    ) -> None:
        """Add value to record for given datafield and subfield."""
        datafield = DataField(tag, ind1, ind2)
        subfield = SubField(code, value)
        datafield.subfields.append(subfield)
        self.datafields.append(datafield)

    def add_unique_value(
        self,
        tag: str = "",
        ind1: str = " ",
        ind2: str = " ",
        code: str = "",
        value: str = "",
    ) -> None:
        """Add value to record if it doesn't already contain it."""
        datafield = DataField(tag, ind1, ind2)
        subfield = SubField(code, value)
        if not self.contains(datafield, subfield):
            datafield.subfields.append(subfield)
            self.datafields.append(datafield)

    @staticmethod
    def validate_marc21_xml_string(record: str) -> str:
        """Validate the record against a Marc21XML Schema."""
        with open(
            join(dirname(__file__), "MARC21slim.xsd"), "r", encoding="utf-8"
        ) as fp:
            marc21xml_schema = etree.XMLSchema(etree.parse(fp))
            marc21xml = etree.parse(StringIO(record))
            marc21xml_schema.assertValid(marc21xml)
            return record
