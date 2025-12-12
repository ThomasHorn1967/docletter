from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from database import get_db, engine
from models import Base, User, Message
import schemas
import auth
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
