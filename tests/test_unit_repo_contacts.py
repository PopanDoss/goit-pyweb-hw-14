import unittest
from datetime import date, timedelta
from unittest.mock import Mock
from sqlalchemy.orm import Session
from Lab_11.database.models import Contact
from Lab_11.repository.contacts_crud import search_contact, all_contacts, add_contact, update_contact, del_contact, search_born_date, search_born_date_7days
from Lab_11.shemas import ContactAdd, ContactUpdate

class TestSearchContact(unittest.TestCase):
    def setUp(self):
        self.db = Mock(spec=Session)
        self.user_id = 1

    def test_search_by_firstname(self):
        mock_contact = Contact(firstname="John", created_by_id=self.user_id)
        self.db.query.return_value.filter.return_value.first.return_value = mock_contact

        result = search_contact(self.db, self.user_id, contact_firstname="John")
        self.assertEqual(result.firstname, "John")

    def test_search_by_lastname(self):
        mock_contact = Contact(lastname="Doe", created_by_id=self.user_id)
        self.db.query.return_value.filter.return_value.first.return_value = mock_contact

        result = search_contact(self.db, self.user_id, contact_lastname="Doe")
        self.assertEqual(result.lastname, "Doe")

    def test_search_by_id(self):
        mock_contact = Contact(id=1, created_by_id=self.user_id)
        self.db.query.return_value.filter.return_value.first.return_value = mock_contact

        result = search_contact(self.db, self.user_id, contact_id=1)
        self.assertEqual(result.id, 1)

    def test_search_by_email(self):
        mock_contact = Contact(email="john.doe@example.com", created_by_id=self.user_id)
        self.db.query.return_value.filter.return_value.first.return_value = mock_contact

        result = search_contact(self.db, self.user_id, contact_email="john.doe@example.com")
        self.assertEqual(result.email, "john.doe@example.com")

    def test_search_no_match(self):
        self.db.query.return_value.filter.return_value.first.return_value = None

        result = search_contact(self.db, self.user_id, contact_firstname="Jane")
        self.assertIsNone(result)

class TestAllContacts(unittest.TestCase):
    def setUp(self):
        self.db = Mock(spec=Session)
        self.user_id = 1

    def test_all_contacts(self):
        mock_contacts = [Contact(id=i, created_by_id=self.user_id) for i in range(10)]
        self.db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_contacts

        results = all_contacts(self.db, self.user_id)
        self.assertEqual(len(results), 10)

class TestAddContact(unittest.TestCase):
    def setUp(self):
        self.db = Mock(spec=Session)
        self.user_id = 1
        self.contact_data = ContactAdd(firstname="John", lastname="Doe", email="john.doe@example.com", phone_number="432432", born_date="2024-07-13")

    def test_add_contact(self):
        new_contact = add_contact(self.db, self.contact_data, self.user_id)
        self.assertEqual(new_contact.firstname, "John")
        self.assertEqual(new_contact.lastname, "Doe")
        self.assertEqual(new_contact.email, "john.doe@example.com")
        self.assertEqual(new_contact.phone_number, "432432")
        self.assertEqual(str(new_contact.born_date), "2024-07-13")

class TestUpdateContact(unittest.TestCase):
    def setUp(self):
        self.db = Mock(spec=Session)
        self.user_id = 1
        self.contact_id = 1
        self.contact_data = ContactUpdate(firstname="Jane", lastname="Doe", email="jane.doe@example.com", phone_number="1234567890", born_date=date(1990, 1, 1))

    def test_update_contact(self):
        mock_contact = Contact(id=self.contact_id, firstname="John")
        self.db.query.return_value.filter.return_value.first.return_value = mock_contact

        updated_contact = update_contact(self.db, self.user_id, self.contact_id, self.contact_data)  # Додано self.user_id
        self.assertEqual(updated_contact.firstname, "Jane")

    def test_update_contact_not_found(self):
        self.db.query.return_value.filter.return_value.first.return_value = None

        updated_contact = update_contact(self.db, self.user_id, self.contact_id, self.contact_data)  # Додано self.user_id
        self.assertIsNone(updated_contact)

class TestDeleteContact(unittest.TestCase):
    def setUp(self):
        self.db = Mock(spec=Session)
        self.user_id = 1
        self.contact_id = 1

    def test_delete_contact(self):
        mock_contact = Contact(id=self.contact_id)
        self.db.query.return_value.filter.return_value.first.return_value = mock_contact

        deleted_contact = del_contact(self.db, self.user_id, self.contact_id)  # Додано self.user_id
        self.assertEqual(deleted_contact.id, self.contact_id)

    def test_delete_contact_not_found(self):
        self.db.query.return_value.filter.return_value.first.return_value = None

        deleted_contact = del_contact(self.db, self.user_id, self.contact_id)  # Додано self.user_id
        self.assertIsNone(deleted_contact)

class TestSearchBornDate(unittest.TestCase):
    def setUp(self):
        self.db = Mock(spec=Session)
        self.user_id = 1
        self.born_date = date(1990, 1, 1)

    def test_search_born_date(self):
        mock_contacts = [Contact(born_date=self.born_date, created_by_id=self.user_id) for _ in range(5)]
        self.db.query.return_value.filter.return_value.all.return_value = mock_contacts

        results = search_born_date(self.db, self.user_id, self.born_date)
        self.assertEqual(len(results), 5)

class TestSearchBornDate7Days(unittest.TestCase):
    def setUp(self):
        self.db = Mock(spec=Session)
        self.user_id = 1

    def test_search_born_date_7days(self):
        mock_contacts = [Contact(born_date=date.today() + timedelta(days=i), created_by_id=self.user_id) for i in range(7)]
        self.db.query.return_value.filter.return_value.all.return_value = mock_contacts

        results = search_born_date_7days(self.db, self.user_id)
        self.assertEqual(len(results), 7)

if __name__ == '__main__':
    unittest.main()