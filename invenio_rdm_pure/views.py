# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz.
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds pure"""

from flask import Blueprint, render_template, current_app
from flask_babelex import gettext as _
from .setup import pure_import_file
from flask_login import current_user
from invenio_oauthclient.models import UserIdentity

blueprint = Blueprint(
    "invenio_rdm_pure", __name__, template_folder="templates", static_folder="static",
)

# Pure import
@blueprint.route("/pure_import")
def index():
    if current_user.is_authenticated:
        id = current_user.get_id()
        user_external = UserIdentity.query.filter_by(id_user=id).first()
        print(user_external.id)
        # TODO check if user is oauth

    return user_external.id
