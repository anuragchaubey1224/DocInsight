# backend/app/schemas/document.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class DocumentBase(BaseModel):
    """Base document schema with shared fields."""
    filename: str


class DocumentRead(DocumentBase):
    """Schema for reading document data."""
    id: int
    user_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DocumentMeta(DocumentRead):
    """Extended schema with processing artifacts metadata."""
    text_path: Optional[str] = None
    summary_path: Optional[str] = None
    index_path: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
