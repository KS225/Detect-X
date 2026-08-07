from app.database.session import Base, engine

# Import ALL models here
from app.models.user import User
from app.models.website import Website
from app.models.scan import Scan
from app.models.scan_result import ScanResult


def initialize_database():
    """
    Creates all database tables.
    """
    Base.metadata.create_all(bind=engine)