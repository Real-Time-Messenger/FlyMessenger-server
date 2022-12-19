import os
from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, select_autoescape, PackageLoader
from pydantic import EmailStr

# Load the templates.
env = Environment(
    loader=PackageLoader("app", "templates"),
    autoescape=select_autoescape(["html"])
)

# Load the configuration.
config = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_USERNAME"),
    MAIL_FROM_NAME = os.getenv("MAIL_FROM"),
    MAIL_PORT = os.getenv("MAIL_PORT"),
    MAIL_SERVER = os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS = os.getenv("MAIL_STARTTLS"),
    MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS"),
    USE_CREDENTIALS = os.getenv("MAIL_USE_CREDENTIALS"),
    VALIDATE_CERTS = os.getenv("MAIL_VALIDATE_CERTS"),
    TEMPLATE_FOLDER = Path("app/templates"),
)


class EmailService:
    @staticmethod
    async def send_email(email: EmailStr, subject: str, template: str, **kwargs):
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=env.get_template(f"{template}.html").render(**kwargs),
            subtype="html"
        )

        fm = FastMail(config)
        await fm.send_message(message)


# example of usage:
# from app.services.mail.mail import EmailService
#
# await EmailService.send_email(
#     email="email",
#     subject="subject",
#     template="template.html",
#     **kwargs
# )