from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from repository.users_crud import UserService
from services.auth_service import create_email_token
from settings import conf

async def send_email(email: EmailStr, host: str):
    """
    Send an email for email verification.

    :param email: The email address of the recipient.
    :param host: The base URL of the application.
    """
    try:
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_tamplate.html")
    except ConnectionErrors as err:
        print(err)
