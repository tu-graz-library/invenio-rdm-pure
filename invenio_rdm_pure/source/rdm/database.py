import os

import psycopg2
import yaml
from source.reports import Reports

from setup import database_uri, dirpath, pure_rdm_user_file


class RdmDatabase:
    """ Responsible for database connection and querying. """

    def __init__(self):
        self.report = Reports()
        self._db_connect()

    def _db_connect(self):
        """ Establis a connection to RDM database """

        host = open(database_uri["db_host"], "r").readline()
        name = open(database_uri["db_name"], "r").readline()
        user = open(database_uri["db_user"], "r").readline()
        password = open(database_uri["db_password"], "r").readline()

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
        """ Makes a select query to the database """
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
        """ Gets the userId of the Pure admin user """
        email = open(pure_rdm_user_file, "r").read()
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
