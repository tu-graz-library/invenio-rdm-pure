import smtplib

from flask import current_app

from setup import (
    email_message,
    email_sender,
    email_sender_password,
    email_smtp_port,
    email_smtp_server,
)


def send_email(uuid: str, file_name: str):

    # creates SMTP session
    s = smtplib.SMTP(email_smtp_server, email_smtp_port)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(email_sender, email_sender_password)

    # sending the mail
    message = email_message.format(uuid, file_name)
    email_receiver = current_app.config.get("PURE_RESPONSIBLE_EMAIL")
    s.sendmail(email_sender, email_receiver, message)

    # terminating the session
    s.quit()
