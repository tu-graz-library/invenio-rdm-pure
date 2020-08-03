Installation
============

invenio-rdm-pure is on PyPI so all you need is:

Make sure you have already installed invenio-config-tugraz module (https://github.com/mb-wali/invenio-config-tugraz.git)

.. code-block:: console

   $ git clone git@github.com:fair-data-austria/invenio-rdm-pure.git

   $ python ../invenio-rdm-pure/invenio_rdm_pure/initial_setup.py

Running initial_setup.py, the following information will be asked:
•	Pure API key (36 digits)
•	Pure API URL (e.g. https://pure01.tugraz.at/ws/api/514)
•	Pure username
•	Pure password
•	RDM host URL (e.g. https://127.0.0.1:5000)
•	RDM token (Created using invenio UI)
•	Pure file deletion – Sender e-mail
•	Pure file deletion – Sender password
•	Pure file deletion – E-mail of Pure responsible for deletion
•	RDM user creation – Insert Pure user e-mail
•	RDM user creation – Password

.. code-block:: console

   $ pip install -e ../invenio-rdm-pure

Once the module is installed, call https://127.0.0.1:5000/database_uri to get database URI (see description in VIEWS chapter)

Add fields applied_restrictions and group_restrictions to invenio-rdm-records module (https://github.com/mat-gro/invenio-rdm-records)

Comment in invenio-rdm-records/marshmellow/json.py all identifiers validations (in AffiliationSchemaV1 and CreatorSchemaV1) in order to allow to add as creators’ identifiers externalId and uuid (see https://github.com/mat-gro/invenio-rdm-records/blob/master/marshmallow/json.py)

