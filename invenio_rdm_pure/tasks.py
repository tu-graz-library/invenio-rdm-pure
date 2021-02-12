# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Scheduled tasks for celery."""

from celery import shared_task
from flask import current_app

from .source.rdm.run.synchronizer import Synchronizer


@shared_task
def synchronize_records():
    """Synchronize records."""
    synchronizer = Synchronizer()
    synchronizer.run_scheduled_synchronization()
