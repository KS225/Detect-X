from app.database.session import Base, engine

# Import all models here
from app.models.user import User


def initialize_database():
    """
    Creates all database tables.
    """
    Base.metadata.create_all(bind=engine)