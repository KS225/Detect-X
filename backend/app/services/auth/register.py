from sqlalchemy.orm import Session

from app.core.password import hash_password
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.exceptions.auth import EmailAlreadyExistsException

class RegisterService:

    @staticmethod
    def execute(user_data: RegisterRequest, db: Session):

        existing_user = (
            db.query(User)
            .filter(User.email == user_data.email)
            .first()
        )

        if existing_user:
           raise EmailAlreadyExistsException()

        user = User(
            name=user_data.name,
            email=user_data.email,
            password=hash_password(user_data.password),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user