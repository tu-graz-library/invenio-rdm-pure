import os

from source.rdm.requests import Requests
from source.reports import Reports

from setup import temporary_files_name


def rdm_add_file(file_name: str, recid: str):

    rdm_requests = Requests()
    reports = Reports()

    file_path_name = f"{temporary_files_name['base_path']}/{file_name}"

    # PUT FILE TO RDM
    response = rdm_requests.put_file(file_path_name, recid)

    # Report
    reports.add(f"\tRDM put file @ {response} @ {file_name}")

    if response.status_code >= 300:
        reports.add(response.content)
        return False

    else:
        # if the upload was successful then delete file from /reports/temporary_files
        os.remove(file_path_name)
        return True
