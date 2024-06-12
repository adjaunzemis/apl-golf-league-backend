from functools import lru_cache
from typing import Any, Dict, List

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr

from app.dependencies import get_settings


class EmailSchema(BaseModel):
    subject: str
    to_addresses: List[EmailStr]
    body: Dict[str, Any]


@lru_cache()
def get_email_config() -> ConnectionConfig:
    settings = get_settings()
    return ConnectionConfig(
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=settings.mail_password,
        MAIL_FROM=settings.mail_from_address,
        MAIL_FROM_NAME=settings.mail_from_name,
        MAIL_SERVER=settings.mail_server,
        MAIL_PORT=settings.mail_port,
        TEMPLATE_FOLDER="app/templates/",
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
    )


async def send_email(
    email: EmailSchema,
    template_name: str,
    background_tasks: BackgroundTasks | None = None,
):
    message = MessageSchema(
        subject=email.model_dump().get("subject"),
        recipients=email.model_dump().get("to_addresses"),
        template_body=email.model_dump().get("body"),
        subtype=MessageType.html,
    )
    fm = FastMail(get_email_config())

    if background_tasks is None:
        await fm.send_message(message=message, template_name=template_name)
    else:
        background_tasks.add_task(fm.send_message, message, template_name=template_name)
