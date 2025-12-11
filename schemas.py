from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

# User Schemas


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    """
    email: EmailStr
    api_key: str = Field(min_length=5, max_length=50)
    message: str = "Enter the initial API key for registration"


class UserResponse(BaseModel):
    """
    Public user information returned in responses.
    """
    id: int
    email: EmailStr
    created: datetime
    is_valid: bool


class UserCreatedResponse(BaseModel):
    """
    Special response only used when creating a user.
    """
    email: str
    api_key: str
    message: str = "Store this API key securely - it won't be shown again"


class MessageCreate(BaseModel):
    """Request schema for creating a message"""
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    """Response schema for message data"""
    id: int
    title: str
    body: str
    created: datetime
