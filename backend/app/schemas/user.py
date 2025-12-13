# backend/app/schemas/user.py

from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with shared fields."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str


class UserRead(UserBase):
    """Schema for reading user data (no password exposure)."""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
