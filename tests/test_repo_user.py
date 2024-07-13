import unittest
from unittest.mock import MagicMock, Mock, patch
from unittest import TestCase, mock
import tempfile

from sqlalchemy.orm import Session
from fastapi import UploadFile
from fastapi.security import OAuth2PasswordRequestForm

from database.models import User
from repository.auth import create_access_token, create_refresh_token, get_email_form_refresh_token, Hash
from repository.users_crud import UserService, UsernameTaken, LoginFailed, InvalidRefreshtoken, hash_handler

from utils.cloudinary import upload_file_to_cloudinary

from shemas import UserModel

from datetime import datetime, timedelta, timezone

from settings import SECRET_KEY, ALGORITHM

from jose import JWTError, jwt


class TestUserService(unittest.TestCase):

    def setUp(self):
        self.db = Mock(spec=Session)
        self.db.commit = Mock()

    def test_get_user(self):
        mock_user = User(email="test@example.com")

        self.db.query.return_value.filter.return_value.first.return_value = mock_user

        result = UserService.get_user("test@example.com", self.db)

        self.assertEqual(result.email, "test@example.com")

    def test_get_user_not_found(self):
        self.db.query.return_value.filter.return_value.first.return_value = None

        result = UserService.get_user("nonexistent@example.com", self.db)
        self.assertIsNone(result)

    def test_check_username_availability_taken(self):
        mock_user = User(email="taken@example.com")
        self.db.query.return_value.filter.return_value.first.return_value = mock_user

        with self.assertRaises(UsernameTaken):
            UserService.check_username_availablity("taken@example.com", self.db)

    def test_check_username_availability_available(self):
        self.db.query.return_value.filter.return_value.first.return_value = None

        try:
            UserService.check_username_availablity("available@example.com", self.db)
        except UsernameTaken:
            self.fail("UserService.check_username_availablity() raised UsernameTaken unexpectedly!")

    def test_create_new_user(self):
        body = UserModel(username="newuser@example.com", password="password123")
        self.db.query.return_value.filter.return_value.first.return_value = None
        self.db.add.return_value = None

        result = UserService.creat_new_user(body, self.db)
        self.assertEqual(result.email, "newuser@example.com")

    def test_login_user_successful(self):
        body = OAuth2PasswordRequestForm(username="test@example.com", password="password123")
        hashed_password = hash_handler.get_password_hash("password123")
        mock_user = User(email="test@example.com", password=hashed_password)

        self.db.query.return_value.filter.return_value.first.return_value = mock_user

        access_token, refresh_token = UserService.login_user(body, self.db)
        self.assertIsNotNone(access_token)
        self.assertIsNotNone(refresh_token)

    def test_login_user_failed(self):
        body = OAuth2PasswordRequestForm(username="test@example.com", password="incorrect_password")
        hashed_password = hash_handler.get_password_hash("password123")
        mock_user = User(email="test@example.com", password=hashed_password)

        self.db.query.return_value.filter.return_value.first.return_value = mock_user

        with self.assertRaises(LoginFailed):
            UserService.login_user(body, self.db)

    def test_refresh_token_valid(self):
        refresh_token = "valid_refresh_token"
        mock_user = mock.Mock(spec=User)
        mock_user.refresh_token = refresh_token
        self.db.query.return_value.filter.return_value.first.return_value = mock_user
        access_token_data = {"sub": mock_user.email}

        with mock.patch('repository.auth.create_access_token', return_value="new_access_token"):
            
            access_token = UserService.refresh_token(refresh_token, self.db)

            
            self.assertEqual(access_token, "new_access_token")
            self.db.query.return_value.filter.assert_called_once_with(User.email == mock_user.email)
            self.db.commit.assert_called_once()

    def test_refresh_token_invalid(self):
        refresh_token = "invalid_refresh_token"
        mock_user = Mock(spec=User)
        mock_user.refresh_token = "valid_refresh_token"
        self.db.query.return_value.filter.return_value.first.return_value = mock_user

        with self.assertRaises(InvalidRefreshtoken):
            UserService.refresh_token(refresh_token, self.db)

    def test_update_avatar(self):
        mock_user = User(id=1)
        
        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp_file:
            tmp_file.write(b"dummy_content")
            tmp_file.flush()
            tmp_file.seek(0)
            
            user_avatar = UploadFile(filename="avatar.jpg", file=tmp_file)

            with unittest.mock.patch('utils.cloudinary.upload_file_to_cloudinary', return_value='mocked_url'):
                updated_user = UserService.update_avatar(mock_user, user_avatar, self.db)

                self.assertEqual(updated_user.avatar_urls, 'mocked_url')

    def test_confirmed_email(self):
        mock_user = Mock(spec=User)
        self.db.query.return_value.filter.return_value.first.return_value = mock_user

        UserService.confirmed_email("test@example.com", self.db)
        self.assertTrue(mock_user.confirmed)

if __name__ == '__main__':
    unittest.main()