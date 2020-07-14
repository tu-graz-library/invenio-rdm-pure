# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz.
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds pure"""

import os
from flask import Blueprint, render_template, current_app
from flask_babelex import gettext as _
from .setup import pure_import_file, dirpath


blueprint = Blueprint(
    "invenio_rdm_pure", __name__, template_folder="templates", static_folder="static",
)

# Pure import
@blueprint.route("/pure_import")
def index():
    # Check if the XML file does not exist
    if not os.path.isfile(pure_import_file):
        # Create the file
        os.system(f"python3.6 {dirpath}/cli.py pure_import")
    return open(pure_import_file, "r").read()

