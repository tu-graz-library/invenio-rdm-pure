# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

import json
import os
from xml.dom import minidom
from xml.etree import ElementTree as ET

from ...setup import dirpath, pure_import_file, pure_import_path
from ..rdm.requests_rdm import Requests
from ..utils import add_spaces, check_if_directory_exists, current_date, get_value


class ImportRecords:
    """Description."""

    def __init__(self):
        """Description."""
        self.rdm_requests = Requests()

    def run_import(self):
        """Description."""
        page = 1
        self.next_page = True
        xml = self._create_xml()

        # Get RDM records by page
        while self.next_page:
            data = self._get_rdm_records_metadata(page)
            if not data:
                # if self._check_if_file_exists(pure_import_file):
                #     self.report.add("\nTask correctly finished\n")
                #     pass
                # else:
                #     self.report.add("\nTask ended - No xml file created\n")
                #     pass
                return
            self._process_data(data, xml)
            page += 1
        self._parse_xml()

    def _delete_old_xml(self):
        """Description."""
        # Check if file exists
        if self._check_if_file_exists(pure_import_file):
            # Delete old file
            os.remove(pure_import_file)

    def _check_if_file_exists(self, file_name):
        """Description."""
        return os.path.isfile(file_name)

    def _check_uuid(self, item):
        """If a uuid is specified in the RDM record means that it was importedfrom Pure.

        In this case, the record will be ignored.
        """
        if "uuid" in item:
            return False
        return True

    def _check_date(self, item):
        """Checks if the record was created today."""
        if item["created"] > current_date():
            return True
        else:
            date = item["created"].split("T")[0]
            return False

    def _create_xml(self):
        """Creates the xml file that will be imported in pure."""
        name_space = {
            "dataset": "v1.dataset.pure.atira.dk",
            "commons": "v3.commons.pure.atira.dk",
        }

        ET.register_namespace("v1", name_space["dataset"])
        ET.register_namespace("v3", name_space["commons"])

        # Build a tree structure
        self.root = ET.Element("{%s}datasets" % name_space["dataset"])
        return name_space

    def _process_data(self, data, xml):
        """Creates the xml file that will be imported in pure."""
        count = 0

        for item in data:

            count += 1
            self.full_item = item
            item_metadata = item["metadata"]

            # Checks if the record was created today
            if not self._check_date(item):
                self.next_page = False
                return

            # If the rdm record has a uuid means that it was imported from pure - REVIEW
            if not self._check_uuid(item_metadata):
                continue

            # Adds fields to the created xml element
            self._populate_xml(item_metadata, xml)

    def _populate_xml(self, item, xml):
        """Description."""
        # Dataset element
        body = ET.SubElement(self.root, "{%s}dataset" % xml["dataset"])
        body.set("type", "dataset")

        # Title                     (mandatory field)
        value = get_value(item, ["titles", 0, "title"])
        if not value:
            return False
        self._sub_element(body, xml["dataset"], "title").text = value

        # Managing organisation     (mandatory field)
        organisational_unit = self._sub_element(
            body, xml["dataset"], "managingOrganisation"
        )
        self._add_attribute(
            item,
            organisational_unit,
            "lookupId",
            ["managingOrganisationalUnit_externalId"],
        )

        # Persons                   (mandatory field)
        self._add_persons(body, xml, item)

        # Available date            (mandatory field)
        date = self._sub_element(body, xml["dataset"], "availableDate")
        sub_date = self._sub_element(date, xml["commons"], "year")
        sub_date.text = get_value(item, ["publication_date"])

        # Publisher                 (mandatory field)
        self._add_publisher(body, xml, item)

        # Description
        value = get_value(item, ["abstract"])
        value = "test description"
        if value:
            descriptions = self._sub_element(body, xml["dataset"], "descriptions")
            description = self._sub_element(descriptions, xml["dataset"], "description")
            description.set("type", "datasetdescription")
            description.text = value

        # Links
        self._add_links(body, xml)

        # Organisations
        self._add_organisations(body, xml, item)

    def _add_publisher(self, body, name_space, item):
        """Description."""
        publisher_name = get_value(item, ["publisherName"])
        publisher_uuid = get_value(item, ["publisherUuid"])
        publisher_type = get_value(item, ["publisherType"])

        if not publisher_uuid:
            return
        if not publisher_name:
            publisher_name = ""
        if not publisher_type:
            publisher_type = ""

        publisher = self._sub_element(body, name_space["dataset"], "publisher")
        publisher.set("lookupId", publisher_uuid)
        self._sub_element(
            publisher, name_space["dataset"], "name"
        ).text = publisher_name
        self._sub_element(
            publisher, name_space["dataset"], "type"
        ).text = publisher_type

    def _add_organisations(self, body, name_space, item):
        """Description."""
        if "organisationalUnits" not in item:
            return False
        organisations = self._sub_element(body, name_space["dataset"], "organisations")

        for unit_data in item["organisationalUnits"]:

            # Pure dataset documentation:
            # Can be both an internal and external organisation, use origin to enforce either internal or external.
            # If the organisation is an internal organisation in Pure, then the lookupId attribute must be used.
            # If the organisation is an external organisation and id is given, the matching will be done on the id,
            # if not found mathching will be done on name, if still not found then an external
            # organisation with the specified id and organisation will be created.
            organisation = self._sub_element(
                organisations, name_space["dataset"], "organisation"
            )
            self._add_attribute(unit_data, organisation, "lookupId", ["externalId"])
            name = self._sub_element(organisation, name_space["dataset"], "name")
            name.text = get_value(unit_data, ["name"])

    def _add_persons(self, body, name_space, item):
        """Description."""
        persons = self._sub_element(body, name_space["dataset"], "persons")

        for person_data in item["creators"]:
            person = self._sub_element(persons, name_space["dataset"], "person")
            person.set("contactPerson", "true")
            self._add_attribute(person_data, person, "id", ["identifiers", "uuid"])
            # External id
            person_id = self._sub_element(person, name_space["dataset"], "person")
            self._add_attribute(
                person_data, person_id, "lookupId", ["identifiers", "externalId"]
            )
            # Role
            role = self._sub_element(person, name_space["dataset"], "role")
            role.text = get_value(person_data, ["pure_personRole"])
            # Name
            name = self._sub_element(person, name_space["dataset"], "name")
            name.text = get_value(person_data, ["name"])

    def _add_links(self, body, name_space):
        """Adds relative links for RDM files and api."""
        link_files = get_value(self.full_item, ["links", "files"])
        link_self = get_value(self.full_item, ["links", "self"])
        recid = get_value(self.full_item, ["id"])
        if link_files or link_self:
            links = self._sub_element(body, name_space["dataset"], "links")
            # Files
            if link_files:
                link = self._sub_element(links, name_space["dataset"], "link")
                link.set("id", "link_files")
                self._sub_element(link, name_space["dataset"], "url").text = link_files
                self._sub_element(
                    link, name_space["dataset"], "description"
                ).text = "Link to record files"
            # Self
            if link_self:
                link = self._sub_element(links, name_space["dataset"], "link")
                link.set("id", "link_self")
                url = self._sub_element(
                    link, name_space["dataset"], "url"
                ).text = link_self
                self._sub_element(
                    link, name_space["dataset"], "description"
                ).text = "Link to record API"

    def _parse_xml(self):
        """Description."""
        check_if_directory_exists(f"{dirpath}/{pure_import_path}")

        # Wrap it in an ElementTree instance and save as XML
        xml_str = minidom.parseString(ET.tostring(self.root)).toprettyxml(indent="   ")
        open(pure_import_file, "w").write(xml_str)

    def _sub_element(self, element, namespace: str, sub_element_name: str):
        """Adds the the xml a sub element."""
        return ET.SubElement(element, "{%s}%s" % (namespace, sub_element_name))

    def _add_attribute(
        self, item: object, sub_element, attribute: str, value_path: list
    ):
        """Gets from the rdm response a value and adds it as attribute to a given xml element."""
        value = get_value(item, value_path)
        if value:
            sub_element.set(attribute, value)

    def _add_text(self, item: object, sub_element: object, path):
        """Gets from the rdm response a value and adds it as text to a given xml element."""
        sub_element.text = get_value(item, path)

    def _get_rdm_records_metadata(self, page: int):
        """Requests to rdm records metadata by page."""
        # Size of the pages received from RDM
        page_size = 50

        params = {"sort": "mostrecent", "size": page_size, "page": page}
        response = self.rdm_requests.get_metadata(params)

        if response.status_code >= 300:
            return False
        # Load response
        json_data = json.loads(response.content)["hits"]["hits"]

        # Checks if any record is listed
        if not json_data:
            return False

        return json_data
