import os
import getpass
from pathlib import Path
from setup import pure_rdm_user_file, pure_rdm_password_file

dirpath = os.path.dirname(os.path.abspath(__file__))

folder_name = "data_setup"
full_path = f"{dirpath}/{folder_name}"

# data_setup parameters
import_setup = {
    "pure_api_key": "Pure API key",
    "pure_rest_api_url": "Pure API URL",
    "pure_username": "Pure username",
    "pure_password": "Pure password",
    "rdm_host_url": "RDM host URL",
    "rdm_token": "RDM token",
    "db_host": "Database host",
    "email_sender": "Pure file deletion - Sender e-mail",
    "email_sender_password": "Pure file deletion - Sender password",
    "email_receiver": "Pure file deletion - E-mail of Pure responsible",
}

# If the folder does not exist then creates it
Path(full_path).mkdir(parents=True, exist_ok=True)

print("\nSpecifying the basic setup for this module.")
print("Please fill the following fields:\n")

for file in import_setup:
    # Ask for input value
    value = input(f"{import_setup[file]}: ")
    # Create file
    open(f"{dirpath}/{folder_name}/{file_name}.txt", "w+").write(value)

# Create Pure user in RDM
# User email
email = input("RDM user creation - Insert desired Pure user e-mail: ")
open(pure_rdm_user_file, "w+").write(email)
# User password
password = getpass.getpass("RDM user creation - Password: ")
open(pure_rdm_password_file, "w+").write(password)
# Create user
os.system(f"pipenv run invenio users create {email} --password {password} --active")
# Assign admin rights
os.system("pipenv run invenio roles add {email} admin")
