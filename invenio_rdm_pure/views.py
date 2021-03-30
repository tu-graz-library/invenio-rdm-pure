# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Technische Universität Graz.
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds pure."""

import os

from flask import Blueprint
from flask_babelex import gettext as _

from .setup import dirpath, pure_import_file

blueprint = Blueprint(
    "invenio_rdm_pure",
    __name__,
    template_folder="templates",
    static_folder="static",
)


@blueprint.route("/pure_import_xml")
def index1():
    """Render pure_import_xml view."""
    # Check if the XML file does not exist
    if not os.path.isfile(pure_import_file):
        # Run pure_import task to create the XML file
        os.system(f"python {dirpath}/cli.py pure_import")
    return open(pure_import_file, "r").read()
