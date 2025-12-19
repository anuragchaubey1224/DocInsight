# backend/app/core/config.py

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --------------------------------
    # Project Settings
    # --------------------------------
    PROJECT_NAME: str = "DocInsight API"
    API_PREFIX: str = "/api"

    # --------------------------------
    # Security
    # --------------------------------
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # --------------------------------
    # Database
    # --------------------------------
    DATABASE_URL: str = "sqlite:///./dev.db"

    # --------------------------------
    # Environment Mode
    # --------------------------------
    # DEV MODE ONLY - REMOVE BEFORE PRODUCTION
    ENV: str = "development"  # Set to "production" before deployment

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
    # OCR / System Paths
    # --------------------------------
    TESSERACT_CMD: str = "/opt/homebrew/bin/tesseract"

    class Config:
        # Always load `.env` from project root (DocInsight/.env)
        env_file = str(Path(__file__).resolve().parents[3] / ".env")
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Load & cache project settings.
    """
    settings = Settings()

    # Ensure directories exist
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.INDEX_DIR.mkdir(parents=True, exist_ok=True)

    return settings
