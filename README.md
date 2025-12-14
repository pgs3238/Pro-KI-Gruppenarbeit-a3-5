# Pro-KI-Gruppenarbeit-a3-5
Gruppenarbeit für das Modul Programmieren für KI - WiSe25/26 an der FHSWF

## 📋 Projektbeschreibung

Ausgabenverwaltungs-System für Finanztransaktionen. Dieses Repository befindet sich **in Entwicklung** und wird von mehreren Teammitgliedern parallel bearbeitet.

### Aktuell implementiert:
- ✅ SQLite-Datenbank mit SQLAlchemy ORM
- ✅ Transaction-Datenmodell
- ✅ CRUD-Operationen (Create, Read, Update, Delete)
- ✅ Beispiel-Skripte zur Demonstration

## 🗂️ Projektstruktur

```
Pro-KI-Gruppenarbeit-a3-5/
├── src/                          # Hauptcode
│   └── database/                 # Datenbank-Layer
│       ├── __init__.py          # Package-Exports
│       ├── connection.py        # DB-Engine & Session-Management
│       └── models.py            # ORM-Modelle
├── examples/                     # Beispiel-Skripte
│   ├── 01_create_transactions.py
│   ├── 02_read_transactions.py
│   ├── 03_update_transaction.py
│   └── 04_delete_transaction.py
├── data/                         # Datenbank-Dateien (wird automatisch erstellt)
│   └── expenses.db
├── databaseTest/                 # Alte Test-Dateien
├── requirements.txt              # Python-Dependencies
├── pyproject.toml               # Projekt-Konfiguration
└── README.md
```

## 🚀 Installation & Setup

### 1. Repository klonen
```bash
git clone https://github.com/pgs3238/Pro-KI-Gruppenarbeit-a3-5.git
cd Pro-KI-Gruppenarbeit-a3-5
```

### 2. Virtuelle Umgebung erstellen
```powershell
python -m venv .venv
```

### 3. Virtuelle Umgebung aktivieren

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 4. Projekt installieren
```powershell
pip install -e .
```

Dies installiert:
- Alle Dependencies aus `pyproject.toml`
- Das Projekt selbst im "editable mode" (Änderungen wirken sofort)

## 💾 Datenbank

### Technologie
- **SQLite**: Leichtgewichtige, dateibasierte Datenbank
- **SQLAlchemy**: Python ORM für objektorientierte DB-Zugriffe

### Datenmodell

#### Transaction-Tabelle
| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | Integer (PK) | Automatische ID |
| `buchungstag` | Date | Datum der Buchung |
| `beguenstigter` | String(200) | Empfänger/Zahler |
| `verwendungszweck` | String(500) | Verwendungszweck |
| `iban_kontonummer` | String(34) | IBAN oder Kontonummer |
| `betrag` | Float | Betrag (positiv/negativ) |
| `waehrung` | String(3) | Währungscode (Standard: EUR) |
| `beschreibung` | String(500) | Zusätzliche Beschreibung |
| `created_at` | DateTime | Erstellungszeitpunkt |

### Datenbankoperationen

Die Datenbank wird automatisch erstellt bei der ersten Nutzung unter `data/expenses.db`.

**Initialisierung:**
```python
from src.database import init_db
init_db()  # Erstellt alle Tabellen
```

**Session erstellen:**
```python
from src.database import SessionLocal
session = SessionLocal()
# ... Operationen ...
session.close()
```

## 📝 Beispiele ausführen

### 1. Transaktionen erstellen
```powershell
python examples\01_create_transactions.py
```
Erstellt die Datenbank und fügt 3 Beispiel-Transaktionen hinzu.

### 2. Transaktionen lesen
```powershell
python examples\02_read_transactions.py
```
Zeigt alle Transaktionen, filtert nach Ausgaben/Einnahmen und berechnet Summen.

### 3. Transaktion aktualisieren
```powershell
python examples\03_update_transaction.py
```
Demonstriert das Update von Transaktionen (nach ID und Verwendungszweck).

### 4. Transaktion löschen
```powershell
python examples\04_delete_transaction.py
```
Löscht eine Transaktion aus der Datenbank.

## 🔧 Verwendung im eigenen Code

```python
from src.database import SessionLocal, Transaction
from datetime import date

# Session erstellen
session = SessionLocal()

try:
    # Neue Transaktion erstellen
    transaction = Transaction(
        buchungstag=date(2024, 12, 13),
        beguenstigter="REWE",
        verwendungszweck="Einkauf",
        betrag=-50.00,
        waehrung="EUR"
    )
    
    # Zur Datenbank hinzufügen
    session.add(transaction)
    session.commit()
    
    # Transaktionen abfragen
    all_transactions = session.query(Transaction).all()
    
    # Filtern
    ausgaben = session.query(Transaction).filter(
        Transaction.betrag < 0
    ).all()
    
finally:
    session.close()
```

## 🌐 REST API

Das Projekt bietet eine **FastAPI REST API** zur Kommunikation zwischen Frontend und Backend.

### API starten

**Mit dem Startskript:**
```powershell
python examples\05_start_api_server.py
```

**Oder direkt mit uvicorn:**
```powershell
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Nach dem Start ist die API verfügbar unter:
- **API Base URL**: http://localhost:8000
- **Interaktive Dokumentation**: http://localhost:8000/docs
- **Alternative Dokumentation**: http://localhost:8000/redoc

### API Endpunkte

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| GET | `/` | API-Status und Informationen |
| GET | `/transactions` | Alle Transaktionen abrufen |
| GET | `/transactions/{id}` | Einzelne Transaktion nach ID |
| POST | `/transactions` | Neue Transaktion erstellen |
| PUT | `/transactions/{id}` | Transaktion aktualisieren |
| DELETE | `/transactions/{id}` | Transaktion löschen |
| GET | `/transactions/filter/date-range` | Filtern nach Datumsbereich |
| GET | `/transactions/stats/summary` | Statistik (Einnahmen, Ausgaben, Saldo) |

### Beispiele für API-Aufrufe

#### Alle Transaktionen abrufen (JavaScript)
```javascript
fetch('http://localhost:8000/transactions')
    .then(response => response.json())
    .then(data => console.log(data));
```

#### Neue Transaktion erstellen (JavaScript)
```javascript
fetch('http://localhost:8000/transactions', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        buchungstag: '2024-12-14',
        beguenstigter: 'REWE',
        verwendungszweck: 'Lebensmittel',
        iban_kontonummer: 'DE89370400440532013000',
        betrag: -45.67,
        waehrung: 'EUR',
        beschreibung: 'Wocheneinkauf'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

#### Transaktion löschen (JavaScript)
```javascript
fetch('http://localhost:8000/transactions/1', {
    method: 'DELETE'
})
.then(response => {
    if (response.ok) {
        console.log('Transaktion gelöscht');
    }
});
```

#### Statistik abrufen (JavaScript)
```javascript
fetch('http://localhost:8000/transactions/stats/summary')
    .then(response => response.json())
    .then(data => {
        console.log('Einnahmen:', data.total_income);
        console.log('Ausgaben:', data.total_expenses);
        console.log('Saldo:', data.balance);
    });
```

### API Test Interface

Eine fertige HTML-Testseite zum Ausprobieren der API:
```powershell
# Öffne examples\api_test.html im Browser
```

Die Datei `examples\api_test.html` enthält ein vollständiges Frontend-Beispiel mit:
- Verbindungstest zur API
- Formular zum Erstellen neuer Transaktionen
- Liste aller Transaktionen
- Löschen von Transaktionen
- Statistik-Anzeige

## 📦 Dependencies

- Python >= 3.8
- SQLAlchemy == 2.0.44
- FastAPI >= 0.104.0
- Uvicorn >= 0.24.0
- Pydantic >= 2.0.0


