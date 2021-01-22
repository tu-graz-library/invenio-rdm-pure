# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

from .source.pure.import_records import ImportRecords
from .source.rdm.delete_record import Delete
from .source.rdm.run.changes import PureChanges
from .source.rdm.run.groups import RdmGroups
from .source.rdm.run.owners import RdmOwners
from .source.rdm.run.pages import RunPages
from .source.rdm.run.uuid_run import AddFromUuidList

# from .source.rdm.testing.run_test import Testing
from .source.reports import Reports


class ShellInterface:
    """ShellInterface."""

    def testing(self):
        """testing."""
        testing = Testing()
        testing.run()

    def pure_import(self):
        """Pure import."""
        pure_import_records = ImportRecords()
        pure_import_records.run_import()

    def changes(self):
        """Gets changes from Pure API endpoint.

        all the records that have been created, modified and deleted.

        Next updates accordingly RDM records.
        """
        pure_changes_by_date = PureChanges()
        pure_changes_by_date.get_pure_changes()

    def pages(self, page_start, page_end, page_size):
        """Push to RDM records from Pure by page."""
        run_pages = RunPages()
        run_pages.get_pure_by_page(page_start, page_end, page_size)

    def logs(self):
        """Delete old log files."""
        Reports().delete_old_log_files()

    def delete(self):
        """Delete RDM records by recid (to_delete.log)."""
        delete = Delete()
        delete.from_list()

    def uuid(self):
        """Push to RDM all uuids that are in to_transfer.log."""
        add_uuids = AddFromUuidList()
        add_uuids.add_from_uuid_list()

    def owner(self, identifier, identifier_value):
        """Gets from pure all the records related to a certain user.

        afterwards it create/modify/delete RDM records accordingly.
        """
        rdm_owners = RdmOwners()
        rdm_owners.run_owners(identifier, identifier_value)

    def rdm_group_split(self, old_id, new_ids):
        """Split a single group into moltiple ones."""
        rdm_groups = RdmGroups()
        rdm_groups.rdm_group_split(old_id, new_ids)

    def rdm_group_merge(self, old_ids, new_id):
        """Merges multiple groups into a single one."""
        rdm_groups = RdmGroups()
        rdm_groups.rdm_group_merge(old_ids, new_id)


def method_call(docopt_instance: object, arguments: dict):
    """Call method."""
    if arguments["pure_import_xml"]:
        docopt_instance.pure_import()

    elif arguments["get_pure_changes"]:
        docopt_instance.changes()

    elif arguments["rdm_testing"]:
        docopt_instance.testing()

    elif arguments["get_pure_pages"]:
        page_start = int(arguments["--pageStart"])
        page_end = int(arguments["--pageEnd"])
        page_size = int(arguments["--pageSize"])
        docopt_instance.pages(page_start, page_end, page_size)

    elif arguments["delete_old_logs"]:
        docopt_instance.logs()

    elif arguments["delete_by_recid"]:
        docopt_instance.delete()

    elif arguments["add_by_uuid"]:
        docopt_instance.uuid()

    elif arguments["get_owner_records"]:
        identifier = arguments["--identifier"]
        identifier_value = arguments["--identifierValue"]
        docopt_instance.owner(identifier, identifier_value)

    elif arguments["group_split"]:
        old_id = arguments["--oldGroup"]
        new_ids = arguments["--newGroups"].split(" ")
        docopt_instance.rdm_group_split(old_id, new_ids)

    elif arguments["group_merge"]:
        old_ids = arguments["--oldGroups"].split(" ")
        new_id = arguments["--newGroup"]
        docopt_instance.rdm_group_merge(old_ids, new_id)
