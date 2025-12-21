import sqlite3
from datetime import datetime

def erstelle_datenbank(db_name='kontostände.db'):
    """
    Erstellt die SQLite-Datenbank und die Tabelle für Kontostände
    
    Parameter:
    - db_name: Name der Datenbankdatei
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Erstelle Tabelle für Kontostände
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kontostände (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datum TEXT NOT NULL,
            kontostand REAL NOT NULL,
            kontoart TEXT,
            zeitstempel TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def speichere_kontostand(datum, kontostand, kontoart="Girokonto", db_name='kontostände.db'):
    """
    Speichert einen Kontostand mit Datum in der Datenbank
    
    Parameter:
    - datum: Datum als String (YYYY-MM-DD)
    - kontostand: Kontostand als Float
    - kontoart: Art des Kontos (optional)
    - db_name: Name der Datenbankdatei
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO kontostände (datum, kontostand, kontoart)
        VALUES (?, ?, ?)
    ''', (datum, kontostand, kontoart))
    
    conn.commit()
    conn.close()

def hole_alle_kontostände(db_name='kontostände.db'):
    """
    Gibt alle gespeicherten Kontostände zurück
    
    Parameter:
    - db_name: Name der Datenbankdatei
    
    Returns:
    - Liste von Tupeln (id, datum, kontostand, kontoart, zeitstempel)
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM kontostände ORDER BY datum')
    ergebnisse = cursor.fetchall()
    
    conn.close()
    return ergebnisse

def hole_aktuellen_kontostand(kontoart="Girokonto", db_name='kontostände.db'):
    """
    Gibt den aktuellsten Kontostand für eine bestimmte Kontoart zurück
    
    Parameter:
    - kontoart: Art des Kontos
    - db_name: Name der Datenbankdatei
    
    Returns:
    - Tupel (datum, kontostand) oder None
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT datum, kontostand 
        FROM kontostände 
        WHERE kontoart = ? 
        ORDER BY datum DESC 
        LIMIT 1
    ''', (kontoart,))
    
    ergebnis = cursor.fetchone()
    conn.close()
    
    return ergebnis

def loesche_alle_kontostaende(db_name='kontostände.db'):
    """
    Löscht alle Einträge aus der Datenbank
    
    Parameter:
    - db_name: Name der Datenbankdatei
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM kontostände')
    
    conn.commit()
    conn.close()

# Initialisiere die Hauptdatenbank beim Import
erstelle_datenbank()
