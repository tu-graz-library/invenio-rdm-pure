# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

from flask_login import current_user
from invenio_oauthclient.models import UserIdentity


def user_externalid():
    """Description."""
    if current_user.is_authenticated:
        id = current_user.get_id()
        user_external = UserIdentity.query.filter_by(id_user=id).first()
        if user_external:
            return user_external.id
    return False
