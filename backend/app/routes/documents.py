# backend/app/routes/documents.py

"""
Document management routes: upload, retrieval, and processing.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.document import DocumentUploadFullResponse
from app.services.document_service import (
    save_upload_file,
    create_document_record,
    create_user_folder,
    read_raw_text,
    save_cleaned_text
)
from app.services.extractor import extract_text_auto
from app.utils.text_cleaner import clean_text

router = APIRouter()

# Supported file extensions
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post("/upload", response_model=DocumentUploadFullResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a document, extract raw text, and clean text.
    
    Supported formats: PDF, DOCX, TXT
    
    Workflow:
    1. Validate file type
    2. Create user/document directory structure
    3. Save uploaded file
    4. Extract raw text
    5. Save raw.txt
    6. Clean text using NLP pipeline
    7. Save cleaned.txt
    8. Create database record
    9. Return document metadata with word counts
    
    Args:
        file: Uploaded file
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Document metadata with doc_id, filename, raw_word_count, clean_word_count
        
    Raises:
        HTTPException: 400 if file type is unsupported or text extraction fails
    """
    # Validate file extension
    filename = file.filename
    file_ext = None
    if filename:
        file_ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else None
    
    if not file_ext or file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Create a temporary document record to get doc_id
    temp_doc = create_document_record(
        db=db,
        user_id=current_user.id,
        filename=filename,
        text_path=None  # Will be updated after extraction
    )
    doc_id = temp_doc.id
    
    # Create user-specific folder structure
    user_doc_dir = create_user_folder(current_user.id, doc_id)
    
    # Save uploaded file
    saved_file_path = await save_upload_file(file, user_doc_dir, filename)
    
    # Extract raw text
    raw_text = extract_text_auto(saved_file_path)
    
    if not raw_text:
        # Clean up and raise error
        db.delete(temp_doc)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to extract text from document"
        )
    
    # Save raw text to raw.txt
    raw_text_path = user_doc_dir / "raw.txt"
    raw_text_path.write_text(raw_text, encoding="utf-8")
    
    # Calculate raw word count
    raw_word_count = len(raw_text.split())
    
    # Clean text using NLP pipeline
    cleaned_text = clean_text(raw_text)
    
    if not cleaned_text:
        # Clean up and raise error
        db.delete(temp_doc)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cleaning resulted in empty content"
        )
    
    # Save cleaned text to cleaned.txt
    cleaned_text_path = save_cleaned_text(current_user.id, doc_id, cleaned_text)
    
    # Calculate clean word count
    clean_word_count = len(cleaned_text.split())
    
    # Update document record with text_path
    temp_doc.text_path = str(raw_text_path)
    db.commit()
    db.refresh(temp_doc)
    
    return DocumentUploadFullResponse(
        doc_id=doc_id,
        filename=filename,
        raw_word_count=raw_word_count,
        clean_word_count=clean_word_count,
        message="Upload + cleaning successful"
    )
