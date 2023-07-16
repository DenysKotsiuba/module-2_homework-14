from fastapi import Depends, status, Path, Query, APIRouter, HTTPException
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from sqlalchemy import and_

from typing import List

from src.database.db import get_db
from src.database.models import User
from src.schemas.contacts import ContactModel, ContactResponseModel
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service


router = APIRouter(prefix="/contacts", tags=["contacts"])    

@router.get("/", response_model=List[ContactResponseModel], 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contacts(limit: int = Query(10, le=100), skip: int = 0, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The get_contacts function returns a list of contacts.
    
    :param limit: int: Limit the number of contacts returned
    :param le: Limit the number of contacts returned
    :param skip: int: Skip a certain number of contacts from the database
    :param user: User: Get the current user from the database
    :param db: Session: Get a database session
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts(limit, skip, user, db)
    return contacts


@router.get("/week_birthday_people", response_model=List[ContactResponseModel], 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_week_birthday_people(user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The get_week_birthday_people function returns a list of contacts that have birthdays in the next week.
    
    
    :param user: User: Get the user from the database
    :param db: Session: Get the database session
    :return: A list of contacts that have their birthday in the next week
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_week_birthday_people(user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponseModel, 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact_by_id(contact_id: int = Path(ge=1), user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The get_contact_by_id function returns a contact by its id.
    
    :param contact_id: int: Get the contact id from the url
    :param user: User: Get the current user
    :param db: Session: Get the database session
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_id(contact_id, user, db)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return contact


@router.get("/first_name/{contact_first_name}", response_model=ContactResponseModel, 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact_by_first_name(contact_first_name, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The get_contact_by_first_name function returns a contact by first name.
    
    :param contact_first_name: Get the contact by first name
    :param user: User: Get the current user from the auth_service
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_first_name(contact_first_name, user, db)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return contact


@router.get("/last_name/{contact_last_name}", response_model=ContactResponseModel, 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact_by_last_name(contact_last_name, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The get_contact_by_last_name function returns a contact by last name.
    
    :param contact_last_name: Get a contact by the last name
    :param user: User: Get the current user from the auth_service
    :param db: Session: Pass the database session to the function
    :return: A contact by the last name
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_last_name(contact_last_name, user, db)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return contact


@router.get("/email/{contact_email}", response_model=ContactResponseModel, 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact_by_email(contact_email, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The get_contact_by_email function returns a contact by email.
    
    :param contact_email: Find the contact by email
    :param user: User: Get the current user
    :param db: Session: Pass the database session to the repository layer
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_email(contact_email, user, db)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return contact


@router.post("/", response_model=ContactResponseModel, status_code=status.HTTP_201_CREATED, 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_contact(body: ContactModel, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The create_contact function creates a new contact in the database.
    
    :param body: ContactModel: Get the body of the request, which is a contactmodel object
    :param user: User: Get the user from the auth_service
    :param db: Session: Pass the database session to the repository layer
    :return: A contactmodel object
    :doc-author: Trelent
    """
    contact = await repository_contacts.create_contact(body, user, db)

    return contact
    

@router.put("/{contact_id}", response_model=ContactResponseModel, 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_contact(body: ContactModel, contact_id: int, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The update_contact function updates a contact in the database.
        The function takes a ContactModel object as input, and returns an updated ContactResponseModel object.
    
    
    :param body: ContactModel: Get the data from the request body
    :param contact_id: int: Identify the contact that will be deleted
    :param user: User: Get the current user
    :param db: Session: Pass the database session to the repository
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(body, contact_id, user, db)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def remove_contact(contact_id: int, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The remove_contact function removes a contact from the database.
        The function takes in an integer, contact_id, and uses it to find the correct row in the contacts table of our database.
        It then deletes that row from our contacts table.
    
    :param contact_id: int: Specify the contact to be removed
    :param user: User: Get the current user
    :param db: Session: Access the database
    :return: A 204 status code, which means that the request was successful but there is no content to return
    :doc-author: Trelent
    """
    contact = await repository_contacts.remove_contact(contact_id, user, db)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
