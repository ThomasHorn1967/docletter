from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """
    User model with API key authentication.
    The api_key is stored hashed for security
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_api_key = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.now())
    is_valid = Column(Boolean, default=True)


class Message(Base):
    """
    Simple message model for demonstration.
    Each message is owned by a user (enforced through foreign key).
    """
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.now())
