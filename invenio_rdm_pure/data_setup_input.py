from setup                          import dirpath
from source.general_functions       import check_if_directory_exists

import_setup = {
    'pure_api_key':         'Pure API key',
    'pure_password':        'Pure API password',
    'pure_rest_api_url':    'Pure API url',
    'pure_username':        'Pure username',
    'rdm_host_url':         'RDM host URL',
    'rdm_token':            'RDM token',
    'email_sender':         'Sender e-mail for Pure file deletion',
    'email_sender_password':'Sender password for Pure file deletion',
    'email_receiver':       'E-mail of responsible for Pure deletion'
}

folder_name = 'data_setup'
check_if_directory_exists(folder_name)

for file in import_setup:
    value = input(f"\nPlease insert '{import_setup[file]}': ")
    open(f"{dirpath}/{folder_name}/{file}.txt", "w+").write(value)