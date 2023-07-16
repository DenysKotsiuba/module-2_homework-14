from sqlalchemy.orm import Session
from sqlalchemy import and_

from datetime import date

from src.database.db import get_db
from src.database.models import Contact, User
from src.schemas.contacts import ContactModel


async def get_contacts(limit: int, offset: int, user: User, db: Session):
    """
    The get_contacts function returns a list of contacts for the user.
    
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip before starting to return rows
    :param user: User: Get the user's id
    :param db: Session: Access the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(user_id=user.id).order_by(Contact.id).limit(limit).offset(offset).all()
    return contacts


async def get_contact_by_id(contact_id: int, user: User, db: Session):
    """
    The get_contact_by_id function takes in a contact_id and user, and returns the contact with that id.
    If no such contact exists, it raises an HTTPException.
    
    :param contact_id: int: Specify the contact id that we want to retrieve
    :param user: User: Get the user's id
    :param db: Session: Pass the database session to the function
    :return: A contact
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    return contact


async def get_contact_by_first_name(contact_first_name: str, user: User, db: Session):
    """
    The get_contact_by_first_name function takes a contact_first_name and user as input,
    and returns the first Contact object in the database that matches both of these inputs.
    If no such Contact exists, an HTTPException is raised.
    
    :param contact_first_name: str: Specify the first name of the contact to be retrieved
    :param user: User: Get the user's id from the database
    :param db: Session: Pass in the database session
    :return: The first contact found with the given first name
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.first_name==contact_first_name)).first()
    return contact


async def get_contact_by_last_name(contact_last_name: str, user: User, db: Session):
    """
    The get_contact_by_last_name function returns a contact object from the database.
    
    :param contact_last_name: str: Filter the database query by last name
    :param user: User: Ensure that the user is authenticated and authorized to access the endpoint
    :param db: Session: Access the database
    :return: The contact object that has the same last name as the one passed in
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.last_name==contact_last_name)).first()
    return contact


async def get_contact_by_email(contact_email: str, user: User, db: Session):
    """
    The get_contact_by_email function takes in a contact_email and user, and returns the contact with that email.
    If no such contact exists, it raises an HTTPException.
    
    :param contact_email: str: Specify the email of the contact to be retrieved
    :param user: User: Get the user_id from the database
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.email==contact_email)).first()
    return contact


async def get_week_birthday_people(user: User, db: Session):
    """
    The get_week_birthday_people function returns a list of contacts whose birthdays are in the next week.
    
    :param user: User: Get the user's id from the database
    :param db: Session: Connect to the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    birthday_people = []

    today = date.today()
    week = [date(year=today.year, month=today.month, day=today.day+num) for num in range(7)]

    objs = db.query(Contact).filter_by(user_id=user.id).all()

    if objs:
        for obj in objs:
            this_year_birthday = obj.birth_date.replace(year=today.year)

            if this_year_birthday in week:
                birthday_people.append(obj)
    return birthday_people


async def create_contact(body: ContactModel, user: User, db: Session):
    """
    The create_contact function creates a new contact in the database.
    
    :param body: ContactModel: Get the data from the request body
    :param user: User: Get the user id from the token
    :param db: Session: Access the database
    :return: The contact object that was created
    :doc-author: Trelent
    """
    contact = Contact(**body.dict(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact
    

async def update_contact(body: ContactModel, contact_id: int, user: User, db: Session):
    """
    The update_contact function updates a contact in the database.
        Args:
            body (ContactModel): The new contact information to be updated.
            user (User): The current user making the request.
            db (Session, optional): An open database session for querying and updating contacts. Defaults to None, which will create a new session if one is not provided by the caller of this function.
    
    :param body: ContactModel: Pass the contact data to the function
    :param contact_id: int: Identify the contact to delete
    :param user: User: Get the user_id from the database
    :param db: Session: Access the database
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    
    if contact is None:
        return None
    
    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.email = body.email
    contact.phone = body.phone
    contact.birth_date = body.birth_date
    contact.additional_data = body.additional_data

    db.commit()

    return contact


async def remove_contact(contact_id: int, user: User, db: Session):
    """
    The remove_contact function removes a contact from the database.
    
    :param contact_id: int: Specify the contact to be removed
    :param user: User: Identify the user who is making the request
    :param db: Session: Access the database
    :return: A 204 status code, which means that the request was successful but there is no content to return
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()

    if contact is None:
        return None
    
    db.delete(contact)
    db.commit()
    
    return contact
