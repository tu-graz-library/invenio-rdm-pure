# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-Records-Marc21 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CLI commands for Invenio-RDM-Pure."""


import json
import random
from datetime import date, timedelta
from os.path import dirname, isfile, join

import click
from faker import Faker
from flask.cli import with_appcontext
from flask_principal import Identity
from invenio_access.permissions import any_user
from invenio_records_marc21.services import Marc21RecordService, Metadata
from invenio_records_marc21.vocabularies import Vocabularies

from .source.rdm.converter import Converter, Marc21Record
from .source.rdm.database import RdmDatabase
from .source.utils import load_file_as_string


def fake_access_right():
    """Generate fake access_right."""
    vocabulary = Vocabularies.get_vocabulary("access_right")
    _type = random.choice(list(vocabulary.data.keys()))
    return _type


def fake_feature_date(days=365):
    """Generate fake feature_date."""
    start_date = date.today()
    random_number_of_days = random.randrange(days)
    _date = start_date + timedelta(days=random_number_of_days)
    return _date.strftime("%Y-%m-%d")


def create_invenio_record(record: dict) -> None:
    """Create a record."""
    converter = Converter()
    record_marc21 = converter.convert_pure_json_to_marc21_xml(record)

    if not Marc21Record.is_valid_marc21_xml_string(record_marc21):
        click.secho("ERROR - Can't convert provided JSON to valid Marc21XML.", fg="red")
        return

    identity = Identity(RdmDatabase.get_pure_user_id())
    identity.provides.add(any_user)
    metadata = Metadata()
    metadata.xml = record_marc21
    service = Marc21RecordService()
    fake_acces = {
        "access_right": fake_access_right(),
        "embargo_date": fake_feature_date(),
    }
    draft = service.create(metadata=metadata, identity=identity, access=fake_acces)
    record = service.publish(id_=draft.id, identity=identity)
    click.secho("Record converted and stored successfully.", fg="green")


def create_demo_record() -> dict:
    """Create a demo record dict."""
    with open(join(dirname(__file__), "data/pure_record_fake.json"), "rb") as fp:
        demo_record = json.load(fp)

    faker = Faker()

    demo_record["title"]["value"] = faker.text()
    for i in range(len(demo_record["abstract"]["text"])):
        demo_record["abstract"]["text"][i]["value"] = faker.text()
    for i in range(len(demo_record["publisher"]["name"]["text"])):
        demo_record["publisher"]["name"]["text"][i]["value"] = faker.name()

    return demo_record


@click.group()
def pure():
    """Commands for InvenioRdmPure."""
    pass


@pure.command("import")
@click.argument("data", required=True)
@with_appcontext
def pure_import_json(data):
    """Import a record from given JSON file or JSON string."""
    if isfile(data):
        data = load_file_as_string(data)
    try:
        record = json.loads(data)
    except json.JSONDecodeError:
        click.secho("ERROR - Invalid JSON provided.", fg="red")
    create_invenio_record(record)


@pure.command("demo")
@click.option(
    "--number",
    "-n",
    default=10,
    show_default=True,
    type=int,
    help="Number of demo records to be converted and stored.",
)
@with_appcontext
def pure_demo(number):
    """Demonstrate conversion and storage of Pure records."""
    click.echo("Creating demo records...")

    for _ in range(number):
        demo_record = create_demo_record()
        create_invenio_record(demo_record)

    click.secho("Demo records created succesfully.", fg="green")


"""Pure synchronizer.

Usage:
    shell_interface.py get_pure_changes
    shell_interface.py get_pure_pages       [--pageStart=<page>, --pageEnd=<page>, --pageSize=<page>]
    shell_interface.py delete_old_logs
    shell_interface.py delete_by_recid
    shell_interface.py add_by_uuid
    shell_interface.py get_owner_records    [--identifier=<value>, --identifierValue=<value>]
    shell_interface.py group_split          [--oldGroup=<recid>, --newGroups=<recid>]
    shell_interface.py group_merge          [--oldGroups=<recid>, --newGroup=<recid>]
    shell_interface.py pure_import_xml
    shell_interface.py rdm_testing

Options:
    --pageStart=<page>      Initial page [default:  1].
    --pageEnd=<page>        Ending page  [default:  2].
    --pageSize=<page>       Page size    [default: 10].
    --oldGroup=<recid>      Old group externalId.
    --newGroups=<recid>     List of new groups externalIds separated by a space.
    --oldGroups=<recid>     List of old groups externalIds separated by a space.
    --newGroup=<recid>      New group externalId.
    --identifier=<value>    Run process identifying the user with externalId or orcid
    --identifierValue=<value>    User externalId or orcid
    -h --help               Show this screen.
    --version               Show version.

from docopt import docopt

from .setup import dirpath
from .shell_interface import ShellInterface, method_call
from .source.utils import check_if_directory_exists

if __name__ == "__main__":
    arguments = docopt(__doc__, version="Pure synchronizer 1.0")
    check_if_directory_exists(f"{dirpath}/data/temporary_files")
    # Create new instance
    shell_interface = ShellInterface()

    # Calls the method given in the arguments
    method_call(shell_interface, arguments)
"""
