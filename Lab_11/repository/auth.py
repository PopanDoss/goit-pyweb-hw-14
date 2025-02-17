from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException
from passlib.context import CryptContext

from sqlalchemy.orm import Session
from jose import JWTError, jwt
from starlette import status

from database.models import User
from database.db import get_db

from settings import SECRET_KEY, ALGORITHM, oauth2_scheme

class Hash:

    """
    Class for handling password hashing.

    :attributes pwd_context: The context for hashing passwords using bcrypt. (CryptContext)
        
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies the given plain password against the hashed password.

        :param plain_password: The original password. (str)
        :param hashed_password: The hashed password. (str)
        :returns: True if the passwords match, False otherwise. (bool)
    
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generates a hash for the given password.

        :param password: The original password. (str)
        :returns: The hashed password. (str)
        
        """
        return self.pwd_context.hash(password)



def create_access_token(data: dict, expires_delta: Optional[float] = None):
    """
    Creates an access token.

    
    :param data: The data to encode in the token. (dict)
    :param expires_delta: The number of seconds until the token expires. (Optional[float])
    :returns: The encoded access token. (str)

    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "access_token"})
    encoded_access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_access_token


# define a function to generate a new refresh token
def create_refresh_token(data: dict, expires_delta: Optional[float] = None):
    """
    Creates a refresh token.

    :param data: The data to encode in the token. (dict)
    :param expires_delta: The number of seconds until the token expires. (Optional[float])
    :returns: The encoded refresh token. (str)

    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(datetime.UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"})
    encoded_refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_refresh_token


def get_email_form_refresh_token(refresh_token: str):
    """
    Retrieves the email from the refresh token.

    :param refresh_token: The refresh token. (str)
    :returns: The email extracted from the token. (str)
    :raises HTTPException: If the token is invalid or has an incorrect scope.
    
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload['scope'] == 'refresh_token':
            email = payload['sub']
            return email
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retrieves the current user based on the access token.

    :param token: The access token. (str)
    :param db: The database session. (Session)
    :returns User: The current user.
    :raises HTTPException: If the token is invalid or the user is not found.
   
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload['scope'] == 'access_token':
            email = payload["sub"]
            exp = payload['exp']
            if email is None:
                raise credentials_exception
            if exp is None or exp <= int(datetime.now(timezone.utc).timestamp()):
                raise HTTPException( 
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="JWT Token expired",
                    headers={"WWW-Authenticate": "Bearer"})
        else:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    user: User = db.query(User).filter(User.email == email).first()
    if user is None :
        raise credentials_exception
    return user

