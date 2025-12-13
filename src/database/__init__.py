#Durch diesen File machen wir aus dem Ordner "database " ein Package, welches von anderen Teilen der Anwendung importiert werden kann.

from .connection import engine, SessionLocal, get_session, init_db # Importiere wichtige Funktionen und Objekte aus connection.py
from .models import Base, Transaction # Importiere die ORM-Modelle aus models.py

__all__ = [ #Definiert, welche Objekte beim Importieren des Packages sichtbar sind, diese kommen aus den importierten Modulen, also connection.py und models.py
    'engine', #Verbindungsobjekt zur Datenbank
    'SessionLocal', #Session Factory für Datenbankoperationen; genutzt um Sitzungen zu erstellen und zu verwalten
    'init_db', #Funktion zur Initialisierung der Datenbank und Erstellung der Tabellen
    'Base', #Basisklasse für alle ORM-Modelle 
    'Transaction' #ORM-Modell für Transaktionen
]
