from sqlalchemy.orm import Session

from app.core.jwt import create_access_token
from app.core.password import verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest


class LoginService:

    @staticmethod
    def execute(
        login_data: LoginRequest,
        db: Session,
    ):

        user = (
            db.query(User)
            .filter(User.email == login_data.email)
            .first()
        )

        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(
            login_data.password,
            user.password,
        ):
            raise ValueError("Invalid email or password")

        token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "type": "access"
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }