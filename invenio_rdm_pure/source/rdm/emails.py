# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Technische Universität Graz
#
# invenio-rdm-pure is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""File description."""

import smtplib

from flask import current_app

from ...setup import email_message, email_smtp_port, email_smtp_server


def send_email(uuid: str, file_name: str):
    """Description."""
    # creates SMTP session
    s = smtplib.SMTP(email_smtp_server, email_smtp_port)

    # start TLS for security
    s.starttls()

    # Authentication
    email_sender = current_app.config.get("INVENIO_PURE_USER_EMAIL")
    email_sender_password = current_app.config.get("INVENIO_PURE_USER_PASSWORD")
    s.login(email_sender, email_sender_password)

    # sending the mail
    message = email_message.format(uuid, file_name)
    email_receiver = current_app.config.get("PURE_RESPONSIBLE_EMAIL")
    s.sendmail(email_sender, email_receiver, message)

    # terminating the session
    s.quit()
