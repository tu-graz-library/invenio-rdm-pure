# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Converter Module to facilitate conversion of metadata."""
import json
import os

from .marc21_record import DataField, Marc21Record, SubField


class Converter(object):
    """Converter Class to facilitate conversion of metadata."""

    def __init__(self):
        """Default Constructor of the class."""
        # Cache iso639-3 language codes to dict
        self.languages = self.initialize_languages()

    def initialize_languages(self) -> dict:
        """Initialize language cache dictionary."""
        language_cache = dict()
        path = os.path.join(os.path.dirname(__file__), "iso6393.json")
        with open(path) as file:
            languages = json.load(file)
            for language in languages:
                language_cache[language["name"]] = dict()
                for key, value in language.items():
                    if key == "iso6393":
                        language_cache[language["name"]] = value
                        break
        return language_cache

    def convert_pure_json_to_marc21_xml(self, pure_json: dict):
        """Convert record from Pure JSON format to MARC21XML."""
        record = Marc21Record()
        for attribute, value in pure_json.items():
            self.convert_attribute(attribute, value, record)
        return record.print_to_xml()

    def convert_attribute(self, attribute: str, value: object, record: Marc21Record):
        """Traverse first level elements of dictionary and extract necessary attributes."""
        convert_function = getattr(self, f"convert_{attribute}", lambda *args: None)
        convert_function(value, record)

    def convert_abstract(self, value: str, record: Marc21Record):
        """Add the abstract to the Marc21Record."""
        if isinstance(value, dict):
            abstracts = []  # To avoid multiple insertions (identical EN and DE entries)
            for language in value["text"]:
                if language["value"] not in abstracts:
                    abstracts.append(language["value"])
                    record.add_value(tag="520", code="a", value=language["value"])
        else:
            raise RuntimeError("Unhandled value type")

    def convert_additionalLinks(self, value: str, record: Marc21Record):
        """Add the additionalLinks attribute to the Marc21Record."""
        if isinstance(value, list):
            for link in value:
                if "url" in link:
                    record.add_value(
                        tag="856", ind1="4", ind2="1", code="u", value=link["url"]
                    )
                else:
                    raise RuntimeError("Unhandled value type")
        else:
            raise RuntimeError("Unhandled value type")

    def convert_bibliographicalNote(self, value: str, record: Marc21Record):
        """Add the bibliographicalNote attribute to the Marc21Record."""
        if isinstance(value, dict):
            notes = []  # To avoid multiple insertions (identical EN and DE entries)
            for text in value["text"]:
                if text["value"] not in notes:
                    notes.append(text["value"])
                    record.add_value(tag="500", code="a", value=text["value"])
        else:
            raise RuntimeError("Unhandled value type")

    def convert_edition(self, value: str, record: Marc21Record):
        """Add the edition attribute to the Marc21Record."""
        if isinstance(value, str):
            record.add_value(tag="250", code="a", value=value)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_electronicIsbns(self, value: str, record: Marc21Record):
        """Add the electronicIsbns attribute to the Marc21Record."""
        if isinstance(value, list) and len(value) > 0 and len(value) < 3:
            record.add_value(tag="020", code="a", value=str(value[0]).strip())
        else:
            raise RuntimeError("Unhandled value type")

    def convert_event(self, value: str, record: Marc21Record):
        """Add the event attribute to the Marc21Record."""
        if isinstance(value, dict):
            event_names = (
                []
            )  # To avoid multiple insertions (identical EN and DE entries)
            for event_name in value["name"]["text"]:
                if event_name["value"] not in event_names:
                    event_names.append(event_name["value"])
                    record.add_value(
                        tag="711", ind1="2", code="a", value=event_name["value"]
                    )
        else:
            raise RuntimeError("Unhandled value type")

    def convert_isbns(self, value: str, record: Marc21Record):
        """Add the isbns attribute to the Marc21Record."""
        if isinstance(value, list):
            for isbn in value:
                record.add_value(tag="020", code="a", value=isbn)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_journalAssociation(self, value: str, record: Marc21Record):
        """Add the journalAssociation attribute to the Marc21Record."""
        if isinstance(value, dict):
            journal_association = value["title"]["value"]
            record.add_value(
                tag="773", ind1="0", ind2="8", code="t", value=journal_association
            )
        else:
            raise RuntimeError("Unhandled value type")

    def convert_journalNumber(self, value: str, record: Marc21Record):
        """Add the journalNumber attribute to the Marc21Record."""
        if isinstance(value, str):
            record.add_value(tag="773", ind1="0", ind2="8", code="g", value=value)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_keywordGroups(self, value: str, record: Marc21Record):
        """Add the keywordGroups attribute to the Marc21Record."""
        if isinstance(value, list):
            for keywordgroup in value:
                for keywordcontainer in keywordgroup["keywordContainers"]:
                    if "freeKeywords" in keywordcontainer:
                        free_keywords = []
                        for freekeyword in keywordcontainer["freeKeywords"]:
                            for word in freekeyword["freeKeywords"]:
                                if word not in free_keywords:
                                    free_keywords.append(word)
                                    record.add_value(
                                        tag="650", ind2="4", code="g", value=word
                                    )
                    elif "structuredKeyword" in keywordcontainer:
                        structured_keyword = keywordcontainer["structuredKeyword"]
                        structured_keywords = []
                        for locale in structured_keyword["term"]["text"]:
                            if locale["value"] not in structured_keywords:
                                structured_keywords.append(locale["value"])
                                record.add_value(
                                    tag="650", ind2="4", code="a", value=locale["value"]
                                )
                    else:
                        raise RuntimeError("Unhandled Keyword type")
        else:
            raise RuntimeError("Unhandled value type")

    def convert_language(self, value: str, record: Marc21Record):
        """Add the language attribute to the Marc21Record."""
        if isinstance(value, dict):
            for locale in value["term"]["text"]:
                if locale["locale"] == "en_GB":
                    language = locale["value"]
                    language_iso6393 = self.languages[language]
                    record.add_value(tag="041", code="a", value=language_iso6393)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_managingOrganisationalUnit(self, value: str, record: Marc21Record):
        """Add the managingOrganisationalUnit attribute to the Marc21Record."""
        if isinstance(value, dict) and "name" in value and "text" in value["name"]:
            if isinstance(value["name"]["text"], list):
                for locale in value["name"]["text"]:
                    # Check if institute has already been added by attribute organisationalUnits
                    record.add_unique_value(
                        tag="100", ind1="1", code="u", value=locale["value"]
                    )
                    record.add_unique_value(
                        tag="700", ind1="1", code="u", value=locale["value"]
                    )
            else:
                raise RuntimeError("Unhandled value type")
        else:
            raise RuntimeError("Unhandled value type")

    def convert_numberOfPages(self, value: str, record: Marc21Record):
        """Add the numberOfPages attribute to the Marc21Record."""
        if isinstance(value, int):
            record.add_value(tag="300", code="a", value=str(value))
        else:
            raise RuntimeError("Unhandled value type")

    def convert_organisationalUnits(self, value: str, record: Marc21Record):
        """Add the organisationalUnits attribute to the Marc21Record."""
        if isinstance(value, list):
            for o_unit in value:
                for locale in o_unit["name"]["text"]:
                    # Check if institute has already been added by attribute managingOrganisationalUnit
                    record.add_unique_value(
                        tag="100", ind1="1", code="u", value=locale["value"]
                    )
                    record.add_unique_value(
                        tag="700", ind1="1", code="u", value=locale["value"]
                    )
        else:
            raise RuntimeError("Unhandled value type")

    def convert_pages(self, value: str, record: Marc21Record):
        """Add the pages attriute to the Marc21Record."""
        if isinstance(value, str):
            pages = value
            record.add_value(tag="300", code="a", value=pages)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_patentNumber(self, value: str, record: Marc21Record):
        """Add the patentNumber attribute to the Marc21Record."""
        if isinstance(value, str):
            record.add_value(tag="013", code="a", value=value)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_peerReview(self, value: str, record: Marc21Record):
        """Add the peerReview attribute to the Marc21Record."""
        if isinstance(value, bool):
            if value:
                status = "Refereed/Peer-reviewed"
                record.add_value(tag="500", code="a", value=status)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_placeOfPublication(self, value: str, record: Marc21Record):
        """Add the placeOfPublication attribute to the Marc21Record."""
        if isinstance(value, str):
            record.add_value(tag="264", code="a", value=value)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_publicationSeries(self, value: str, record: Marc21Record):
        """Add the publicationSeries attribute to the Marc21Record."""
        if isinstance(value, list):
            for series in value:
                record.add_value(tag="490", ind1="0", code="a", value=series["name"])
        else:
            raise RuntimeError("Unhandled value type")

    def convert_publicationStatuses(self, value: str, record: Marc21Record):
        """Add the publicationStatuses attribute to the Marc21Record."""
        if isinstance(value, list):
            for entry in value:
                if "publicationDate" in entry:
                    record.add_value(
                        tag="264", code="c", value=entry["publicationDate"]["year"]
                    )
                if "publicationStatus" in entry:
                    statuses = (
                        []
                    )  # To avoid multiple insertions (identical EN and DE entries)
                    for text in entry["publicationStatus"]["term"]["text"]:
                        if text["value"] not in statuses:
                            statuses.append(text["value"])
                            record.add_value(tag="250", code="a", value=text["value"])
                else:
                    raise RuntimeError("Unhandled value type")
        else:
            raise RuntimeError("Unhandled value type")

    def convert_publisher(self, value: str, record: Marc21Record):
        """Add the publisher attribute to the Marc21Record."""
        if isinstance(value, dict):
            publishers = (
                []
            )  # To avoid multiple insertions (identical EN and DE entries)
            for text in value["name"]["text"]:
                if text["value"] not in publishers:
                    publishers.append(text["value"])
                    record.add_value(tag="264", code="b", value=text["value"])
        else:
            raise RuntimeError("Unhandled value type")

    def convert_relatedProjects(self, value: str, record: Marc21Record):
        """Add the relatedProjects attribute to the Marc21Record."""
        if isinstance(value, list):
            for entry in value:
                project_names = (
                    []
                )  # To avoid multiple insertions (identical EN and DE entries)
                for locale in entry["name"]["text"]:
                    if locale["value"] not in project_names:
                        project_names.append(locale["value"])
                        record.add_value(tag="536", code="a", value=locale["value"])
        else:
            raise RuntimeError("Unhandled value type")

    def convert_subTitle(self, value: str, record: Marc21Record):
        """Add the subTitle attribute to the Marc21Record."""
        if isinstance(value, list):
            for subtitle in value:
                subtitles = (
                    []
                )  # To avoid multiple insertions (identical EN and DE entries)
                for subtitle_language in subtitle["name"]["text"]:
                    if subtitle_language["value"] not in subtitles:
                        subtitles.append(subtitle_language["value"])
                        record.add_value(
                            tag="245",
                            ind1="1",
                            ind2="0",
                            code="b",
                            value=subtitle_language["value"],
                        )
        elif isinstance(value, dict):
            record.add_value(
                tag="245", ind1="1", ind2="0", code="b", value=value["value"]
            )
        else:
            raise RuntimeError("Unhandled value type")

    def convert_title(self, value: str, record: Marc21Record):
        """Add the title attribute to the Marc21Record."""
        if isinstance(value, dict):
            title = value["value"]
            record.add_value(tag="245", ind1="1", ind2="0", code="a", value=title)
        elif isinstance(value, str):
            title = value
            record.add_value(tag="245", ind1="1", ind2="0", code="a", value=title)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_volume(self, value: str, record: Marc21Record):
        """Add the volume attribute to the Marc21Record."""
        if isinstance(value, str):
            record.add_value(tag="490", ind1="0", code="a", value=value)
            record.add_value(tag="773", ind1="0", ind2="8", code="g", value=value)
        else:
            raise RuntimeError("Unhandled value type")
