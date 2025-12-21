# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import Base, engine
from app.routes import auth, documents, summarize, ask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events for the application.
    Ensures database tables are created on first deployment.
    """
    # Startup
    logger.info("🚀 Starting DocInsight API...")
    try:
        # Create database tables if they don't exist
        logger.info("Initializing database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # Don't crash the app - Railway might not have DB ready yet
    
    yield
    
    # Shutdown
    logger.info("Shutting down DocInsight API...")


def create_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        lifespan=lifespan,
    )

    # --------------------------------
    # CORS (Environment-aware)
    # --------------------------------
    if settings.ENV == "production":
        # Production: Use specific origins from env
        origins = (
            settings.CORS_ORIGINS.split(",") 
            if settings.CORS_ORIGINS != "*" 
            else ["*"]
        )
        logger.info(f"Production mode - CORS origins: {origins}")
    else:
        # Development: Allow all origins
        origins = ["*"]
        logger.info("Development mode - CORS origins: ['*']")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --------------------------------
    # Include Routers
    # --------------------------------
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(documents.router, prefix="/documents", tags=["Documents"])
    app.include_router(summarize.router, prefix="/summarize", tags=["Summarization"])
    app.include_router(ask.router, tags=["Question Answering"])

    # --------------------------------
    # Health & Status Endpoints
    # --------------------------------
    @app.get("/")
    def root():
        return {
            "status": "DocInsight API running",
            "environment": settings.ENV,
            "version": "1.0.0"
        }
    
    @app.get("/health")
    def health():
        """Health check endpoint for Railway and monitoring."""
        return {
            "status": "healthy",
            "environment": settings.ENV,
            "database": "connected" if settings.DATABASE_URL else "not configured"
        }

    logger.info(f"Application started in {settings.ENV} mode")
    return app


app = create_application()
