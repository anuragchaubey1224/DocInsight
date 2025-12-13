# backend/app/routes/auth.py

"""
Authentication routes: signup, login, and user info.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.schemas.auth import Token, LoginRequest

router = APIRouter()


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data (email, password)
        db: Database session
        
    Returns:
        Created user data (without password)
        
    Raises:
        HTTPException: 400 if email already exists
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Authenticate user and return JWT access token.
    
    Args:
        login_data: Login credentials (email, password)
        db: Database session
        
    Returns:
        JWT access token and token type
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Fetch user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    # Validate user exists and password is correct
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token with user email as subject
    access_token = create_access_token(data={"sub": user.email})
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get current authenticated user's information.
    
    Args:
        current_user: Current authenticated user (injected via dependency)
        
    Returns:
        Current user data (without password)
    """
    return current_user
