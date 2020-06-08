import psycopg2
from setup          import db_host, db_name, db_user, db_password

class RdmDatabase:

    def __init__(self):
        connection = psycopg2.connect(f"""\
            host={db_host} \
            dbname={db_name} \
            user={db_user} \
            password={db_password} \
            """)
        self.cursor = connection.cursor()


    def select_query(self, fields: str, table: str, filters = {}):

        # Filters
        filters_str = ''
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
