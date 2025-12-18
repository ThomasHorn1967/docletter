from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


class User(Base):
    """
    User model with API key authentication.
    The api_key is stored hashed for security
    """
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False)
    hashed_api_key: Mapped[str] = mapped_column(String, nullable=False)
    key_expires: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now() + timedelta(days=365))
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)


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
