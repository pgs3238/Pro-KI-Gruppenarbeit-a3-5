# Durch diesen File machen wir aus dem Ordner "database " ein Package, welches von anderen Teilen der Anwendung importiert werden kann.

from .connection import (
    engine,
    SessionLocal,
    init_db,
)  # Importiere wichtige Funktionen und Objekte aus connection.py
from .models import (
    Base,
    Transaktion,
    Category,
    CategoryRules,
    Konto,
    CategorizationState,
)  # Importiere die ORM-Modelle aus models.py
from .konto_manager import KontoManager  # Importiere den KontoManager

__all__ = [  # Definiert, welche Objekte beim Importieren des Packages sichtbar sind, diese kommen aus den importierten Modulen, also connection.py und models.py
    "engine",  # Verbindungsobjekt zur Datenbank
    "SessionLocal",  # Session Factory für Datenbankoperationen; genutzt um Sitzungen zu erstellen und zu verwalten
    "init_db",  # Funktion zur Initialisierung der Datenbank und Erstellung der Tabellen
    "Base",  # Basisklasse für alle ORM-Modelle
    "Transaktion",  # ORM-Modell für Transaktionen
    "Category",  # ORM-Modell für Kategorien
    "CategoryRules",  # ORM-Modell für Kategorisierungsregeln
    "Konto",  # ORM-Modell für Konten
    "CategorizationState",  # ORM-Modell für den Kategorisierungsstatus
    "KontoManager",  # Manager-Klasse für Konto-Operationen
]
