import os
from pathlib import Path

dirpath = os.path.dirname(os.path.abspath(__file__))

folder_name = "data_setup"
full_path = f"{dirpath}/{folder_name}"

# data_setup parameters
import_setup = {
    # "pure_api_key": "Pure API key",
    # "pure_password": "Pure API password",
    # "pure_rest_api_url": "Pure API url",
    # "pure_username": "Pure username",
    # "rdm_host_url": "RDM host URL",
    # "rdm_token": "RDM token",
    "email_sender": "Sender e-mail for Pure file deletion",
    # "email_sender_password": "Sender password for Pure file deletion",
    # "email_receiver": "E-mail of responsible for Pure deletion",
}

# If the folder does not exist then creates it
Path(full_path).mkdir(parents=True, exist_ok=True)

print("\nSpecifying the basic setup for this module.")
print("Please fill the following fields:\n")

for file in import_setup:
    # Ask for input value
    value = input(f"{import_setup[file]}: ")
    # Create file
    open(f"{dirpath}/{folder_name}/{file}.txt", "w+").write(value)

# Create Pure user and assign admin rights
email = input("RDM user creation - Insert desired Pure user e-mail: ")
password = input("RDM user creation - Password: ")
os.system(f"pipenv run invenio users create {email} --password {password} --active")
os.system("pipenv run invenio roles add {email} admin")
