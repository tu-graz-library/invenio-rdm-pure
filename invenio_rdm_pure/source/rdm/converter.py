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
        """Description."""
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
        record.print_to_xml()

    def convert_attribute(self, attribute: str, value: object, record: Marc21Record):
        """Traverse first level elements of dictionary and extract necessary attributes."""
        convert_function = getattr(self, f"convert_{attribute}", lambda *args: None)
        convert_function(value, record)

    def convert_abstract(self, value: str, record: Marc21Record):  # DONE
        """Add the abstract to the Marc21Record."""
        if isinstance(value, dict):
            abstracts = []  # To avoid multiple insertions (identical EN and DE entries)
            for language in value["text"]:
                if language["value"] not in abstracts:
                    abstracts.append(language["value"])
                    datafield = DataField(tag="520")
                    subfield = SubField(code="a", value=language["value"])
                    datafield.subfields.append(subfield)
                    record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_additionalLinks(self, value: str, record: Marc21Record):  # DONE
        """Add the additionalLinks attribute to the Marc21Record."""
        if isinstance(value, list):
            for link in value:
                if "url" in link:
                    datafield = DataField(tag="856", ind1="4", ind2="1")
                    subfield = SubField(code="u", value=link["url"])
                    datafield.subfields.append(subfield)
                    record.datafields.append(datafield)
                else:
                    raise RuntimeError("Unhandled value type")
        else:
            raise RuntimeError("Unhandled value type")

    def convert_bibliographicalNote(self, value: str, record: Marc21Record):  # DONE
        """Add the bibliographicalNote attribute to the Marc21Record."""
        if isinstance(value, dict):
            notes = []  # To avoid multiple insertions (identical EN and DE entries)
            for text in value["text"]:
                if text["value"] not in notes:
                    notes.append(text["value"])
                    datafield = DataField(tag="500")
                    subfield = SubField(code="a", value=text["value"])
                    datafield.subfields.append(subfield)
                    record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_edition(self, value: str, record: Marc21Record):  # DONE
        """Add the edition attribute to the Marc21Record."""
        if isinstance(value, str):
            datafield = DataField(tag="250")
            subfield = SubField(code="a", value=value)
            datafield.subfields.append(subfield)
            record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_electronicIsbns(self, value: str, record: Marc21Record):  # DONE
        """Add the electronicIsbns attribute to the Marc21Record."""
        if isinstance(value, list) and len(value) == 1:
            datafield = DataField(tag="020")
            subfield = SubField(code="a", value=str(value[0]).strip())
            datafield.subfields.append(subfield)
            record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_event(self, value: str, record: Marc21Record):  # DONE
        """Add the event attribute to the Marc21Record."""
        if isinstance(value, dict):
            event_names = []
            for event_name in value["name"]["text"]:
                if event_name["value"] not in event_names:
                    event_names.append(event_name["value"])
                    datafield = DataField(tag="711", ind1="2")
                    subfield = SubField(code="a", value=event_name["value"])
                    datafield.subfields.append(subfield)
                    record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_isbns(self, value: str, record: Marc21Record):  # DONE
        """Add the isbns attribute to the Marc21Record."""
        if isinstance(value, list):
            for isbn in value:
                datafield = DataField(tag="020")
                subfield = SubField(code="a", value=isbn)
                datafield.subfields.append(subfield)
                record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_journalAssociation(self, value: str, record: Marc21Record):  # DONE
        """Add the journalAssociation attribute to the Marc21Record."""
        if isinstance(value, dict):
            journal_association = value["title"]["value"]
            datafield = DataField(tag="773", ind1="0", ind2="8")
            subfield = SubField(code="t", value=journal_association)
            datafield.subfields.append(subfield)
            record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_journalNumber(self, value: str, record: Marc21Record):  # DONE
        """Add the journalNumber attribute to the Marc21Record."""
        if isinstance(value, str):
            datafield = DataField(tag="773", ind1="0", ind2="8")
            subfield = SubField(code="g", value=value)
            datafield.subfields.append(subfield)
            record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_keywordGroups(self, value: str, record: Marc21Record):  # DONE
        """Add the keywordGroups attribute to the Marc21Record."""
        if isinstance(value, list):
            for keywordgroup in value:
                if isinstance(keywordgroup["keywordContainers"], list):
                    for keywordcontainer in keywordgroup["keywordContainers"]:
                        if "freeKeywords" in keywordcontainer:
                            free_keywords = []
                            for freekeyword in keywordcontainer["freeKeywords"]:
                                if "freeKeywords" in freekeyword and isinstance(
                                    freekeyword["freeKeywords"], list
                                ):
                                    for word in freekeyword["freeKeywords"]:
                                        if word not in free_keywords:
                                            free_keywords.append(word)
                                            datafield = DataField(tag="650", ind2="4")
                                            subfield = SubField(code="g", value=word)
                                            datafield.subfields.append(subfield)
                                            record.datafields.append(datafield)
                        elif "structuredKeyword" in keywordcontainer:
                            structured_keyword = keywordcontainer["structuredKeyword"]
                            text_values = []
                            for text in structured_keyword["term"]["text"]:
                                if "value" in text and text["value"] not in text_values:
                                    text_values.append(text["value"])
                                    datafield = DataField(tag="650", ind2="4")
                                    subfield = SubField(code="a", value=text["value"])
                                    datafield.subfields.append(subfield)
                                    record.datafields.append(datafield)
                        else:
                            raise RuntimeError("Unhandled Keyword type")
                else:
                    raise RuntimeError("Unhandled value type")
        else:
            raise RuntimeError("Unhandled value type")

    def convert_language(self, value: str, record: Marc21Record):  # DONE
        """Add the language attribute to the Marc21Record."""
        if isinstance(value, dict):
            for locale in value["term"]["text"]:
                if locale["locale"] == "en_GB":
                    language = locale["value"]
                    language_iso6393 = self.languages[language]
                    datafield = DataField(tag="041")
                    subfield = SubField(code="a", value=language_iso6393)
                    datafield.subfields.append(subfield)
                    record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_managingOrganisationalUnit(
        self, value: str, record: Marc21Record
    ):  # DONE
        """Add the managingOrganisationalUnit attribute to the Marc21Record."""
        if isinstance(value, dict) and "name" in value and "text" in value["name"]:
            if isinstance(value["name"]["text"], list):
                for locale in value["name"]["text"]:
                    datafield_100 = DataField(tag="100", ind1="1")
                    subfield_100 = SubField(code="u", value=locale["value"])
                    datafield_700 = DataField(tag="700", ind1="1")
                    subfield_700 = SubField(code="u", value=locale["value"])
                    # Check if institute has already been added by attribute organisationalUnits
                    if not (
                        record.contains(datafield_100, subfield_100)
                        and record.contains(datafield_700, subfield_700)
                    ):
                        datafield_100.subfields.append(subfield_100)
                        datafield_700.subfields.append(subfield_700)
                        record.datafields.extend([datafield_100, datafield_700])
            else:
                raise RuntimeError("Unhandled value type")
        else:
            raise RuntimeError("Unhandled value type")

    def convert_numberOfPages(self, value: str, record: Marc21Record):  # DONE
        """Add the numberOfPages attribute to the Marc21Record."""
        if isinstance(value, int):
            datafield = DataField(tag="300")
            subfield = SubField(code="a", value=str(value))
            datafield.subfields.append(subfield)
            record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_organisationalUnits(self, value: str, record: Marc21Record):  # DONE
        """Add the organisationalUnits attribute to the Marc21Record."""
        if isinstance(value, list):
            for o_unit in value:
                for locale in o_unit["name"]["text"]:
                    datafield_100 = DataField(tag="100", ind1="1")
                    subfield_100 = SubField(code="u", value=locale["value"])
                    datafield_700 = DataField(tag="700", ind1="1")
                    subfield_700 = SubField(code="u", value=locale["value"])
                    # Check if institute has already been added by attribute managingOrganisationalUnit
                    if not (
                        record.contains(datafield_100, subfield_100)
                        and record.contains(datafield_700, subfield_700)
                    ):
                        datafield_100.subfields.append(subfield_100)
                        datafield_700.subfields.append(subfield_700)
                        record.datafields.extend([datafield_100, datafield_700])
        else:
            raise RuntimeError("Unhandled value type")

    def convert_pages(self, value: str, record: Marc21Record):  # DONE
        """Add the pages attriute to the Marc21Record."""
        if isinstance(value, str):
            pages = value
            datafield = DataField(tag="300")
            subfield = SubField(code="a", value=pages)
            datafield.subfields.append(subfield)
            record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_patentNumber(self, value: str, record: Marc21Record):
        """Add the patentNumber attribute to the Marc21Record."""
        if isinstance(value, str):
            pass
        datafield = DataField(tag="013")
        subfield = SubField(code="a", value=value)

        datafield.subfields.append(subfield)
        record.datafields.append(datafield)

    def convert_peerReview(self, value: str, record: Marc21Record):  # DONE
        """Add the peerReview attribute to the Marc21Record."""
        if isinstance(value, bool):
            status = "Peer Reviewed" if value else "Not Peer Reviewed"
            datafield = DataField(tag="500")
            subfield = SubField(code="a", value=status)
            datafield.subfields.append(subfield)
            record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_placeOfPublication(self, value: str, record: Marc21Record):  # DONE
        """Add the placeOfPublication attribute to the Marc21Record."""
        if isinstance(value, str):
            datafield = DataField(tag="264")
            subfield_a = SubField(code="a", value=value)
            datafield.subfields.append(subfield_a)
            record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_publicationSeries(self, value: str, record: Marc21Record):  # DONE
        """Add the publicationSeries attribute to the Marc21Record."""
        if isinstance(value, list):
            for series in value:
                datafield = DataField(tag="490", ind1="0")
                subfield_a = SubField(code="a", value=series["name"])
                datafield.subfields.append(subfield_a)
                record.datafields.append(datafield)
        else:
            subfield_v = SubField(code="v", value=value)
            raise RuntimeError("Unhandled value type")

    def convert_publicationStatuses(self, value: str, record: Marc21Record):  # DONE
        """Add the publicationStatuses attribute to the Marc21Record."""
        if isinstance(value, list):
            for entry in value:
                if "publicationDate" in entry:
                    datafield = DataField(tag="264")
                    subfield = SubField(
                        code="c", value=entry["publicationDate"]["year"]
                    )
                    datafield.subfields.append(subfield)
                    record.datafields.append(datafield)
                if "publicationStatus" in entry:
                    statuses = (
                        []
                    )  # To avoid multiple insertions (identical EN and DE entries)
                    for text in entry["publicationStatus"]["term"]["text"]:
                        if text["value"] not in statuses:
                            statuses.append(text["value"])
                            datafield = DataField(tag="250")
                            subfield = SubField(code="a", value=text["value"])
                            datafield.subfields.append(subfield)
                            record.datafields.append(datafield)
                else:
                    raise RuntimeError("Unhandled value type")
        else:
            raise RuntimeError("Unhandled value type")

    def convert_publisher(self, value: str, record: Marc21Record):  # DONE
        """Add the publisher attribute to the Marc21Record."""
        if isinstance(value, dict):
            publishers = (
                []
            )  # To avoid multiple insertions (identical EN and DE entries)
            for text in value["name"]["text"]:
                if text["value"] not in publishers:
                    publishers.append(text["value"])
                    datafield = DataField(tag="264")
                    subfield = SubField(code="b", value=text["value"])
                    datafield.subfields.append(subfield)
                    record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_relatedProjects(
        self, value: str, record: Marc21Record
    ):  # TODO: Logic TBD
        """Add the relatedProjects attribute to the Marc21Record."""
        if isinstance(value, list):
            for entry in value:
                pass  # TODO: Logic TBD
                # datafield = DataField(tag="536", value=value)
                # record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_subTitle(self, value: str, record: Marc21Record):  # DONE
        """Add the subTitle attribute to the Marc21Record."""
        if isinstance(value, list):
            for subtitle in value:
                subtitles = (
                    []
                )  # To avoid multiple insertions (identical EN and DE entries)
                for subtitle_language in subtitle["name"]["text"]:
                    if subtitle_language["value"] not in subtitles:
                        subtitles.append(subtitle_language["value"])
                        datafield = DataField(tag="245", ind1="1", ind2="0")
                        subfield = SubField(code="b", value=subtitle_language["value"])
                        datafield.subfields.append(subfield)
                        record.datafields.append(datafield)
        elif isinstance(value, dict):
            datafield = DataField(tag="245", ind1="1", ind2="0")
            subfield = SubField(code="b", value=value["value"])
            datafield.subfields.append(subfield)
            record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_title(self, value: str, record: Marc21Record):  # DONE
        """Add the title attribute to the Marc21Record."""
        if isinstance(value, dict) and "value" in value:
            title = value["value"]
            datafield = DataField(tag="245", ind1="1", ind2="0")
            subfield = SubField(code="a", value=title)
            datafield.subfields.append(subfield)
            record.datafields.append(datafield)
        else:
            raise RuntimeError("Unhandled value type")

    def convert_volume(self, value: str, record: Marc21Record):  # DONE
        """Add the volume attribute to the Marc21Record."""
        if isinstance(value, str):
            datafield_490 = DataField(tag="490", ind1="0")
            subfield_490 = SubField(code="a", value=value)
            datafield_773 = DataField(tag="773", ind1="0", ind2="8")
            subfield_773 = SubField(code="g", value=value)
            datafield_490.subfields.append(subfield_490)
            datafield_773.subfields.append(subfield_773)
            record.datafields.extend([datafield_490, datafield_773])
        else:
            raise RuntimeError("Unhandled value type")
