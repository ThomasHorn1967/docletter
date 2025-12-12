import secrets
import bcrypt
from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Annotated
from database import get_db
from models import User
from datetime import datetime, timezone


def generate_api_key() -> str:
    """
    Generate a cryptographically secure random API key.
    """
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key using bcrypt.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(api_key.encode('utf-8'), salt).decode('utf-8')


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """
    Verify a plain API key against its hashed version.
    """
    return bcrypt.checkpw(plain_key.encode('utf-8'), hashed_key.encode('utf-8'))


async def get_current_user(
    x_api_key: Annotated[str, Header()],
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency function that validates the API key and returns the current user.
    """
    # Query active users only
    try:
        users = db.query(User).filter(User.is_valid == True).all()
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )
        # Check the provided API key against each user's hashed key
        for user in users:
            if verify_api_key(x_api_key, user.hashed_api_key):
                # check if the key is expired:
                if user.key_expires <= datetime.now():
                    raise exception
                return user

        # No matching user found - authentication failed
        raise exception
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"A Database error occured: {e}")
