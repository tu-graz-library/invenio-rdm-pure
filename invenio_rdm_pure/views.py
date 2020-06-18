# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Fair Data Austria.
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds pure"""

# TODO: This is an example file. Remove it if you do not need it, including
# the templates and static folders as well as the test case.

from flask import Blueprint, render_template
from flask_babelex import gettext as _

from flask.globals import session
import os
from flask import current_app

blueprint = Blueprint(
    'invenio_rdm_pure',
    __name__,
    template_folder='templates',
    static_folder='static',
)


# Pure import
@blueprint.route("/pure_import")
def index1():
    """Render a basic view."""
    return render_template(
        # "invenio_rdm_pure/temporary_files/pure_import.xml",
        "invenio_rdm_pure/temporary_files/test.xml",
        module_name=_('invenio-rdm-pure'))


# Session data
@blueprint.route("/session_data")
def index2():
    def _get_session_field(field):
        if field in session:
            print(f'{field}: {session[field]}')
            return session[field]
    print('\n')
    _get_session_field('_permanent')
    _get_session_field('_fresh')
    _get_session_field('SSO::SAML::NameId')
    _get_session_field('SSO::SAML::SessionIndex')
    _get_session_field('user_id')
    _get_session_field('_id')
    _get_session_field('csrf_token')
    print('\n')
    return 'flask session'


# Run owner task
@blueprint.route("/run_owner")
def index3():
    command = '/home/bootcamp/src/cli12/virtual-env/bin/python3.6 /home/bootcamp/src/cli12/invenio-rdm-pure/invenio_rdm_pure/cli.py '
    os.system(command + "owner --identifier='externalId'")
    return 'Run task'


