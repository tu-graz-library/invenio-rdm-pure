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
]

# Should follow inveniosoftware/invenio versions
invenio_db_version = ">=1.0.4,<2.0.0"
invenio_search_version = ">=1.4.0,<2.0.0"

extras_require = {
    "docs": [
        "Sphinx>=1.5.1",
    ],
    "elasticsearch7": [
        "invenio-search[elasticsearch7]{}".format(invenio_search_version),
    ],
    "postgresql": [
        "invenio-db[postgresql,versioning]{}".format(invenio_db_version),
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
    "docopt>=0.6.2",
    "Flask-BabelEx>=0.9.4",
    "invenio-access>=1.3.3",
    "invenio-accounts>=1.4.3",
    "invenio-app>=1.3.0",
    "invenio-celery>=1.2.2",
    "invenio-db>=1.0.8",
    "invenio-records-marc21>=0.1.0",
    "lxml>=4.6.2",
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
        "invenio_config.module": [
            "invenio_rdm_pure = invenio_rdm_pure.config",
        ],
        "invenio_celery.tasks": ["invenio_rdm_pure = invenio_rdm_pure.tasks"],
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
