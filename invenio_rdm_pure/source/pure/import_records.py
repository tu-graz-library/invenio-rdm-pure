# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

import json
import os
from os.path import dirname
from pathlib import Path
from typing import Optional
from xml.dom import minidom
from xml.etree import ElementTree as ET

from flask import current_app

from ..rdm.requests_rdm import Requests
from ..utils import current_date, get_value

PURE_DATASET_NAMESPACE = "v1.dataset.pure.atira.dk"
PURE_COMMONS_NAMESPACE = "v3.commons.pure.atira.dk"


def create_pure_import_file(pure_import_file_path: str) -> None:
    """Description."""
    page = 1
    next_page = True
    root = create_xml()

    while next_page:
        # Get RDM records by page
        records = get_rdm_records_metadata(page)
        if not records:
            if os.path.isfile(pure_import_file_path):
                current_app.logger.info("\nTask correctly finished\n")
                pass
            else:
                current_app.logger.error("\nTask ended - No xml file created\n")
                pass
            return
        page += 1
        next_page = process_data(records, root)
    write_xml_to_file(root, pure_import_file_path)


def create_xml() -> ET.Element:
    """Creates the xml which will be imported in pure."""
    ET.register_namespace("v1", PURE_DATASET_NAMESPACE)
    ET.register_namespace("v3", PURE_COMMONS_NAMESPACE)

    root = ET.Element("{%s}datasets" % PURE_DATASET_NAMESPACE)
    return root


def process_data(records, root) -> bool:
    """Creates the xml file that will be imported in pure."""

    for record in records:
        item_metadata = record["metadata"]

        # If the rdm record has a uuid means that it was imported from pure - REVIEW
        if "uuid" in item_metadata:
            continue

        # Checks if the record was created today
        if record["created"] <= current_date():
            return False

        # Adds fields to the created xml element
        populate_xml(item_metadata, record, root)
    return True


def populate_xml(item, record, root) -> None:
    """Description."""
    # Dataset element
    body = ET.SubElement(root, "{%s}dataset" % PURE_DATASET_NAMESPACE)
    body.set("type", "dataset")

    # Title                     (mandatory field)
    value = get_value(item, ["titles", 0, "title"])
    if not value:
        return False
    sub_element(body, PURE_DATASET_NAMESPACE, "title").text = value

    # Managing organisation     (mandatory field)
    organisational_unit = sub_element(
        body, PURE_DATASET_NAMESPACE, "managingOrganisation"
    )
    add_attribute(
        item,
        organisational_unit,
        "lookupId",
        ["managingOrganisationalUnit_externalId"],
    )

    # Persons                   (mandatory field)
    add_persons(body, item)

    # Available date            (mandatory field)
    date = sub_element(body, PURE_DATASET_NAMESPACE, "availableDate")
    sub_date = sub_element(date, PURE_COMMONS_NAMESPACE, "year")
    sub_date.text = get_value(item, ["publication_date"])

    # Publisher                 (mandatory field)
    add_publisher(body, item)

    # Description
    value = get_value(item, ["abstract"])
    value = "test description"
    if value:
        descriptions = sub_element(body, PURE_DATASET_NAMESPACE, "descriptions")
        description = sub_element(descriptions, PURE_DATASET_NAMESPACE, "description")
        description.set("type", "datasetdescription")
        description.text = value

    # Links
    add_links(body, record)

    # Organisations
    add_organisations(body, item)


def add_publisher(body, item) -> None:
    """Add publisher attribute."""
    publisher_name = get_value(item, ["publisherName"])
    publisher_uuid = get_value(item, ["publisherUuid"])
    publisher_type = get_value(item, ["publisherType"])

    if not publisher_uuid:
        return

    publisher = sub_element(body, PURE_DATASET_NAMESPACE, "publisher")
    publisher.set("lookupId", publisher_uuid)
    sub_element(publisher, PURE_DATASET_NAMESPACE, "name").text = (
        publisher_name if publisher_name else ""
    )
    sub_element(publisher, PURE_DATASET_NAMESPACE, "type").text = (
        publisher_type if publisher_type else ""
    )


def add_organisations(body, item) -> None:
    """Add organisations."""
    if "organisationalUnits" not in item:
        return False
    organisations = sub_element(body, PURE_DATASET_NAMESPACE, "organisations")

    for unit_data in item["organisationalUnits"]:
        """
        Pure dataset documentation:
        Can be both an internal and external organisation, use origin to enforce either internal or external.
        If the organisation is an internal organisation in Pure, then the lookupId attribute must be used.
        If the organisation is an external organisation and id is given, the matching will be done on the id,
        if not found mathching will be done on name, if still not found then an external
        organisation with the specified id and organisation will be created.
        """
        organisation = sub_element(
            organisations, PURE_DATASET_NAMESPACE, "organisation"
        )
        add_attribute(unit_data, organisation, "lookupId", ["externalId"])
        name = sub_element(organisation, PURE_DATASET_NAMESPACE, "name")
        name.text = get_value(unit_data, ["name"])


def add_persons(body, item) -> None:
    """Add persons."""
    persons = sub_element(body, PURE_DATASET_NAMESPACE, "persons")

    for person_data in item["creators"]:
        person = sub_element(persons, PURE_DATASET_NAMESPACE, "person")
        person.set("contactPerson", "true")
        add_attribute(person_data, person, "id", ["identifiers", "uuid"])
        # External id
        person_id = sub_element(person, PURE_DATASET_NAMESPACE, "person")
        add_attribute(person_data, person_id, "lookupId", ["identifiers", "externalId"])
        # Role
        role = sub_element(person, PURE_DATASET_NAMESPACE, "role")
        role.text = get_value(person_data, ["pure_personRole"])
        # Name
        name = sub_element(person, PURE_DATASET_NAMESPACE, "name")
        name.text = get_value(person_data, ["name"])


def add_links(body, record) -> None:
    """Adds relative links for RDM files and api."""
    link_files = get_value(record, ["links", "files"])
    link_self = get_value(record, ["links", "self"])
    recid = get_value(record, ["id"])
    if link_files or link_self:
        links = sub_element(body, PURE_DATASET_NAMESPACE, "links")
        # Files
        if link_files:
            link = sub_element(links, PURE_DATASET_NAMESPACE, "link")
            link.set("id", "link_files")
            sub_element(link, PURE_DATASET_NAMESPACE, "url").text = link_files
            sub_element(
                link, PURE_DATASET_NAMESPACE, "description"
            ).text = "Link to record files"
        # Self
        if link_self:
            link = sub_element(links, PURE_DATASET_NAMESPACE, "link")
            link.set("id", "link_self")
            url = sub_element(link, PURE_DATASET_NAMESPACE, "url").text = link_self
            sub_element(
                link, PURE_DATASET_NAMESPACE, "description"
            ).text = "Link to record API"


def write_xml_to_file(root, pure_import_file_path: str) -> None:
    """Write the xml to a file."""
    pure_import_dir = dirname(pure_import_file_path)
    Path(f"{pure_import_dir}").mkdir(parents=True, exist_ok=True)

    # Wrap it in an ElementTree instance and save as XML
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent=(4 * " "))
    open(pure_import_file_path, "w").write(xml_str)


def sub_element(element, namespace: str, sub_element_name: str) -> None:
    """Adds the the xml a sub element."""
    return ET.SubElement(element, "{%s}%s" % (namespace, sub_element_name))


def add_attribute(item: object, sub_element, attribute: str, value_path: list) -> None:
    """Gets from the rdm response a value and adds it as attribute to a given xml element."""
    value = get_value(item, value_path)
    if value:
        sub_element.set(attribute, value)


def add_text(item: object, sub_element: object, path) -> None:
    """Gets from the rdm response a value and adds it as text to a given xml element."""
    sub_element.text = get_value(item, path)


def get_rdm_records_metadata(page: int, page_size=50) -> Optional(dict):
    """Requests to rdm records metadata by page."""
    """
    # TODO: replace REST with internal API
    from invenio_search import RecordsSearch, current_search_client

    class ExampleSearch(RecordsSearch):
        class Meta:
            index = "marc21records-marc21"  # Search alias of marc21 records
            fields = ("*",)
            facets = {}

    search = ExampleSearch()
    document = current_search_client.get()  # TODO: sort them most-recent-first if not standard
    """
    parameters = {"sort": "mostrecent", "size": page_size, "page": page}
    response = Requests.get_metadata(parameters)

    if response.status_code >= 300:
        return None

    # Load response
    hits = json.loads(response.content)["hits"]["hits"]
    return hits if hits else None
