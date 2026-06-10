"""Send email through Gmail SMTP using an app password."""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()
_ADDRESS      = os.environ["GMAIL_ADDRESS"]
_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]


def send_email(to_address: str, subject: str, html_body: str, from_name: str = "Hamecon Training"):
    """Send one HTML email. from_name shows in the recipient's inbox."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{from_name} <{_ADDRESS}>"
    msg["To"]      = to_address
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
        server.starttls()
        server.login(_ADDRESS, _APP_PASSWORD)
        server.sendmail(_ADDRESS, to_address, msg.as_string())
