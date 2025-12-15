# In connection.py werden die Datenbankverbindung und die Session-Verwaltung definiert.

from sqlalchemy import create_engine # SQLAlchemy nutzen wir um ORM mit SQLite zu verbinden
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path

# Datenbankpfad relativ zum Projekt-Root
DB_DIR = Path(__file__).parent.parent.parent / "data" # Ordnerstruktur hochgehen bis zum Projekt-Root und dann in data Ordner
DB_DIR.mkdir(exist_ok=True) # Erstellt den data Ordner, falls er nicht existiert
DB_PATH = DB_DIR / "expenses.db" # Datenbankdatei im data Ordner definieren

# SQLite Connection String
DATABASE_URL = f"sqlite:///{DB_PATH}" 

# Engine erstellen
engine = create_engine( # Erstellt die Verbindung zur SQLite-Datenbank
    DATABASE_URL,
    echo=False,  # SQL-Queries in Console ausgeben (für Debugging)
)

# Session Factory
# So sind wir in der Lage uns ganz einfach neue Sessions zu erstellen: session1 = SessionLocal(), session2 = SessionLocal(), etc.
SessionLocal = sessionmaker( # Erstellt eine Session Factory für die Datenbank, die Sessions verwaltet
    autocommit=False,
    autoflush=False, 
    bind=engine # Bindet die Sessions an die erstellte Engine
)

def init_db():
    from .models import Base
    Base.metadata.create_all(bind=engine)
    print(f"✓ Datenbank initialisiert: {DB_PATH}")
