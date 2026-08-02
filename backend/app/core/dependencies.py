from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db

# Database
DBSession = Annotated[Session, Depends(get_db)]

# JWT Authentication (Coming Soon)
# CurrentUser = Annotated[User, Depends(get_current_user)]

# Admin Authentication (Future)
# AdminUser = Annotated[User, Depends(get_current_admin)]