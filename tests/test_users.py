# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""User operation tests."""

from invenio_rdm_pure.source.rdm.database import RdmDatabase


def test_create_pure_user(base_app) -> None:
    """Test to create pure user."""
    id = RdmDatabase.get_pure_user_id()
    assert id is not None
