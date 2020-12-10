..
    Copyright (C) 2020 Technische Universität Graz.

    invenio-rdm-pure is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

==================
 invenio-rdm-pure
==================

.. image:: https://github.com/tu-graz-library/invenio-rdm-pure/workflows/CI/badge.svg
        :target: https://github.com/tu-graz-library/invenio-rdm-pure/actions?query=workflow%3ACI

.. image:: https://coveralls.io/repos/github/tu-graz-library/invenio-rdm-pure/badge.svg
        :target: https://coveralls.io/github/tu-graz-library/invenio-rdm-pure

.. image:: https://img.shields.io/github/tag/fair-data-austria/invenio-rdm-pure.svg
        :target: https://github.com/fair-data-austria/invenio-rdm-pure/releases

.. image:: https://img.shields.io/pypi/dm/invenio-rdm-pure.svg
        :target: https://pypi.python.org/pypi/invenio-rdm-pure

.. image:: https://img.shields.io/github/license/fair-data-austria/invenio-rdm-pure.svg
        :target: https://github.com/fair-data-austria/invenio-rdm-pure/blob/master/LICENSE

.. image:: https://readthedocs.org/projects/invenio-rdm-pure/badge/?version=latest
        :target: https://invenio-rdm-pure.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

Invenio module that adds TUGraz Pure integration.

Further documentation is available on
https://invenio-rdm-pure.readthedocs.io/


---             ---             ---             ---

CLI - SCHEDULED TASKS
---------------------
Changes:
Gets from Pure 'changes' endpoint all records that have been created / updated / deleted on a certain date and modifies accordingly the relative RDM records.

Owner:
Gets from Pure all the records belonging to a certain user and modifies/create RDM records accordingly. Takes in input two attributes:
--identifier: with possible values ‘externalid’ or ‘orcid’ 
--identifierValue: with the ‘externalid’ or ‘orcid’ of the user 

Pure_import:
Get records from RDM and creates with this data an XML file suitable to be imported into Pure, which will be available at the URL …/pure_import.
The RDM records are filtered in two ways:
-   Records that have a value in the field extensions/tug:uuid have been imported from Pure, therefore will be ignored. See _check_uuid method in invenio_rdm_pure/source/pure/import_records.py
-    All records created before the date of the import will be ignored. See _check_date method in invenio_rdm_pure/source/pure/import_records.py

Group_split:
When a group in Pure (organisationalUnit) splits in two, the same process needs to take place also in RDM. Therefore, the following steps:
-   Create new groups
-   Add users belonging to old group into the new groups
-   Remove users from old group
-   Delete old group
-   Modify RDM records belonging to the old group
It takes as input parameters 

Group_merge:
It is the opposite process as compared to group_split. In this case, two groups in Pure (organisationalUnit) merge into one following the next steps:
-   Create new group
-   Remove users from old groups
-   Add users to new group
-   Delete old groups
-   Modify RDM records belonging to the old groups

Logs: 
Removes all old log files from invenio_rdm_pure/reports. The number of days that these files will be kept is specified in invenio_rdm_pure/setup.py days_keep_log variable.

Pages:
Gets records from Pure 'research-outputs' endpoint by page and submit them to RDM. Takes in input three attributes:
-- pageStart: initial page of import
-- pageEnd: last page of import
-- pageSize: size of imported pages

---             ---             ---             ---

CLI - NOT SCHEDULED TASKS
-------------------------
Testing:
Performs testing related to: 
-   RDM records creation and deletion;
-   RDM user creation, role assignment, role removal, user deactivation;

Delete:
Deletes all records listed (by recid) in invenio_rdm_pure/data/to_delete.txt

Uuid:
Adds to RDM all records listed (by uuid) in invenio_rdm_pure/data/to_transmit.txt

---             ---             ---             ---

DATA DIRECTORY
--------------
Invenio_rdm_pure/data/

all_rdm_records.txt:
all records that will be added to RDM will be listed in this file, adding for each record Pure uuid and RDM recid.

successful_changes.txt:
holds the list of dates in which a successful changes task was performed.

user_ids_match.txt:
when running owners task, a match between externalId and RDM user id is done. This information will be store in this file following the order:
RDM user id – Pure uuid – External id

---             ---             ---             ---

VIEWS
-----
https://127.0.0.1:5000/pure_import
Returns an XML file containing RDM records formatted for Pure import

https://127.0.0.1:5000/database_uri
Creates in invenio_rdm_pure/data_setup/ the necessary files for database interaction

https://127.0.0.1:5000/user_import_records
•   Gets the externalId of the logged-in user
•   Gets from Pure all records belonging to the given externalId
•   Checks if these records are already in RDM; if not, they will be added
Note: this is a temporary way to trigger this task. It was necessary to trigger through the browser in order to get the user externalId. When celery scheduled tasks will be running there will be no need any more of this view.
