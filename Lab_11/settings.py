import os
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv  

from fastapi_mail import ConnectionConfig
from pathlib import Path

from slowapi import Limiter
from slowapi.util import get_remote_address

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
SQLALCHEMY_TEST_DATABASE_URL = os.getenv('SQLALCHEMY_TEST_DATABASE_URL')


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

CLOUDINARY_NAME = os.getenv('CLOUDINARY_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET_KEY = os.getenv('CLOUDINARY_API_SECRET_KEY')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")




conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_FROM=os.getenv('MAIL_FROM'),
    MAIL_PORT=465,
    MAIL_SERVER="smtp.meta.ua",
    MAIL_FROM_NAME="Mozok E",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

limiter = Limiter(key_func=get_remote_address)

user_agent_ban_list = [r"Python-urllib"]