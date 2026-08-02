from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.core.config import settings
from app.core.setup import initialize_database
from app.core.exception_handlers import register_exception_handlers


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)


register_exception_handlers(app)

initialize_database()

app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}"
    }