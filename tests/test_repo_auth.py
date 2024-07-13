

import unittest

from datetime import datetime, timedelta
from jose import jwt, JWTError
from unittest.mock import Mock, patch

from repository.auth  import Hash, create_access_token, create_refresh_token, get_email_form_refresh_token, get_current_user
from settings import SECRET_KEY, ALGORITHM
from database.models import User
from fastapi import HTTPException
from sqlalchemy.orm import Session




class TestHash(unittest.TestCase):
    def setUp(self):
        self.hash_util = Hash()
        self.password = "password123"
        self.hashed_password = self.hash_util.get_password_hash(self.password)

    def test_verify_password(self):
        self.assertTrue(self.hash_util.verify_password(self.password, self.hashed_password))
        self.assertFalse(self.hash_util.verify_password("wrongpassword", self.hashed_password))

    def test_get_password_hash(self):
        hashed_password = self.hash_util.get_password_hash(self.password)
        self.assertNotEqual(hashed_password, self.password)


class TestTokenFunctions(unittest.TestCase):
    def test_create_access_token(self):
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        self.assertEqual(decoded_token["sub"], "test@example.com")
        self.assertEqual(decoded_token["scope"], "access_token")

    def test_create_refresh_token(self):
        data = {"sub": "test@example.com"}
        token = create_refresh_token(data)
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        self.assertEqual(decoded_token["sub"], "test@example.com")
        self.assertEqual(decoded_token["scope"], "refresh_token")

    def test_get_email_form_refresh_token(self):
        data = {"sub": "test@example.com"}
        token = create_refresh_token(data)
        email = get_email_form_refresh_token(token)
        self.assertEqual(email, "test@example.com")

        with self.assertRaises(HTTPException):
            get_email_form_refresh_token("invalid.token.here")


class TestGetCurrentUser(unittest.IsolatedAsyncioTestCase):
    @patch("database.db.get_db", return_value=Mock(spec=Session))
    @patch("settings.oauth2_scheme", return_value="token")
    async def test_get_current_user(self, mock_oauth2_scheme, mock_get_db):
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        mock_user = Mock(spec=User)
        mock_user.email = "test@example.com"
        
        mock_db = mock_get_db.return_value
        mock_db.query().filter().first.return_value = mock_user

        user = await get_current_user(token, mock_db)
        self.assertEqual(user.email, "test@example.com")

        # Test expired token
        expired_token = create_access_token(data, expires_delta=-10)
        with self.assertRaises(HTTPException):
            await get_current_user(expired_token, mock_db)

        # Test invalid token
        with self.assertRaises(HTTPException):
            await get_current_user("invalid.token.here", mock_db)


if __name__ == '__main__':
    unittest.main()