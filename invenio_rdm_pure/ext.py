# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz.
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds pure."""

from flask_babelex import gettext as _

from . import config


class InvenioRdmPure(object):
    """invenio-rdm-pure extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["invenio-rdm-pure"] = self

    def init_config(self, app):
        """Initialize configuration."""
        # Use theme's base template if theme is installed
        if "BASE_TEMPLATE" in app.config:
            app.config.setdefault(
                "INVENIO_RDM_PURE_BASE_TEMPLATE",
                app.config["BASE_TEMPLATE"],
            )
        for k in dir(config):
            if (
                k.startswith("INVENIO_RDM_PURE_")
                or k.startswith("INVENIO_PURE")
                or k.startswith("PURE")
            ):
                app.config.setdefault(k, getattr(config, k))
        if "SQLALCHEMY_DATABASE_URI" in app.config:
            database_uri = app.config.get("SQLALCHEMY_DATABASE_URI").split("//")[1]
            database_credentials = database_uri.split("@")[0]
            database_connection = database_uri.split("@")[1]
            database_host = database_connection.split("/")[0]
            database_name = database_connection.split("/")[1]
            database_username = database_credentials.split(":")[0]
            database_password = database_credentials.split(":")[1]
            app.config.setdefault("INVENIO_DATABASE_HOST", database_host)
            app.config.setdefault("INVENIO_DATABASE_NAME", database_name)
            app.config.setdefault("INVENIO_DATABASE_USERNAME", database_username)
            app.config.setdefault("INVENIO_DATABASE_PASSWORD", database_password)
