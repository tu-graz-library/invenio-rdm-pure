import psycopg2
import yaml
import os
from setup import db_host, dirpath


class RdmDatabase:
    def __init__(self):
        self._db_connect()

    def _db_connect(self):
        """ Establis a connection to RDM database """
        credentials = self._get_db_credentials()

        connection = psycopg2.connect(
            f"""\
            host={db_host} \
            dbname={credentials['db']} \
            user={credentials['user']} \
            password={credentials['psw']} \
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

    def _get_db_credentials(self):
        """ Get credentials from yaml file """
        # Get base instance directory
        upper_dirpath = os.path.abspath(os.path.join(dirpath, os.pardir))
        # Read yaml file
        data = yaml.safe_load(open(f"{upper_dirpath}/docker-services.yml", "r"))

        db_data = data["services"]["db"]["environment"]
        credentials = {}

        for i in db_data:
            key = i.split("=")[0]
            value = i.split("=")[1]

            if key == "POSTGRES_USER":
                credentials["user"] = value
            elif key == "POSTGRES_PASSWORD":
                credentials["psw"] = value
            elif key == "POSTGRES_DB":
                credentials["db"] = value

        return credentials
