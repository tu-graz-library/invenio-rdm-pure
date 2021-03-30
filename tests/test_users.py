# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""User operation tests."""

from invenio_rdm_pure.utils import get_user_id


def test_create_pure_user(base_app) -> None:
    """Test to create pure user."""
    id = get_user_id("pure_user", "pure_password")
    assert id is not None


def test_get_pure_user_id(base_app) -> None:
    """Test to create pure user and then get their ID."""
    created_id = get_user_id("pure_user", "pure_password")
    assert created_id is not None
    retrieved_id = get_user_id("pure_user", "pure_password")
    assert retrieved_id is not None
    assert created_id == retrieved_id
