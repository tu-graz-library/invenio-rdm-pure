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
        controlfield_tag = [" " * indent]
        controlfield_tag.append(f'<controlfield tag="{self.tag}">{self.value}')
        controlfield_tag.append(" " * indent)
        controlfield_tag.append("</controlfield>")
        controlfield_tag.append(tagsep)
        return "".join(controlfield_tag)


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
        datafield_tag = [" " * indent]
        datafield_tag.append(
            f'<datafield tag="{self.tag}" ind1="{self.ind1}" ind2="{self.ind2}">'
        )
        datafield_tag.append(tagsep)
        for subfield in self.subfields:
            datafield_tag.append(2 * " " * indent)
            datafield_tag.append(subfield.to_xml_tag(tagsep, indent))
        datafield_tag.append(" " * indent)
        datafield_tag.append("</datafield>")
        datafield_tag.append(tagsep)
        return "".join(datafield_tag)


class SubField(object):
    """SubField class representing the subfield HTML tag in MARC21 XML."""

    def __init__(self, code: str = "", value: str = ""):
        """Default constructor of the class."""
        self.code = code
        self.value = value

    def to_xml_tag(self, tagsep: str = linesep, indent: int = 4) -> str:
        """Get the Marc21 Subfield XML tag as string."""
        subfield_tag = [2 * " " * indent]
        subfield_tag.append(f'<subfield code="{self.code}">{self.value}')
        subfield_tag.append(f"</subfield>")
        subfield_tag.append(tagsep)
        return "".join(subfield_tag)


class Marc21Record(object):
    """MARC21 Record class to facilitate storage of records in MARC21 format."""

    LEADER_PLACEHOLDER = (
        "97628dxefp 201109bOq4500"  # TODO: find a way to generate proper leaders
    )

    def __init__(self, leader: str = LEADER_PLACEHOLDER):
        """Default constructor of the class."""
        self.leader = leader
        self.controlfields = list()
        self.datafields = list()

    def to_xml_string(self, tagsep: str = linesep, indent: int = 4) -> str:
        """Get a pretty-printed XML string of the record."""
        record = ["<?xml version='1.0' ?>"]
        record.append(
            '<record xmlns="http://www.loc.gov/MARC21/slim" xsi:schemaLocation="http://www.loc.gov/MARC21/slim schema.xsd" type="Bibliographic" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        )
        record.append(tagsep)
        if self.leader:
            record.append(self.getLeaderXmlTag(self.leader))
        for controlfield in self.controlfields:
            record.append(controlfield.to_xml_tag(tagsep, indent))
        for datafield in self.datafields:
            record.append(datafield.to_xml_tag(tagsep, indent))
        record.append("</record>")
        return Marc21Record.validateMarc21Xml("".join(record))

    @staticmethod
    def validateMarc21Xml(record: str) -> str:
        """Validate the record against a Marc21XML Schema."""
        with open(
            join(dirname(__file__), "MARC21slim.xsd"), "r", encoding="utf-8"
        ) as fp:
            marc21xml_schema = etree.XMLSchema(etree.parse(fp))
            marc21xml = etree.parse(StringIO(record))
            marc21xml_schema.assertValid(marc21xml)
            return record

    @staticmethod
    def getLeaderXmlTag(leader: str, tagsep: str = linesep) -> str:
        """Get the leader XML tag of the Marc21Record as string."""
        leader_tag = ["<leader>"]
        leader_tag.append(leader)
        leader_tag.append("</leader>")
        leader_tag.append(tagsep)
        return "".join(leader_tag)

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
