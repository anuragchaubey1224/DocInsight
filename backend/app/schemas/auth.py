# backend/app/schemas/auth.py

from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded token data schema."""
    email: Optional[str] = None
