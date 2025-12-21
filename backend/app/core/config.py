# backend/app/core/config.py

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings
import os
import shutil


class Settings(BaseSettings):
    # --------------------------------
    # Project Settings
    # --------------------------------
    PROJECT_NAME: str = "DocInsight API"
    API_PREFIX: str = "/api"

    # --------------------------------
    # Security
    # --------------------------------
    SECRET_KEY: str = "dev-secret-key-change-in-production"  # Default for local dev
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # --------------------------------
    # Database
    # --------------------------------
    DATABASE_URL: str = "sqlite:///./dev.db"  # Default for local dev

    # --------------------------------
    # Environment Mode (Auto-detected)
    # --------------------------------
    ENV: str = "development"  # Auto-detected: production/development

    # --------------------------------
    # CORS Origins
    # --------------------------------
    CORS_ORIGINS: str = "*"  # Comma-separated list, or "*" for dev

    # --------------------------------
    # Directories
    # --------------------------------
    # Project root = DocInsight/
    BASE_DIR: Path = Path(__file__).resolve().parents[3]

    UPLOAD_DIR: Path = BASE_DIR / "backend" / "app" / "data" / "uploads"
    INDEX_DIR: Path = BASE_DIR / "backend" / "app" / "data" / "index"

    # --------------------------------
    # ML Models
    # --------------------------------
    SUMMARIZER_MODEL: str = "google/flan-t5-base"
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"

    # --------------------------------
    # OCR / System Paths (Auto-detected)
    # --------------------------------
    TESSERACT_CMD: str = ""  # Auto-detected based on OS

    class Config:
        # Always load `.env` from project root (DocInsight/.env)
        env_file = str(Path(__file__).resolve().parents[3] / ".env")
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Load & cache project settings with auto-detection.
    """
    settings = Settings()

    # Auto-detect environment (Railway sets DATABASE_URL with postgresql://)
    if settings.DATABASE_URL.startswith("postgresql://") or settings.DATABASE_URL.startswith("postgres://"):
        settings.ENV = "production"
        
        # AUTO-OPTIMIZE: Use memory-efficient models for Railway free tier
        settings.EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # 80MB vs 420MB
        settings.SUMMARIZER_MODEL = "sshleifer/distilbart-cnn-6-6"  # 60MB vs 250MB (T5-small)
    
    # Validate production config
    if settings.ENV == "production":
        if settings.SECRET_KEY == "dev-secret-key-change-in-production":
            raise ValueError(
                "CRITICAL: SECRET_KEY must be set in production! "
                "Generate one with: openssl rand -hex 32"
            )
    
    # Auto-detect Tesseract path if not set
    if not settings.TESSERACT_CMD:
        # Try common paths
        tesseract_paths = [
            "/opt/homebrew/bin/tesseract",  # macOS Homebrew (Apple Silicon)
            "/usr/local/bin/tesseract",      # macOS Homebrew (Intel)
            "/usr/bin/tesseract",            # Linux/Railway
        ]
        for path in tesseract_paths:
            if shutil.which("tesseract") or os.path.exists(path):
                settings.TESSERACT_CMD = shutil.which("tesseract") or path
                break
        
        if not settings.TESSERACT_CMD:
            settings.TESSERACT_CMD = "tesseract"  # Fallback to PATH
    
    # Ensure directories exist
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.INDEX_DIR.mkdir(parents=True, exist_ok=True)

    return settings