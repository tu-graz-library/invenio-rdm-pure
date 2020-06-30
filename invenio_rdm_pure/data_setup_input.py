import os
from pathlib import Path
dirpath = os.path.dirname(os.path.abspath(__file__))

import_setup = {
    "pure_api_key": "Pure API key",
    "pure_password": "Pure API password",
    "pure_rest_api_url": "Pure API url",
    "pure_username": "Pure username",
    "rdm_host_url": "RDM host URL",
    "rdm_token": "RDM token",
    "email_sender": "Sender e-mail for Pure file deletion",
    "email_sender_password": "Sender password for Pure file deletion",
    "email_receiver": "E-mail of responsible for Pure deletion",
}

folder_name = "data_setup"
full_path = f"{dirpath}/{folder_name}"

# If full_path does not exist creates the folder
Path(full_path).mkdir(parents=True, exist_ok=True)

print('\nSpecifying the basic setup for this module.\nPlease fill the following fields:\n')

for file in import_setup:
    value = input(f"Please insert '{import_setup[file]}': ")
    open(f"{dirpath}/{folder_name}/{file}.txt", "w+").write(value)
