from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.auth import EmailAlreadyExistsException


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(EmailAlreadyExistsException)
    async def email_exists_handler(
        request: Request,
        exc: EmailAlreadyExistsException,
    ):
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Email already registered"
            },
        )