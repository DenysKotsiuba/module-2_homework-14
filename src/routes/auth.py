from fastapi import APIRouter, Depends, status, HTTPException, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.users import UserModel, UserResponseModel, TokenResponseModel, RequestEmail
from src.repository.users import create_user, get_user_by_email, update_token, confirm_email
from src.services.auth import auth_service
from src.services.email import send_email


router = APIRouter(prefix="/auth", tags=["Auth"])

security = HTTPBearer()


@router.post("/signup", response_model=UserResponseModel, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    The signup function creates a new user in the database.
        It takes a UserModel object as input, and returns an HTTP response with the created user's information.
        If there is already an account associated with that email address, it will return a 409 Conflict error.
    
    :param body: UserModel: Get the data from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :return: A dictionary with the user and a detail message
    :doc-author: Trelent
    """
    exist_user = await get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_hashed_password(body.password)
    user = await create_user(body, db)
    background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"user": user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenResponseModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.
        It takes in the username and password of the user, and returns an access token if successful.
    
    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Pass the database session to the function
    :return: A dict with the access_token, refresh_token and token type
    :doc-author: Trelent
    """
    user = await get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    access_token = auth_service.create_access_token({"sub": body.username})
    refresh_token = auth_service.create_refresh_token({"sub": body.username})
    await update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/refresh_token", response_model=TokenResponseModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns an access token.
    
    
    :param credentials: HTTPAuthorizationCredentials: Get the access token from the request header
    :param db: Session: Get the database session
    :return: A dict containing the new access_token, refresh_token and token type
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = auth_service.decode_refresh_token(token)
    user = await get_user_by_email(email, db)

    if token != user.refresh_token:
        await update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    access_token = auth_service.create_access_token({"sub": email})
    refresh_token = auth_service.create_refresh_token({"sub": email})
    await update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    The request_email function is used to request a confirmation email for the user's account.
        The function takes in an email address and sends a confirmation link to that address.
        If the user has already confirmed their account, they will be notified of this.
    
    :param body: RequestEmail: Validate the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the server
    :param db: Session: Pass the database session to the function
    :return: A message to the user
    :doc-author: Trelent
    """
    user = await get_user_by_email(body.email, db)

    if user and user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation"}


@router.get('/confirmed_email/{email_token}')
async def confirmed_email(email_token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function takes an email token and a database connection.
    It then gets the email from the token, gets the user with that email, checks if they exist,
    and if they do it confirms their account.
    
    :param email_token: str: Get the email from the token
    :param db: Session: Pass the database session to the function
    :return: A message that email is confirmed
    :doc-author: Trelent
    """
    email = auth_service.get_email_from_token(email_token)
    user = await get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await confirm_email(user, db)
    return {"message": "Email confirmed"}