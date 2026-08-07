from sqlalchemy.orm import Session

from app.models.user import User
from app.models.website import Website
from app.schemas.website import (
    CreateWebsiteRequest,
)


class CreateWebsiteService:

    @staticmethod
    def execute(
        website_data: CreateWebsiteRequest,
        current_user: User,
        db: Session,
    ):

        existing = (
            db.query(Website)
            .filter(Website.url == str(website_data.url))
            .first()
        )

        if existing:
            raise ValueError(
                "Website already exists."
            )

        website = Website(
            user_id=current_user.id,
            name=website_data.name,
            url=str(website_data.url),
            description=website_data.description,
        )

        db.add(website)
        db.commit()
        db.refresh(website)

        return website