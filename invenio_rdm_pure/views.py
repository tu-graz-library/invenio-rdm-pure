# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz.
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds pure."""

from os.path import abspath, dirname, isfile, join

from flask import Blueprint
from flask_babelex import gettext as _

from .source.pure.import_records import create_pure_import_file

blueprint = Blueprint(
    "invenio_rdm_pure",
    __name__,
    template_folder="templates",
    static_folder="static",
)


@blueprint.route("/pure_import_xml")
def pure_import():
    """Render pure_import_xml view."""
    # Check if the XML file does not exist
    pure_import_file = join(dirname(abspath(__file__)), "data", pure_import.xml)
    if not isfile(pure_import_file):
        # Run pure_import task to create the XML file
        create_pure_import_file(pure_import_file)
    return open(pure_import_file, "r").read()
