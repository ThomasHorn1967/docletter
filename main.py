from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from database import get_db, engine
from models import Base, User, Message
import schemas
import auth
from datetime import datetime
import models
from dotenv import load_dotenv
import os
load_dotenv()
INITIAL_KEY = os.getenv("INITIAL_KEY")


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Key Authentication Demo", version="1.0.0")

# Type aliases for cleaner code
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(auth.get_current_user)]

# ============= Public Endpoints =============


@app.post("/users", response_model=schemas.UserCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: DBSession):
    """
    Create a new user and generate their API key.
    """
    # Check if username already exists
    existing_user = db.query(User).filter(
        User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    if user.api_key != INITIAL_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Initial key missing or wrong")
    # Generate a new API key and hash it
    plain_api_key = auth.generate_api_key()
    hashed_key = auth.hash_api_key(plain_api_key)

    # Create the user with hashed key
    db_user = User(
        email=user.email,
        hashed_api_key=hashed_key
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    # Return the user info AND the plain API key (only time we do this)
    output = schemas.UserCreatedResponse(
        email=db_user.email,
        api_key=plain_api_key,
    )
    return output


@app.get("/")
async def root():
    """Public endpoint - no authentication required"""
    return {
        "message": "API Key Authentication Demo",
        "docs": "/docs",
        "instructions": "Create a user at POST /users to get an API key"
    }


@app.get("/users/me", response_model=schemas.UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    """
    Get information about the authenticated user.

    The CurrentUser dependency handles all authentication automatically.
    If the request reaches this function, authentication succeeded.
    """

    output = schemas.UserResponse(
        id=current_user.id,
        email=current_user.email,
        created=current_user.created,
        key_expires=current_user.key_expires,
        is_valid=current_user.is_valid
    )

    return output

# TODO: Renew API key
