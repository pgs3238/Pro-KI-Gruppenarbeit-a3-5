"""
Shared Dependencies für FastAPI Endpoints
"""

from ..database.connection import SessionLocal


def get_db():
    """
    Datenbank-Session Dependency für FastAPI Endpoints.
    Wird automatisch nach jedem Request geschlossen.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
