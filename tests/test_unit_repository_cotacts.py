import unittest
from unittest.mock import MagicMock
from datetime import date

from sqlalchemy.orm import Session

from src.repository import contacts as contacts_repository
from src.database.models import Contact, User
from src.schemas.contacts import ContactModel


class TestRepositoryContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.contact = Contact(id=1)

    async def test_get_contacts(self):
        contacts = [self.contact, self.contact, self.contact]
        self.session.query().filter_by().order_by().limit().offset().all.return_value = contacts
        result = await contacts_repository.get_contacts(10, 0, self.user, self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_by_id(self):
        self.session.query().filter().first.return_value = self.contact
        result = await contacts_repository.get_contact_by_id(1, self.user, self.session)
        self.assertEqual(result, self.contact)

    async def test_get_contact_by_id_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await contacts_repository.get_contact_by_id(1, self.user, self.session)
        self.assertIsNone(result)

    async def test_get_contact_by_first_name(self):
        self.session.query().filter().first.return_value = self.contact
        result = await contacts_repository.get_contact_by_first_name("test", self.user, self.session)
        self.assertEqual(result, self.contact)

    async def test_get_contact_by_first_name_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await contacts_repository.get_contact_by_first_name("test", self.user, self.session)
        self.assertIsNone(result)

    async def test_get_contact_by_last_name(self):
        self.session.query().filter().first.return_value = self.contact
        result = await contacts_repository.get_contact_by_last_name("test", self.user, self.session)
        self.assertEqual(result, self.contact)

    async def test_get_contact_by_last_name_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await contacts_repository.get_contact_by_last_name("test", self.user, self.session)
        self.assertIsNone(result)

    async def test_get_contact_by_email(self):
        self.session.query().filter().first.return_value = self.contact
        result = await contacts_repository.get_contact_by_email("test@test.ua", self.user, self.session)
        self.assertEqual(result, self.contact)

    async def test_get_contact_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await contacts_repository.get_contact_by_email("test", self.user, self.session)
        self.assertIsNone(result)

    async def test_get_week_birthday_people(self):
        today = date.today()
        contacts = [
            Contact(birth_date=today), 
            Contact(birth_date=today.replace(day=today.day+8))
            ]
        self.session.query(Contact).filter_by().all.return_value = contacts
        result = await contacts_repository.get_week_birthday_people(self.user, self.session)
        self.assertEqual(result[0].birth_date, contacts[0].birth_date)
        self.assertEqual(len(result), 1)

    async def test_create_contact(self):
        body = ContactModel(
            first_name = "test",
            last_name = "test",
            email = "test@test.ua",
            phone = "+380(63)111-11-11",
            birth_date = date.today(),
            additional_data = None,
        )        
        result = await contacts_repository.create_contact(body, self.user, self.session)
        self.assertTrue(hasattr(result, "id"))
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birth_date, body.birth_date)
        self.assertEqual(result.additional_data, body.additional_data)
        self.assertEqual(result.user_id, self.user.id)

    async def test_update_contact(self):
        body = ContactModel(
            first_name = "test",
            last_name = "test",
            email = "test@test.ua",
            phone = "+380(63)111-11-11",
            birth_date = date.today(),
            additional_data = None,
        )
        self.session.query(Contact).filter().first.return_value = self.contact
        result = await contacts_repository.update_contact(body, self.contact.id, self.user, self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birth_date, body.birth_date)
        self.assertEqual(result.additional_data, body.additional_data)

    async def test_update_contact_not_found(self):
        self.session.query(Contact).filter().first.return_value = None
        result = await contacts_repository.update_contact(None, self.contact.id, self.user, self.session)
        self.assertIsNone(result)

    async def test_remove_contact(self):
        self.session.query(Contact).filter().first.return_value = self.contact
        result = await contacts_repository.remove_contact(self.contact.id, self.user, self.session)
        self.assertEqual(result.id, self.contact.id)

    async def test_remove_contact_not_found(self):
        self.session.query(Contact).filter().first.return_value = None
        result = await contacts_repository.remove_contact(self.contact.id, self.user, self.session)
        self.assertIsNone(result)

