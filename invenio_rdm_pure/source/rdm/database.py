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
        self.pure_user_id = None

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

    def get_user_id(self, user_email: str, user_password: str):
        """Get the userId of the user.

        In case the user doesn't exist yet,
        create it with given credentials.
        """
        if not self.pure_user_id:
            datastore = current_app.extensions["security"].datastore
            if datastore is not None:
                user = datastore.get_user(user_email)
                if not user:
                    user = datastore.create_user(
                        email=user_email,
                        password=hash_password(user_password),
                        active=True,
                    )
                    db.session.commit()
                self.pure_user_id = user.id
                return user.id
        else:
            return self.pure_user_id

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
