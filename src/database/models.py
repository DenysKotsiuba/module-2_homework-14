from sqlalchemy import Column, ForeignKey, Boolean, Date, DateTime, Integer, String, func, event
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    create_at = Column(DateTime, server_default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, server_default="False", nullable=False)
    contacts = relationship("Contact", backref="user")


class Contact(Base):
    __tablename__ = "Contacts"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    phone = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    additional_data = Column(String, default=None)
    create_at = Column(DateTime, server_default=func.now())
    update_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"), server_default="4", nullable=False)







