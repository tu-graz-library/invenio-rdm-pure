# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Technische Universität Graz.
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds pure."""

import os

from flask import Blueprint
from flask_babelex import gettext as _

blueprint = Blueprint(
    "invenio_rdm_pure",
    __name__,
    template_folder="templates",
    static_folder="static",
)
