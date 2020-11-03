# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

import os

from invenio_rdm_pure.setup import temporary_files_name
from invenio_rdm_pure.source.rdm.requests_rdm import Requests
from invenio_rdm_pure.source.reports import Reports


def rdm_add_file(file_name: str, recid: str):
    """Description."""
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
