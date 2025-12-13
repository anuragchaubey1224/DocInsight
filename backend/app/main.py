# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routes import auth


def create_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
    )

    # --------------------------------
    # CORS
    # --------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # change for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --------------------------------
    # Include Routers
    # --------------------------------
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

    # --------------------------------
    # Root Endpoint
    # --------------------------------
    @app.get("/")
    def root():
        return {"status": "DocInsight API running"}

    return app


app = create_application()
