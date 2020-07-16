# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz.
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds pure"""

from flask import Blueprint
from flask_babelex import gettext as _
from .setup import database_uri
from .source.rdm.database_uri import get_db_uri

blueprint = Blueprint(
    "invenio_rdm_pure", __name__, template_folder="templates", static_folder="static",
)


@blueprint.route("/db_uri")
def index():
    get_db_uri()
    return "db_uri"
