import os
import getpass
from pathlib import Path


def _check_if_file_exists(file_name):
    if not os.path.isfile(file_name):
        open(file_name, "a")


dirpath = os.path.dirname(os.path.abspath(__file__))

full_path = f"{dirpath}/data_setup"

# data_setup parameters
import_setup = {
    "pure_api_key": "Pure API key",
    "pure_rest_api_url": "Pure API URL",
    "pure_username": "Pure username",
    "pure_password": "Pure password",
    "rdm_host_url": "RDM host URL",
    "rdm_token": "RDM token",
    "email_sender": "Pure file deletion - Sender e-mail",
    "email_sender_password": "Pure file deletion - Sender password",
    "email_receiver": "Pure file deletion - E-mail of Pure responsible",
}

# If the folder does not exist then creates it
Path(full_path).mkdir(parents=True, exist_ok=True)

print("\nSpecifying the basic setup for this module.")
print("Please fill the following fields:\n")

for file in import_setup:

    file_full_name = f"{full_path}/{file}.txt"

    # Check if file exists
    _check_if_file_exists(file_full_name)

    # Ask for input value
    value = input(f"{import_setup[file]}: ")
    # Create file
    open(file_full_name, "w+").write(value)

# User email
file_name = f"{dirpath}/data_setup/rdmUser_pureEmail.txt"
_check_if_file_exists(file_name)
email = input("RDM user creation - Insert desired Pure user e-mail: ")
open(file_name, "w+").write(email)

# User password
file_name = f"{dirpath}/data_setup/rdmUser_purePassword.txt"
_check_if_file_exists(file_name)
password = getpass.getpass("RDM user creation - Password: ")
open(file_name, "w+").write(password)

# Create user
os.system(f"pipenv run invenio users create {email} --password {password} --active")

# Assign admin rights
os.system(f"pipenv run invenio roles add {email} admin")
