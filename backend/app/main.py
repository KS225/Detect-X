from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.website import router as website_router
from app.api.scanner import router as scanner_router

from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.setup import initialize_database


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# EXCEPTION HANDLERS
# ============================================================

register_exception_handlers(app)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(website_router)
app.include_router(scanner_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}"
    }