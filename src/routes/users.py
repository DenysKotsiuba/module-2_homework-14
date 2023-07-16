from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository.users import update_avatar
from src.services.auth import auth_service
from src.schemas.users import UserDB

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserDB, 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_users_me(user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function is a GET request that returns the current user's information.
        The function takes in an optional parameter, user, which is of type User and depends on the auth_service.get_current_user function to return a valid User object.
    
    :param user: User: Specify that the function expects a user object
    :return: The current user
    :doc-author: Trelent
    """
    return user


@router.patch('/avatar', response_model=UserDB)
async def update_avatar_user(file: UploadFile = File(), user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    The update_avatar_user function takes in a file and user, then uploads the file to cloudinary.
    It returns the updated user with their new avatar.
    
    :param file: UploadFile: Upload the file to cloudinary
    :param user: User: Get the user object from the database
    :param db: Session: Access the database
    :return: A user object
    :doc-author: Trelent
    """
    cloudinary.config(
        cloud_name="dqstgqoym",
        api_key="356476759363581",
        api_secret="Wg3N4UJiykX6kL7227A_WXk8WvM",
        secure=True
    )

    public_id = f"m-2_hw-13/{user.email}"
    r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    src_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop='fill', version=r.get('version'))
    updated_user = await update_avatar(user.email, src_url, db)
    return updated_user