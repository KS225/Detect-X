from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.website import router as website_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.setup import initialize_database
from app.api.scanner import router as scanner_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

register_exception_handlers(app)

initialize_database()

app.include_router(auth_router)
app.include_router(website_router)
app.include_router(auth_router)
app.include_router(website_router)
app.include_router(scanner_router)


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}"
    }