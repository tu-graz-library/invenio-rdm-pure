from flask import current_app
from ...setup import database_uri


def get_db_uri():
    """ Get credentials from yaml file """

    # Get application URI
    db_info = current_app.config.get("SQLALCHEMY_DATABASE_URI")

    db_info = db_info.split("//")[1].split("/")
    # name
    name = db_info[1]
    db_info = db_info[0].split("@")
    # server
    server = db_info[1]
    db_info = db_info[0].split(":")
    # password
    password = db_info[1]
    # user
    user = db_info[0]

    open(database_uri["db_host"], "w+").write(server)
    open(database_uri["db_name"], "w+").write(name)
    open(database_uri["db_user"], "w+").write(user)
    open(database_uri["db_password"], "w+").write(password)

