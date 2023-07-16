from fastapi import HTTPException, status

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
from os import environ, getenv

from src.conf.config import settings

load_dotenv()

url = settings.sqlalchemy_database_url
engine = create_engine(url)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = Session()

    try:
        yield db
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    finally:
        db.close()