from __future__ import annotations

from typing import Iterable

from flask import current_app
from flask_mail import Message

from ..extensions import mail


def send_email(subject: str, recipients: Iterable[str], html_body: str) -> None:
    if not current_app.config.get("MAIL_SERVER"):
        current_app.logger.info("Email sending skipped (MAIL_SERVER not configured). Subject: %s", subject)
        current_app.logger.info("Email preview: %s", html_body)
        return

    msg = Message(
        subject=subject,
        recipients=list(recipients),
        html=html_body,
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
    )
    mail.send(msg)
