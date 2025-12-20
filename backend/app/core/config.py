# backend/app/core/config.py

from functools import lru_cache
from pathlib import Path
import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    # Project Settings
    
    PROJECT_NAME: str = "DocInsight API"
    API_PREFIX: str = "/api"

  
    # Security
    
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

   
    # Database (REQUIRED – injected via ENV)
    
    DATABASE_URL: str

    
    # Environment Mode
    # Default is production (Local dev can override via .env)
    
    ENV: str = "production"

    # Directories
    # Project root = DocInsight/
    BASE_DIR: Path = Path(__file__).resolve().parents[3]

    UPLOAD_DIR: Path = BASE_DIR / "backend" / "app" / "data" / "uploads"
    INDEX_DIR: Path = BASE_DIR / "backend" / "app" / "data" / "index"

    
    # ML Models
    SUMMARIZER_MODEL: str = "google/flan-t5-base"
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"

    
    # OCR / System Paths
    # Linux default for Render, overridable via ENV
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")

    class Config:
        # For local development only (.env)
        # Render ignores this and injects ENV vars directly
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Load & cache project settings.
    Ensures required directories exist.
    """
    settings = Settings()

    # Ensure directories exist
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.INDEX_DIR.mkdir(parents=True, exist_ok=True)

    return settings
