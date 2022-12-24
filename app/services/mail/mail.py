import os
from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from jinja2 import Environment, select_autoescape, PackageLoader
from pydantic import EmailStr

# Load the templates.
env = Environment(
    loader=PackageLoader("app", "templates"),
    autoescape=select_autoescape(["html"])
)

# Validate the mail configuration.
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
assert MAIL_USERNAME is not None, "MAIL_USERNAME is not set. Please set it in your .env file."

MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
assert MAIL_PASSWORD is not None, "MAIL_PASSWORD is not set. Please set it in your .env file."

MAIL_FROM = os.getenv("MAIL_FROM")
assert MAIL_FROM is not None, "MAIL_FROM is not set. Please set it in your .env file."

MAIL_PORT = os.getenv("MAIL_PORT")
assert MAIL_PORT is not None, "MAIL_PORT is not set. Please set it in your .env file."

MAIL_SERVER = os.getenv("MAIL_SERVER")
assert MAIL_SERVER is not None, "MAIL_SERVER is not set. Please set it in your .env file."

MAIL_STARTTLS = os.getenv("MAIL_STARTTLS")
assert MAIL_STARTTLS is not None, "MAIL_STARTTLS is not set. Please set it in your .env file."

MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS")
assert MAIL_SSL_TLS is not None, "MAIL_SSL_TLS is not set. Please set it in your .env file."

MAIL_USE_CREDENTIALS = os.getenv("MAIL_USE_CREDENTIALS")
assert MAIL_USE_CREDENTIALS is not None, "MAIL_USE_CREDENTIALS is not set. Please set it in your .env file."

MAIL_VALIDATE_CERTS = os.getenv("MAIL_VALIDATE_CERTS")
assert MAIL_VALIDATE_CERTS is not None, "VALIDATE_CERTS is not set. Please set it in your .env file."

# Load the configuration.
config = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=EmailStr(MAIL_USERNAME),
    MAIL_FROM_NAME=MAIL_FROM,
    MAIL_PORT=int(MAIL_PORT),
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
    USE_CREDENTIALS=MAIL_USE_CREDENTIALS,
    VALIDATE_CERTS=MAIL_VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path("app/templates"),
)


class EmailService:
    @staticmethod
    async def send_email(email: EmailStr, subject: str, template: str, **kwargs):
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=env.get_template(f"{template}.html").render(**kwargs),
            subtype=MessageType.html
        )

        fm = FastMail(config)
        await fm.send_message(message)
