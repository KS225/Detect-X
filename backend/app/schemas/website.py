from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CreateWebsiteRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    url: HttpUrl

    description: str | None = Field(
        default=None,
        max_length=500,
    )


class UpdateWebsiteRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    url: HttpUrl | None = None

    description: str | None = Field(
        default=None,
        max_length=500,
    )


class WebsiteResponse(BaseModel):
    id: int
    name: str
    url: str
    description: str | None
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )