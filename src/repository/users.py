from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session
from libgravatar import Gravatar

from src.database.db import get_db
from src.database.redis_db import get_async_redis_client
from src.database.models import User
from src.schemas.users import UserModel



async def get_user_by_email(email: EmailStr, db: Session):
    """
    The get_user_by_email function takes an email address and a database session,
    and returns the user object associated with that email address. If no such user
    exists, it returns None.
    
    :param email: EmailStr: Validate the email address
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    user = db.query(User).filter_by(email=email).first()
    return user


async def create_user(body: UserModel, db: Session):
    """
    The create_user function creates a new user in the database.
    
    :param body: UserModel: Parse the request body into a usermodel object
    :param db: Session: Get the database session
    :return: A user object
    :doc-author: Trelent
    """
    avatar = None

    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)

    user = User(**body.dict(), avatar=avatar)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def update_token(user: User, token: str | None, db: Session = Depends(get_db)):
    """
    The update_token function updates the refresh token for a user.
    
    :param user: User: Get the user from the database
    :param token: str | None: Set the refresh token for a user
    :param db: Session: Pass the database session to the function
    :return: The user object
    :doc-author: Trelent
    """
    user.refresh_token = token
    db.commit()

    return user


async def confirm_email(user: User, db: Session) -> None:
    """
    The confirme_email function takes an email address and a database session as arguments.
    It then uses the get_user_by_email function to retrieve the user with that email address from the database.
    The confirme_email function then sets that user's confirmed field to True, and commits this change to the database.
    
    :param email: str: Get the user's email address
    :param db: Session: Access the database
    :return: None
    :doc-author: Trelent
    """
    user.confirmed = True
    db.commit()

    return user


async def update_avatar(email: EmailStr, url: str, db: Session) -> User:
    """
    The update_avatar function takes an email and a url as arguments.
    It then uses the get_user_by_email function to retrieve the user from the database.
    The avatar attribute of that user is set to be equal to the url argument, and then 
    the db session is committed so that this change will persist in our database. 
    Finally, we use get_async_redis_client() to create a redis client object which we can use 
    to delete any cached data for this particular user.
    
    :param email: Get the user from the database
    :param url: str: Specify the type of the url parameter
    :param db: Session: Get the database session
    :return: The updated user
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    redis_client = await get_async_redis_client()
    await redis_client.delete(f"user:{user.email}")
    return user