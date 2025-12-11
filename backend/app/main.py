from fastapi import FastAPI
from .routes.upload import router as upload_router

app = FastAPI(
    title="DocInsight API",
    description="Document summarization + QA + web search",
    version="1.0"
)

app.include_router(upload_router,prefix="/upload",tags=["upload"])
@app.get("/")

def root():
    return {"status": "DocInsight API is running"}