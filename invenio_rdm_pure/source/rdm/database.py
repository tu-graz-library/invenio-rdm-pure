# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

import os

import psycopg2
import yaml
from flask import current_app
from source.reports import Reports

from setup import database_uri, dirpath


class RdmDatabase:
    """Responsible for database connection and querying."""

    def __init__(self):
        """Description."""
        self.report = Reports()
        self._db_connect()

    def _db_connect(self):
        """Establis a connection to RDM database."""
        host = current_app.config.get("INVENIO_DATABASE_HOST")
        name = current_app.config.get("INVENIO_DATABASE_NAME")
        user = current_app.config.get("INVENIO_DATABASE_USERNAME")
        password = current_app.config.get("INVENIO_DATABASE_PASSWORD")

        connection = psycopg2.connect(
            f"""\
            host={host} \
            dbname={name} \
            user={user} \
            password={password} \
            """
        )
        self.cursor = connection.cursor()

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

    def get_pure_admin_userid(self):
        """Gets the userId of the Pure admin user."""
        email = current_app.config.get("RDM_PURE_USER_EMAIL")
        email = f"'{email}'"
        response = self.select_query("id", "accounts_user", {"email": email})
        if not response:
            report = """
            ERROR:
            Pure admin user not found.
            Make sure that the user is created and that it is stored in data_setup/rdmUser_pureEmail.txt
            """
            self.report.add(report)
            return False
        return response[0][0]
