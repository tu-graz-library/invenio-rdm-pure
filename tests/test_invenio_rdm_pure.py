# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz.
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from flask import Flask

from invenio_rdm_pure import InvenioRdmPure
from invenio_rdm_pure.source.rdm.run.uuid_run import AddFromUuidList


def test_version():
    """Test version import."""
    from invenio_rdm_pure import __version__

    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask("testapp")
    ext = InvenioRdmPure(app)
    assert "invenio-rdm-pure" in app.extensions

    app = Flask("testapp")
    ext = InvenioRdmPure()
    assert "invenio-rdm-pure" not in app.extensions
    ext.init_app(app)
    assert "invenio-rdm-pure" in app.extensions


def test_add_from_uuid_list():
    """Tests the method add_from_uuid_list."""
    try:
        AddFromUuidList().add_from_uuid_list()
        assert False
    except FileNotFoundError:
        assert True
