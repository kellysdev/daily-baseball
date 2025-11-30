# emailer.py
import os
import smtplib
from email.message import EmailMessage
import json
from typing import Optional

def send_via_smtp(
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
    from_addr: str,
    to_addrs: list,
    subject: str,
    html_body: str,
):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addrs)
    msg.set_content("This is an HTML email. If you see this, your mail client does not support HTML.")
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(msg)

def send_email(
    subject: str,
    html_body: str,
    to_addrs: list,
    from_addr: Optional[str] = None,
):
    """
    Choose sending method based on env variables:
     - Expect SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASS/SMTP_FROM
    """
    # Prefer explicit from_addr param, otherwise from env
    from_addr = from_addr or os.environ.get("EMAIL_FROM")

    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    smtp_from = from_addr or os.environ.get("SMTP_FROM")
    if not all([smtp_host, smtp_user, smtp_pass, smtp_from]):
        raise RuntimeError("No email sending method configured (SENDGRID_API_KEY or SMTP_* env vars).")

    return send_via_smtp(smtp_host, smtp_port, smtp_user, smtp_pass, smtp_from, to_addrs, subject, html_body)