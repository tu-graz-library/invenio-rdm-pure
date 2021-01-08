# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Converter Module to facilitate conversion of metadata."""
from enum import Enum

from .marc21_record import Marc21Record


class Converter(object):
    """Converter Class to facilitate conversion of metadata."""

    def __init__(self):
        """Default Constructor of the class."""
        pass

    def convert_pure_json_to_marc21_xml(self, pure_json: dict):
        """Convert record from Pure JSON format to MARC21XML."""
        record = Marc21Record()
        for attribute, value in pure_json.items():
            self.convert_attribute(attribute, value, record)
        record.print_to_xml()

    def convert_attribute(self, attribute: str, value: object, record: Marc21Record):
        """Traverse dictionary and extract necessary attributes."""
        convert_function = getattr(self, f"convert_{attribute}", lambda *args: None)
        convert_function(value, record)
        if type(value) is dict:
            for subattribute, subvalue in value.items():
                self.convert_attribute(subattribute, subvalue, record)

    def convert_abstract(self, value: str, record: Marc21Record):
        """Add the abstract to the Marc21Record."""
        pass

    def convert_additionalLinks(self, value: str, record: Marc21Record):
        """Add the abstract attribute to the Marc21Record."""
        pass

    def convert_bibliographicalNote(self, value: str, record: Marc21Record):
        """Add the bibliographicalNote attribute to the Marc21Record."""
        pass

    def convert_edition(self, value: str, record: Marc21Record):
        """Add the edition attribute to the Marc21Record."""
        pass

    def convert_electronicIsbns(self, value: str, record: Marc21Record):
        """Add the electronicIsbns attribute to the Marc21Record."""
        pass

    def convert_event(self, value: str, record: Marc21Record):
        """Add the event attribute to the Marc21Record."""
        pass

    def convert_isbns(self, value: str, record: Marc21Record):
        """Add the isbns attribute to the Marc21Record."""
        pass

    def convert_journalAssociation(self, value: str, record: Marc21Record):
        """Add the journalAssociation attribute to the Marc21Record."""
        pass

    def convert_journalNumber(self, value: str, record: Marc21Record):
        """Add the journalNumber attribute to the Marc21Record."""
        pass

    def convert_keywordGroups(self, value: str, record: Marc21Record):
        """Add the keywordGroups attribute to the Marc21Record."""
        pass

    def convert_languages(self, value: str, record: Marc21Record):
        """Add the languages attribute to the Marc21Record."""
        pass

    def convert_managingOrganisationalUnit(self, value: str, record: Marc21Record):
        """Add the managingOrganisationalUnit attribute to the Marc21Record."""
        pass

    def convert_numberOfPages(self, value: str, record: Marc21Record):
        """Add the numberOfPages attribute to the Marc21Record."""
        pass

    def convert_organisationalUnits(self, value: str, record: Marc21Record):
        """Add the organisationalUnits attribute to the Marc21Record."""
        pass

    def convert_pages(self, value: str, record: Marc21Record):
        """Add the pages attriute to the Marc21Record."""
        pass

    def convert_patentNumber(self, value: str, record: Marc21Record):
        """Add the patentNumber attribute to the Marc21Record."""
        pass

    def convert_peerReview(self, value: str, record: Marc21Record):
        """Add the peerReview attribute to the Marc21Record."""
        pass

    def convert_placeOfPublication(self, value: str, record: Marc21Record):
        """Add the placeOfPublication attribute to the Marc21Record."""
        pass

    def convert_publicationSeries(self, value: str, record: Marc21Record):
        """Add the publicationSeries attribute to the Marc21Record."""
        pass

    def convert_publicationStatuses(self, value: str, record: Marc21Record):
        """Add the publicationStatuses attribute to the Marc21Record."""
        pass

    def convert_publisher(self, value: str, record: Marc21Record):
        """Add the publisher attribute to the Marc21Record."""
        pass

    def convert_subTitle(self, value: str, record: Marc21Record):
        """Add the subTitle attribute to the Marc21Record."""
        pass

    def convert_title(self, value: str, record: Marc21Record):
        """Add the title attribute to the Marc21Record."""
        pass

    def convert_volume(self, value: str, record: Marc21Record):
        """Add the volume attribute to the Marc21Record."""
        pass
