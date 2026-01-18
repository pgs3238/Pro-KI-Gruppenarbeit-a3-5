# Flask Backend für Zinsrechner mit Datenbankanbindung

from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Ermöglicht CORS für Frontend-Zugriff

# Verzeichnis für Vergleichsdatenbanken
BASE_DIR = Path(__file__).parent
VERGLEICH_DIR = BASE_DIR / "data" / "vergleiche"
VERGLEICH_DIR.mkdir(parents=True, exist_ok=True)

# Hauptdatenbank für Kontostände
MAIN_DB = BASE_DIR / "data" / "expenses.db"

# ============ HILFSFUNKTIONEN ============

def erstelle_vergleichs_db(db_nummer):
    """Erstellt eine Vergleichsdatenbank"""
    db_path = VERGLEICH_DIR / f"vergleich_{db_nummer}.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabelle für Kontoverlauf erstellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kontoverlauf (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            periode INTEGER,
            kontostand REAL,
            einzahlungen REAL,
            zinsen REAL
        )
    ''')
    
    # Tabelle für Parameter erstellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parameter (
            id INTEGER PRIMARY KEY,
            startkapital REAL,
            zinssatz REAL,
            intervall TEXT,
            einzahlung REAL,
            laufzeit REAL,
            kontoauswahl TEXT,
            erstellt_am TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    return str(db_path)

def loesche_vergleichs_db(db_nummer):
    """Löscht eine Vergleichsdatenbank"""
    db_path = VERGLEICH_DIR / f"vergleich_{db_nummer}.db"
    if db_path.exists():
        db_path.unlink()
        return True
    return False

def speichere_vergleich(db_nummer, verlauf, parameter):
    """Speichert Vergleichsdaten in Datenbank"""
    try:
        db_path = erstelle_vergleichs_db(db_nummer)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lösche alte Daten
        cursor.execute('DELETE FROM kontoverlauf')
        cursor.execute('DELETE FROM parameter')
        
        # Speichere Verlaufsdaten
        for punkt in verlauf:
            cursor.execute('''
                INSERT INTO kontoverlauf (periode, kontostand, einzahlungen, zinsen)
                VALUES (?, ?, ?, ?)
            ''', (
                punkt.get('periode', 0),
                punkt.get('kapital', 0),
                punkt.get('einzahlungGesamt', 0),
                punkt.get('zinsenGesamt', 0)
            ))
        
        # Speichere Parameter
        cursor.execute('''
            INSERT INTO parameter (id, startkapital, zinssatz, intervall, einzahlung, laufzeit, kontoauswahl, erstellt_am)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            parameter.get('startkapital', 0),
            parameter.get('zinssatz', 0),
            parameter.get('intervall', 'Monatlich'),
            parameter.get('einzahlung', 0),
            parameter.get('laufzeit', 0),
            parameter.get('kontostandTyp', parameter.get('kontoauswahl', 'fiktiv')),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")
        import traceback
        traceback.print_exc()
        return False

def lade_vergleich(db_nummer):
    """Lädt Vergleichsdaten aus Datenbank"""
    db_path = VERGLEICH_DIR / f"vergleich_{db_nummer}.db"
    if not db_path.exists():
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lade Parameter zuerst (brauchen wir für Jahr-Berechnung)
        cursor.execute('SELECT * FROM parameter WHERE id = 1')
        param_row = cursor.fetchone()
        
        if not param_row:
            conn.close()
            return None
            
        parameter = {
            'startkapital': param_row[1],
            'zinssatz': param_row[2],
            'intervall': param_row[3],
            'einzahlung': param_row[4],
            'laufzeit': param_row[5],
            'kontostandTyp': param_row[6],
            'erstellt_am': param_row[7] if len(param_row) > 7 else None
        }
        
        # Lade Verlaufsdaten und konvertiere zu JavaScript-Format
        cursor.execute('SELECT periode, kontostand, einzahlungen, zinsen FROM kontoverlauf ORDER BY periode')
        verlauf_rows = cursor.fetchall()
        
        # Konvertiere Datenbank-Format zu JavaScript-Format
        startjahr = datetime.now().year
        verlauf = []
        for row in verlauf_rows:
            periode = row[0]
            # Berechne Jahr basierend auf Periode und Intervall
            if parameter['intervall'] == 'Monatlich':
                jahr = startjahr + (periode // 12)
            elif parameter['intervall'] == 'Vierteljährlich':
                jahr = startjahr + (periode // 4)
            else:  # Jährlich
                jahr = startjahr + periode
            
            verlauf.append({
                'jahr': jahr,
                'periode': periode,
                'kapital': row[1],
                'einzahlungGesamt': row[2],
                'zinsenGesamt': row[3]
            })
        
        conn.close()
        return {'verlauf': verlauf, 'parameter': parameter}
        
    except Exception as e:
        print(f"Fehler beim Laden von Vergleich {db_nummer}: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============ API ENDPUNKTE ============

@app.route('/api/kontostand', methods=['GET'])
def get_kontostand():
    """Gibt den aktuellen Gesamtkontostand zurück (Summe aller Transaktionen)"""
    try:
        # Prüfe ob Datenbank existiert
        if not MAIN_DB.exists():
            return jsonify({
                'success': True,
                'kontostand': 0.0,
                'waehrung': 'EUR',
                'hinweis': 'Keine Datenbank gefunden'
            })
        
        conn = sqlite3.connect(MAIN_DB)
        cursor = conn.cursor()
        
        # Prüfe ob Tabelle existiert
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transaktionen'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': True,
                'kontostand': 0.0,
                'waehrung': 'EUR',
                'hinweis': 'Keine Transaktionen vorhanden'
            })
        
        # Berechne Summe aller Transaktionen
        cursor.execute('SELECT SUM(betrag) FROM transaktionen')
        result = cursor.fetchone()
        gesamtsumme = result[0] if result[0] is not None else 0.0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'kontostand': float(gesamtsumme),
            'waehrung': 'EUR'
        })
    
    except Exception as e:
        print(f"Fehler beim Laden des Kontostands: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/konten', methods=['GET'])
def get_konten():
    """Gibt alle Konten mit ihren individuellen Kontoständen zurück"""
    try:
        # Prüfe ob Datenbank existiert
        if not MAIN_DB.exists():
            return jsonify({
                'success': True,
                'konten': [],
                'hinweis': 'Keine Datenbank gefunden'
            })
        
        conn = sqlite3.connect(MAIN_DB)
        cursor = conn.cursor()
        
        # Prüfe ob Tabelle existiert
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transaktionen'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': True,
                'konten': [],
                'hinweis': 'Keine Transaktionen vorhanden'
            })
        
        # Hole alle Konten mit Kontostand
        cursor.execute("""
            SELECT 
                iban_kontonummer,
                SUM(betrag) as kontostand,
                COUNT(*) as anzahl_transaktionen
            FROM transaktionen 
            WHERE iban_kontonummer IS NOT NULL AND iban_kontonummer != ''
            GROUP BY iban_kontonummer
            ORDER BY kontostand DESC
        """)
        
        konten = []
        for iban, kontostand, anzahl in cursor.fetchall():
            # Kürze IBAN für Anzeige (z.B. DE89...3000)
            iban_kurz = f"{iban[:4]}...{iban[-4:]}" if len(iban) > 8 else iban
            konten.append({
                'iban': iban,
                'iban_kurz': iban_kurz,
                'kontostand': float(kontostand),
                'anzahl_transaktionen': anzahl,
                'waehrung': 'EUR'
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'konten': konten
        })
    
    except Exception as e:
        print(f"Fehler beim Laden der Konten: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/vergleich/speichern', methods=['POST'])
def speichere_vergleich_endpoint():
    """Speichert einen Vergleich in der Datenbank"""
    try:
        data = request.json
        db_nummer = data.get('db_nummer')
        verlauf = data.get('verlauf')
        parameter = data.get('parameter')
        
        if not all([db_nummer, verlauf, parameter]):
            return jsonify({'success': False, 'error': 'Fehlende Daten'}), 400
        
        if db_nummer not in [1, 2, 3]:
            return jsonify({'success': False, 'error': 'Ungültige DB-Nummer (1-3)'}), 400
        
        success = speichere_vergleich(db_nummer, verlauf, parameter)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Fehler beim Speichern in Datenbank'
            }), 500
        
        return jsonify({
            'success': True,
            'message': f'Vergleich {db_nummer} gespeichert'
        })
    
    except Exception as e:
        print(f"API Fehler beim Speichern: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/vergleich/laden/<int:db_nummer>', methods=['GET'])
def lade_vergleich_endpoint(db_nummer):
    """Lädt einen Vergleich aus der Datenbank"""
    try:
        if db_nummer not in [1, 2, 3]:
            return jsonify({'success': False, 'error': 'Ungültige DB-Nummer (1-3)'}), 400
        
        daten = lade_vergleich(db_nummer)
        
        if daten is None:
            return jsonify({
                'success': False,
                'error': 'Vergleich nicht gefunden'
            }), 404
        
        return jsonify({
            'success': True,
            'daten': daten
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/vergleich/alle', methods=['GET'])
def lade_alle_vergleiche():
    """Lädt alle gespeicherten Vergleiche"""
    try:
        vergleiche = {}
        for i in [1, 2, 3]:
            daten = lade_vergleich(i)
            if daten:
                vergleiche[i] = daten
        
        return jsonify({
            'success': True,
            'vergleiche': vergleiche
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/vergleich/loeschen/<int:db_nummer>', methods=['DELETE'])
def loesche_vergleich_endpoint(db_nummer):
    """Löscht einen Vergleich"""
    try:
        if db_nummer not in [1, 2, 3]:
            return jsonify({'success': False, 'error': 'Ungültige DB-Nummer (1-3)'}), 400
        
        erfolg = loesche_vergleichs_db(db_nummer)
        
        if erfolg:
            return jsonify({
                'success': True,
                'message': f'Vergleich {db_nummer} gelöscht'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Vergleich existiert nicht'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/vergleich/alle_loeschen', methods=['DELETE'])
def loesche_alle_vergleiche():
    """Löscht alle Vergleiche"""
    try:
        for i in [1, 2, 3]:
            loesche_vergleichs_db(i)
        
        return jsonify({
            'success': True,
            'message': 'Alle Vergleiche gelöscht'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Erstelle Verzeichnisse
    VERGLEICH_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 50)
    print("Flask Server startet...")
    print(f"API verfügbar unter: http://localhost:5000/api")
    print(f"Vergleiche werden gespeichert in: {VERGLEICH_DIR}")
    print(f"Hauptdatenbank: {MAIN_DB}")
    print("=" * 50)
    
    # Starte Flask-Server
    app.run(debug=True, port=5000, host='127.0.0.1')
