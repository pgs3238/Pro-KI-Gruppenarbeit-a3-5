# In connection.py werden die Datenbankverbindung und die Session-Verwaltung definiert.

from sqlalchemy import (
    create_engine,
)  # SQLAlchemy nutzen wir um ORM mit SQLite zu verbinden
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path


# Datenbankpfad relativ zum Projekt-Root
DB_DIR = (
    Path(__file__).parent.parent.parent / "data"
)  # Ordnerstruktur hochgehen bis zum Projekt-Root und dann in data Ordner
DB_DIR.mkdir(exist_ok=True)  # Erstellt den data Ordner, falls er nicht existiert
DB_PATH = DB_DIR / "expenses.db"  # Datenbankdatei im data Ordner definieren

# SQLite Connection String
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Engine erstellen
engine = create_engine(  # Erstellt die Verbindung zur SQLite-Datenbank
    DATABASE_URL,
    echo=False,  # SQL-Queries in Console ausgeben (für Debugging)
)

# Session Factory
# So sind wir in der Lage uns ganz einfach neue Sessions zu erstellen: session1 = SessionLocal(), session2 = SessionLocal(), etc.
SessionLocal = sessionmaker(  # Erstellt eine Session Factory für die Datenbank, die Sessions verwaltet
    autocommit=False,
    autoflush=False,
    bind=engine,  # Bindet die Sessions an die erstellte Engine
)


def ensure_categorization_state():
    """
    Stellt sicher, dass der CategorizationState-Eintrag existiert.
    Erstellt ihn, falls er noch nicht vorhanden ist.
    """
    from .models import CategorizationState

    session = SessionLocal()
    try:
        state = session.query(CategorizationState).filter_by(id=1).first()
        if not state:
            state = CategorizationState(
                id=1, has_new_transactions=0, last_categorization=None
            )
            session.add(state)
            session.commit()
            print("[OK] CategorizationState initialisiert")
    finally:
        session.close()


def init_db():
    from .models import Base

    Base.metadata.create_all(bind=engine)
    print(f"[OK] Datenbank initialisiert: {DB_PATH}")

    # Lade Standard-Kategorien, falls die Datenbank leer ist
    from src.categories.categories import check_and_load_defaults_categories

    check_and_load_defaults_categories()
    ensure_categorization_state()
