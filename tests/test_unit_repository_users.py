import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.repository import users as users_repository
from src.database.models import Contact, User
from src.schemas.users import UserModel


class TestRepositoryContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, email="test@test.ua")
        self.contact = Contact(id=1)

    async def test_get_user_by_email(self):
        self.session.query(User).filter_by().first.return_value = self.user
        result = await users_repository.get_user_by_email("test@test.ua", self.session)
        self.assertEqual(result, self.user)

    async def test_create_user(self):
        body = UserModel(
            username="test",
            email="test@test.ua",
            password="test",
        )
        result = await users_repository.create_user(body, self.session)
        self.assertTrue(hasattr(result, "id"))
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)

    async def test_update_token(self):
        token = "test_token"
        result = await users_repository.update_token(self.user, token, self.session)
        self.assertEqual(result.refresh_token, token)

    async def test_confirm_email(self):
        result = await users_repository.confirm_email(self.user, self.session)
        self.assertTrue(result.confirmed)

    async def test_update_avatar(self):
        url = "test_url"
        result = await users_repository.update_avatar(self.user.email, url, self.session)
        self.assertEqual(result.avatar, url)