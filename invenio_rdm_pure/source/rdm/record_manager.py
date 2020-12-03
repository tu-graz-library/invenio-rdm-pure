# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record Manager Module to facilitate Invenio Record interaction."""

import json
from typing import Optional

from flask import current_app
from flask_principal import Identity
from invenio_access.permissions import any_user
from invenio_rdm_records.services import (
    BibliographicRecordService,
    BibliographicRecordServiceConfig,
)
from invenio_records_permissions.generators import AnyUser
from invenio_records_permissions.policies import RecordPermissionPolicy
from invenio_records_resources.services.records.results import RecordItem
from marshmallow.exceptions import ValidationError
from requests.models import Response

from ..reports import Reports
from .database import RdmDatabase
from .requests_rdm import Requests


class PermissionPolicy(RecordPermissionPolicy):
    """Policy class to use with BibliographicRecordServiceConfig."""

    can_create = [AnyUser()]
    can_update_files = [AnyUser()]
    can_publish = [AnyUser()]
    can_read = [AnyUser()]
    can_update = [AnyUser()]
    can_delete = [AnyUser()]
    # FIXME: can_delete has to be changed as soon as user group management
    # works with "current_app.extensions["security"].datastore"


class ServiceConfig(BibliographicRecordServiceConfig):
    """Config class to use with BibliographicRecordService."""

    permission_policy_cls = PermissionPolicy


class RecordManager(object):
    """Record Manager Class to facilitate Invenio Record interaction."""

    __instance: Optional["RecordManager"] = None
    __create_key = object()

    @classmethod
    def instance(cls) -> "RecordManager":
        """Instance method to facilitate singleton pattern."""
        if cls.__instance is None:
            cls.__instance = RecordManager(cls.__create_key)
        return cls.__instance

    def __init__(self, create_key):
        """Constructor with singleton pattern."""
        assert (
            create_key == RecordManager.__create_key
        ), "RecordManager class must be accessed using RecordManager.instance()"
        self.identity = Identity(current_app.config.get(RdmDatabase.get_pure_user_id()))
        self.identity.provides.add(any_user)
        self.service = BibliographicRecordService(config=ServiceConfig)

    def create_record(self, data: dict) -> Optional[RecordItem]:
        """Creates a record from JSON data."""
        if not data:
            return None
        try:
            record = self.service.create(self.identity, data)
            self.service.publish(id_=record.id, identity=self.identity)
            return record

        except ValidationError:
            return None

    def update_record(self, recid: str, data: dict) -> Optional[RecordItem]:
        """Updates a record with JSON data."""
        if not data:
            return None
        try:
            original_record = self.service.read(id_=recid, identity=self.identity)
            original_revision_id = original_record._record.revision_id
            updated_record = self.service.update(
                id_=recid, identity=self.identity, data=data
            )
            return updated_record

        except ValidationError:
            return None

    def update_record_rest(self, recid: str, data: dict) -> Response:
        """Updates a record via REST API with JSON data."""
        response = Requests().put_metadata(recid, data)

        rdm_host_url = current_app.config.get("INVENIO_PURE_HOST_URL")
        url = f"{rdm_host_url}api/records/{recid}"
        Reports().add(f"\tRecord update @ {response} @ {url}")

        return response

    def delete_record(self, recid: str) -> None:
        """Deletes record with given recid."""
        if not recid:
            raise ValueError("Can't delete record without providing recid.")
        deleted = self.service.delete(id_=recid, identity=self.identity)
        if not deleted:
            raise RuntimeError("Failed to delete record.")

    def is_newest_record(self, record: RecordItem) -> bool:
        """Checks if the given record is the most recently inserted one."""
        if record is not None:
            newest_query = {"sort": "newest", "size": 1, "page": 1}
            response = Requests.get_metadata(additional_parameters=newest_query)
            if response.ok:
                response_json = json.loads(response.text)
                newest_recid = response_json["hits"]["hits"][0]["id"]
                if record.id == newest_recid:
                    return True
        return False
