import select
from typing import Optional
from sqlalchemy.orm import Session

from fastapi import UploadFile
from fastapi.security import OAuth2PasswordRequestForm

from database.models import User

from repository.auth import create_access_token, create_refresh_token, Hash, get_email_form_refresh_token

from utils.cloudinary import upload_file_to_cloudinary

from shemas import UserModel

hash_handler = Hash()

class UsernameTaken(Exception):
    """Raised when the username is already taken."""
    pass

class LoginFailed(Exception):
    """Raised when login fails due to incorrect credentials."""
    pass 

class InvalidRefreshtoken(Exception):
    """Raised when the refresh token is invalid."""
    pass



class UserService: 
    """
    Service class for handling user-related operations.
    """

    @staticmethod
    def get_user(username: str, db: Session) -> Optional[User]:
        """
        Retrieve a user by username (email).

        :param username: The user's email.
        :param db: Database session.
        :return: The user object if found, else None.
        """
        return db.query(User).filter(User.email == username).first()



    @staticmethod
    def check_username_availablity(username: str, db: Session):
        """
        Check if a username (email) is available.

        :param username: The user's email.
        :param db: Database session.
        :raises UsernameTaken: If the username is already taken.
        """
        exist_user = UserService.get_user(username, db)
        if exist_user:
            raise UsernameTaken
        

    # @staticmethod
    # def check_password(entered_password: str, database_password: str ):
    #     """
    #     Check if the entered password matches the database password.

    #     :param entered_password: The entered password.
    #     :param database_password: The database password.
    #     :raises LoginFailed: If the password is incorrect.
    #     :return: The user object if the password is correct.
    #     """
    #     if not hash_handler.verify_password(body.password, user.password):
    #         raise UserWrongPassword
    #     return exist_user

        
    @staticmethod
    def creat_new_user(body: UserModel, db: Session ):
        """
        Create a new user.

        :param body: UserModel containing the user's data.
        :param db: Database session.
        :return: The newly created user.
        """
        UserService.check_username_availablity(username=body.username, db=db )
        new_user = User(email=body.username, password=hash_handler.get_password_hash(body.password))
        new_user = UserService.save_user(new_user, db)
        return new_user
    
    @staticmethod
    def login_user(body: OAuth2PasswordRequestForm, db: Session):
        """
        Authenticate and log in a user.

        :param body: OAuth2PasswordRequestForm containing the login credentials.
        :param db: Database session.
        :return: A tuple of access and refresh tokens.
        :raises LoginFailed: If the login fails.
        """
        user = UserService.get_user(body.username, db = db )
        if user is None or not hash_handler.verify_password(body.password, user.password):
            raise  LoginFailed
        
        data={"sub": user.email}
        access_token = create_access_token(data=data)
        refresh_token = create_refresh_token(data=data)
        user.refresh_token = refresh_token
        
        UserService.save_user(user, db)
        return access_token, refresh_token
    
    @staticmethod
    def refresh_token(refresh_token: str, db: Session):
        """
        Refresh an access token using a refresh token.

        :param refresh_token: The refresh token.
        :param db: Database session.
        :return: The new access token.
        :raises InvalidRefreshtoken: If the refresh token is invalid.
        
        """
        email = get_email_form_refresh_token(refresh_token)
        user = UserService.get_user(email, db)
        if user.refresh_token != refresh_token:
            user.refresh_token = None
            UserService.save_user(user, db)
            raise InvalidRefreshtoken

        access_token = create_access_token(data={"sub": email})
        return access_token
        
    
    @staticmethod
    def save_user(user_to_save, db: Session) -> User:
        """
        Save a user to the database.

        :param user_to_save: The user object to save.
        :param db: Database session.
        :return: The saved user.
        """
        db.add(user_to_save)
        db.commit()
        db.refresh(user_to_save)
        return user_to_save
    
    @staticmethod
    def get_user_by_email(email: str, db: Session):
        """
        Retrieve a user by email.

        :param email: The user's email.
        :param db: Database session.
        :return: The user object if found, else None.
        """
        result =  db.query(User).filter(User.email == email)
        return result.first()
    
    @staticmethod
    def confirmed_email(email: str, db: Session) -> None:
        """
        Confirm a user's email.

        :param email: The user's email.
        :param db: Database session.
        """
        user = UserService.get_user_by_email(email, db)
        user.confirmed = True
        db.commit()

    @staticmethod
    def update_avatar(user: User, file: UploadFile, db: Session):
        """
        Update a user's avatar.

        :param user: The user object.
        :param file: The uploaded file containing the new avatar.
        :param db: Database session.
        :return: The updated user object.
        """
        user.avatar_urls = upload_file_to_cloudinary(file.file, f'user_avatar_{user.id}')
        UserService.save_user(user, db)
        return user 

