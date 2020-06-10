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

blueprint = Blueprint(
    'invenio_rdm_pure',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@blueprint.route("/test-irp")
def index():
    """Render a basic view."""
    return render_template(
        "invenio_rdm_pure/index.html",
        module_name=_('invenio-rdm-pure'))
