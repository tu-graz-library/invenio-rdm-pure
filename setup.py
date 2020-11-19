# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds pure."""

import os

from setuptools import find_packages, setup

readme = open("README.rst").read()
history = open("CHANGES.rst").read()

tests_require = [
    "pytest-invenio>=1.4.0",
    "invenio-search[elasticsearch7]>=1.4.0",
]

extras_require = {
    "docs": [
        "Sphinx>=1.5.1",
    ],
    "tests": tests_require,
}

extras_require["all"] = []
for reqs in extras_require.values():
    extras_require["all"].extend(reqs)

setup_requires = [
    "Babel>=1.3",
    "pytest-runner>=3.0.0,<5",
]

install_requires = [
    "Flask-BabelEx>=0.9.4",
    "docopt>=0.6.2",
    "invenio_oauthclient>=1.2.1",
    "invenio-rdm-records>=0.23.4",
    "sqlalchemy-continuum>=1.3.11",
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("invenio_rdm_pure", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="invenio-rdm-pure",
    version=version,
    description=__doc__,
    long_description=readme + "\n\n" + history,
    keywords="invenio TODO",
    license="MIT",
    author="Technische Universität Graz",
    author_email="info@fair-data-austria.com",
    url="https://github.com/fair-data-austria/invenio-rdm-pure",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={
        "invenio_base.apps": [
            "invenio_rdm_pure = invenio_rdm_pure:InvenioRdmPure",
        ],
        "invenio_base.blueprints": [
            "invenio_rdm_pure = invenio_rdm_pure.views:blueprint",
        ],
        "invenio_i18n.translations": [
            "messages = invenio_rdm_pure",
        ],
        "invenio_celery.tasks": ["invenio_rdm_pure = invenio_rdm_pure.tasks"],
        "invenio_config.module": [
            "invenio_rdm_pure = invenio_rdm_pure.config",
        ],
        # TODO: Edit these entry points to fit your needs.
        # 'invenio_access.actions': [],
        # 'invenio_admin.actions': [],
        # 'invenio_assets.bundles': [],
        # 'invenio_base.api_apps': [],
        # 'invenio_base.api_blueprints': [],
        # 'invenio_base.blueprints': [],
        # 'invenio_db.models': [],
        # 'invenio_pidstore.minters': [],
        # 'invenio_records.jsonresolver': [],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 1 - Planning",
    ],
)
