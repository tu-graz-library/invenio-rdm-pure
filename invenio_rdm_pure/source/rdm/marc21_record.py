# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""MARC21 Record Module to facilitate storage of records in MARC21 format."""

from os import linesep


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

    def print_to_xml(self, tagsep: str = linesep, indent: int = 4) -> str:
        """Pretty-print the record as XML string."""
        record = ["<record>"]
        record.append(tagsep)
        if self.leader:
            record.append(self.getLeaderXmlTag())
        for controlfield in self.controlfields:
            record.append(self.getControlFieldXmlTag(controlfield, tagsep, indent))
        for datafield in self.datafields:
            record.append(self.getDataFieldXmlTag(datafield, tagsep, indent))
        record.append("</record>")
        return "".join(record)

    @staticmethod
    def getLeaderXmlTag(leader: str, tagsep: str = linesep) -> str:
        """Get the leader XML tag of the Marc21Record as string."""
        leader_tag = ["<leader>"]
        leader_tag.append(leader)
        leader_tag.append("</leader>")
        leader_tag.append(tagsep)
        return "".join(leader_tag)

    @staticmethod
    def getControlFieldXmlTag(
        controlfield: ControlField, tagsep: str = linesep, indent: int = 4
    ) -> str:
        """Get a controlfield XML tag of the Marc21Record as string."""
        controlfield_tag = [" " * indent]
        controlfield_tag.append(
            f'<controlfield tag="{controlfield.tag}">{controlfield.value}'
        )
        controlfield_tag.append("</controlfield>")
        controlfield_tag.append(tagsep)
        return "".join(controlfield_tag)

    @staticmethod
    def getDataFieldXmlTag(
        datafield: DataField, tagsep: str = linesep, indent: int = 4
    ) -> str:
        """Get a datafield XML tag of the Marc21Record as string."""
        datafield_tag = [" " * indent]
        datafield_tag.append(
            f'<datafield tag="{datafield.tag}" ind1="{datafield.ind1}", ind2={datafield.ind2}>'
        )
        datafield_tag.append(tagsep)
        for subfield in datafield.subfields:
            datafield_tag.append(" " * indent)
            datafield_tag.append(f'<subfield code="{subfield.code}">{subfield.value}')
            datafield_tag.append(tagsep)
        datafield_tag.append("</datafield>")
        datafield_tag.append(tagsep)
        return "".join(datafield_tag)

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
        """Add value to record for given datafield and subfield."""
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
