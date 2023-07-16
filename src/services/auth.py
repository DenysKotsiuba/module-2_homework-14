from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError

from datetime import datetime, timedelta
import pickle

from src.database.db import get_db
from src.database.redis_db import get_async_redis_client
from src.repository.users import get_user_by_email


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = "3efdb0bd9fef572516d19aa6bff146e264708df086a559230cf358ebee036172"
    ALGORITHM = "HS256"
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

    def get_hashed_password(self, password: str):
        """
        The get_hashed_password function takes a password as an argument and returns the hashed version of that password.
        The hashing is done using the CryptContext object, which was initialized in __init__.py.
        
        :param self: Represent the instance of the class
        :param password: str: Get the password from the user
        :return: The hashed password
        :doc-author: Trelent
        """
        hashed_password = self.pwd_context.hash(password)
        return hashed_password

    def verify_password(self, password, hashed_password):
        """
        The verify_password function takes a password and hashed_password as arguments.
        It then uses the verify method of the pwd_context object to check if the password matches
        the hash. If it does, it returns True, otherwise False.
        
        :param self: Refer to the class itself
        :param password: Verify the password that is being passed in
        :param hashed_password: Compare the password that is being entered by the user to what is stored in the database
        :return: A boolean value
        :doc-author: Trelent
        """
        verify = self.pwd_context.verify(password, hashed_password)
        return verify

    def create_access_token(self, data: dict):
        """
        The create_access_token function creates an access token for the user.
            The function takes in a dictionary of data, which is used to create the JWT payload.
            The current time and expiration time are added to the payload as well as a scope value of &quot;access token&quot;.
            Finally, we encode this information using our secret key and algorithm.
        
        :param self: Represent the instance of a class
        :param data: dict: Pass the user's data to the function
        :return: A token that is encoded using the jwt library
        :doc-author: Trelent
        """
        to_encode = data.copy()
        current_time = datetime.utcnow()
        expire = current_time + timedelta(minutes=15)
        scope = "access token"
        to_encode.update({"iat": current_time, "exp": expire, "scope": scope})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)
        return encoded_access_token

    def create_refresh_token(self, data: dict):
        """
        The create_refresh_token function creates a refresh token for the user.
            The function takes in a dictionary of data, and then encodes it into a JWT.
            The encoded JWT is returned to the caller.
        
        :param self: Represent the instance of the class
        :param data: dict: Pass in the data that will be encoded into the token
        :return: A refresh token that is encoded with the jwt library
        :doc-author: Trelent
        """
        to_encode = data.copy()
        current_time = datetime.utcnow()
        expire = current_time + timedelta(days=7)
        scope = "refresh token"
        to_encode.update({"iat": current_time, "exp": expire, "scope": scope})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)
        return encoded_access_token
    
    def create_email_token(self, data: dict):
        """
        The create_email_token function creates a JWT token that is used to verify the user's email address.
        The token contains the following information:
        - iat (issued at): The time when the token was created.
        - exp (expiration): The time when this token will expire and no longer be valid. This is set to 7 days from creation date/time. 
        - scope: A string indicating what this JWT can be used for, in this case &quot;email_token&quot;. 
        
        :param self: Make the function a method of the class
        :param data: dict: Store the user's email address
        :return: An encoded email token
        :doc-author: Trelent
        """
        to_encode = data.copy()
        current_time = datetime.utcnow()
        expire = current_time + timedelta(days=7)
        scope = "email token"
        to_encode.update({"iat": current_time, "exp": expire, "scope": scope})
        encoded_email_token = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)
        return encoded_email_token

    def decode_refresh_token(self, token: str):
        """
        The decode_refresh_token function is used to decode the refresh token that was sent by the client.
        The function first tries to decode the token using jwt.decode(). If it fails, an HTTPException is raised with a status code of 401 and a detail message of &quot;Could not validate credentials&quot;.
        If decoding succeeds, then we check if the scope for this token is &quot;refresh_token&quot;. If it isn't, then we raise an HTTPException with a status code of 401 and a detail message of &quot;Invalid scope for token&quot;.
        If everything checks out so far, then we return email from payload.
        
        :param self: Represent the instance of the class
        :param token: str: Pass the token to be decoded
        :return: The email of the user who is requesting a new access token
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)

            if payload.get("scope") == "refresh token":
                email = payload.get("sub")
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email associated with that token.
        It does this by decoding the JWT, checking to make sure it is an email verification token, and then returning the 
        email address associated with that user.
        
        :param self: Represent the instance of the class
        :param token: str: Pass in the token that is sent to the user's email
        :return: The email associated with the token
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)

            if payload.get("scope") == "email token":
                email = payload.get("sub")
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=f"{e}\nInvalid token for email verification")

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        The get_current_user function is a dependency that can be used to get the current user.
        It will check if the token provided in the Authorization header is valid and return an object of type User.
        If no token was provided, it will raise an HTTPException with status code 401 (Unauthorized).
        
        
        :param self: Refer to the class itself
        :param token: str: Get the token from the authorization header
        :param db: Session: Get the database session
        :return: The user object associated with the access token
        :doc-author: Trelent
        """
        credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                          detail="Could not validate credentials", 
                                          headers={"WWW-Authenticate": "Bearer"})

        try:
            payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)

            if payload.get("scope") == "access token":
                email = payload.get("sub")

                if email is None:
                    raise credentials_exception
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except JWTError:
            raise credentials_exception
        
        redis_client = await get_async_redis_client()
        user = await redis_client.get(f"user:{email}")
        if user is None:
            user = await get_user_by_email(email, db)
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User doesn't exist")
            await redis_client.set(f"user:{email}", pickle.dumps(user))
            await redis_client.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user
    

auth_service = Auth()
