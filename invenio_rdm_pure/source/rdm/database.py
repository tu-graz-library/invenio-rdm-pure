# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

from flask import current_app
from flask_security.utils import hash_password
from invenio_db import db

from ..reports import Reports


class RdmDatabase:
    """Responsible for database connection and querying."""

    def __init__(self):
        """Description."""
        self.report = Reports()

    def select_query(self, fields: str, table: str, filters={}):
        """Makes a select query to the database."""
        # Creating filters string
        filters_str = ""
        if filters:
            filters_str += " WHERE"
            for key in filters:
                filters_str += f" {key} = {filters[key]} AND"
            filters_str = filters_str[:-4]
        # Query
        query = f"SELECT {fields} FROM {table}{filters_str};"

        self.cursor.execute(query)
        if self.cursor.rowcount == 0:
            return False
        return self.cursor.fetchall()

    @staticmethod
    def get_pure_user_id():
        """Gets the userId of the Pure user.

        In case the user doesn't exist yet,
        it is created with credentials defined in config.py.
        """
        datastore = current_app.extensions["security"].datastore
        if datastore is not None:
            invenio_pure_user_email = current_app.config.get("INVENIO_PURE_USER_EMAIL")
            invenio_pure_user_password = current_app.config.get(
                "INVENIO_PURE_USER_PASSWORD"
            )
            invenio_pure_user = datastore.get_user(invenio_pure_user_email)
            if not invenio_pure_user:
                invenio_pure_user = datastore.create_user(
                    email=invenio_pure_user_email,
                    password=hash_password(invenio_pure_user_password),
                    active=True,
                )
                db.session.commit()
            return invenio_pure_user.id

    def make_user_admin(self, id_or_email: str) -> None:
        """Gives the user with given id or email administrator rights."""
        return None  # FIXME: Method stub'd until auxiliary methods are implemented.
        datastore = current_app.extensions["security"].datastore
        if datastore is not None:
            invenio_pure_user = datastore.get_user(
                id_or_email
            )  # FIXME: Not implemented yet.
            admin_role = datastore.find_role("admin")  # FIXME: Not implemented yet.
            datastore.add_role_to_user(invenio_pure_user, admin_role)
