from sqlalchemy.orm import Session
from database.models import Contact
from shemas import ContactAdd, ContactUpdate, ContactBase

from datetime import date, timedelta


def search_contact(db: Session, user_id: int, contact_id: int = None, contact_firstname: str = None, contact_lastname: str = None, contact_email: str = None):
    """
    Search for a contact by specified criteria.

    :param db: Database session.
    :param user_id: ID of the user who created the contact.
    :param contact_id: Contact ID (optional).
    :param contact_firstname: Contact's first name (optional).
    :param contact_lastname: Contact's last name (optional).
    :param contact_email: Contact's email (optional).
    :return: The first found contact or None.
    """
    if contact_firstname:
        return db.query(Contact).filter(Contact.firstname == contact_firstname, Contact.created_by_id == user_id).first()
    
    elif contact_lastname:
        return db.query(Contact).filter(Contact.lastname == contact_lastname, Contact.created_by_id == user_id).first()

    elif contact_id:
        return db.query(Contact).filter(Contact.id == contact_id, Contact.created_by_id == user_id).first()
    
    elif contact_email:
        return db.query(Contact).filter(Contact.email == contact_email, Contact.created_by_id == user_id).first()


def all_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """
    Retrieve all contacts of a user with pagination.

    :param db: Database session.
    :param user_id: ID of the user who created the contact.
    :param skip: Number of contacts to skip (optional).
    :param limit: Maximum number of contacts to return (optional).
    :return: List of contacts.
    """
    return db.query(Contact).filter(Contact.created_by_id == user_id).offset(skip).limit(limit).all()


def add_contact(db: Session, contact: ContactAdd,  user_id: int):
    """
    Add a new contact.

    :param db: Database session.
    :param contact: Data of the new contact.
    :param user_id: ID of the user who created the contact.
    :return: The created contact.
    """
    db_contact = Contact(**contact.model_dump(), created_by_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def update_contact(db: Session, user_id: int, contact_id: int, contact: ContactUpdate):
    """
    Update an existing contact.

    :param db: Database session.
    :param contact_id: ID of the contact to update.
    :param contact: Data for updating the contact.
    :return: The updated contact or None if the contact was not found.
    """
    db_contact = search_contact(db, user_id=user_id, contact_id=contact_id)

    if db_contact:

        for key, value in contact.dict(exclude_unset=True).items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact


def del_contact(db: Session,  user_id: int, contact_id: int):
    """
    Delete a contact.

    :param db: Database session.
    :param contact_id: ID of the contact to delete.
    :return: The deleted contact or None if the contact was not found.
    """
    db_contact = search_contact(db,  user_id=user_id, contact_id=contact_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact


def search_born_date(db: Session, user_id: int, born_date: date):
    """
    Search for contacts by birthdate.

    :param db: Database session.
    :param user_id: ID of the user who created the contact.
    :param born_date: Birthdate for the search.
    :return: List of contacts that match the criteria.
    """
    return db.query(Contact).filter(Contact.born_date == born_date, Contact.created_by_id == user_id).all()

def search_born_date_7days(db: Session, user_id: int,):
    """
    Search for contacts whose birthdays are within the next 7 days.

    :param db: Database session.
    :param user_id: ID of the user who created the contact.
    :return: List of contacts that match the criteria.
    """
    today = date.today()
    last_date = today + timedelta(days=7)
    return db.query(Contact).filter(Contact.born_date >= today, Contact.born_date <= last_date, Contact.created_by_id == user_id).all()
