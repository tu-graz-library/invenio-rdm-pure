# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Fair Data Austria.
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from flask import Flask

from invenio_rdm_pure import inveniordmpure


def test_version():
    """Test version import."""
    from invenio_rdm_pure import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = inveniordmpure(app)
    assert 'invenio-rdm-pure' in app.extensions

    app = Flask('testapp')
    ext = inveniordmpure()
    assert 'invenio-rdm-pure' not in app.extensions
    ext.init_app(app)
    assert 'invenio-rdm-pure' in app.extensions


def test_view(base_client):
    """Test view."""
    res = base_client.get("/")
    assert res.status_code == 200
    assert 'Welcome to invenio-rdm-pure' in str(res.data)
