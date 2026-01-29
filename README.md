# FINLY - Dein Finanzmanager 📊

Willkommen bei **FINLY**, deiner einfachen und modernen Ausgabenverwaltung mit AI-Integration.

## 🚀 Schnellstart (Windows)

Das Projekt enthält ein automatisches Start-Skript für maximalen Komfort.

1.  **Doppelklicke auf `start.bat (Windows)/start.sh (Mac)` ** im Hauptordner.
2.  Das Skript prüft alles, startet den Server und öffnet deinen Browser automatisch.
3.  Fertig! 🎉

---

## 🛠️ Manuelle Installation (Alternative)

Falls du lieber die Kommandozeile nutzt oder Probleme mit dem Skript hast:

1.  **Voraussetzungen prüfen:**

    ```powershell
    python --version
    ```

2.  **Umgebung erstellen & aktivieren:**

    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```

    _(Achte auf das grüne `(venv)` am Zeilenanfang)_

3.  **Abhängigkeiten installieren:**

    ```powershell
    pip install -r requirements.txt
    ```

4.  **Konfiguration (.env):**
    Erstelle eine `.env` Datei mit deinem Google Gemini API Key (optional):

    ```env
    GEMINI_API_KEY=dein_key_hier
    ```

5.  **Starten:**
    ```powershell
    python -m uvicorn src.api.main:app --reload
    ```
    Browser öffnen auf: http://127.0.0.1:8000

---

## ✨ Features

- **Dashboard**: Einnahmen/Ausgaben Übersicht mit interaktiven Charts.
- **Auto-Kategorisierung**: AI lernt aus deinen Buchungen.
- **CSV Import**: Importiere Bankumsätze per Drag & Drop.
- **Finanz-Buddy (Chatbot)**: Stelle Fragen an deine Finanzen (benötigt API Key).
- **Zinsrechner**: Plane deine Sparziele.

## 📁 Projektstruktur

- **`start.bat`**: Ein-Klick-Startskript.
- **`src/`**: Backend (FastAPI, Datenbank).
- **`static/`**: Frontend (CSS, JS).
- **`templates/`**: HTML Seiten.
- **`data/`**: Hier liegt deine Datenbank (`expenses.db`).

### Categories-Modul

#### Zielsetzung und Funktionalität

Das Categories-Modul ermöglicht die automatische Zuordnung von Transaktionen zu Kategorien mittels regelbasierter Kategorisierung. Das System ist selbstlernend und verbessert sich durch Analyse bereits kategorisierter Transaktionen kontinuierlich.

#### 1.2 Komponenten und Aufbau

**Dateistruktur:**

```
src/categories/
├── __init__.py                    # Modul-Initialisierung und Exports
├── categories.py                  # Kategorieverwaltung und -operationen
├── categorizer_rules.py           # Regelbasierte Kategorisierungs-Engine
├── auto_categorizer_service.py    # Iterativer Kategorisierungs- und Lernservice
└── rules.py                       # Standard-Kategorisierungsregeln
```

**1. `categories.py`** - Kategorieverwaltung

- **Standard-Kategorien**: Automatisches Laden von vordefinierten Kategorien (Lebensmittel, Miete, Gehalt, etc.) bei erster Nutzung
- **CRUD-Operationen**:
  - `add_category()`: Erstellt neue Kategorien mit Validierung
  - `remove_category()`: Löscht Kategorien inklusive zugehöriger Regeln
  - `get_categories()`: Ruft alle verfügbaren Kategorien ab
  - `assign_category_to_transaction()`: Weist Transaktionen Kategorien zu
- **Sonstiges**:
  - Icon- und Farbunterstützung für UI-Integration
  - Konsistente Foreign-Key-Behandlung beim Löschen

**2. `categorizer_rules.py`** - Kategorisierungs-Engine

- **Hauptklasse `Categorizer`**: Regelbasierte Kategorisierung

- **Kernfunktionen**:
  - `suggest_category()`: Schlägt Kategorie basierend auf Keywords vor
  - `categorize_all()`: Kategorisiert alle oder nur unkategorisierte Transaktionen
  - `learn_from_categorized_transactions()`: Lernt neue Keywords aus bereits kategorisierten Daten
  - `add_keyword_to_rule()` / `remove_keyword_from_rule()`: Dynamische Regelverwaltung
- **Intelligente Features**:
  - Keyword-Matching über mehrere Transaktionsfelder (Begünstigter, Verwendungszweck, IBAN, Beschreibung)
  - Stopword-Filter zur Vermeidung von generischen Keywords
  - Eindeutigkeitsprüfung: Keywords werden nur gelernt, wenn sie eindeutig einer Kategorie zugeordnet sind
  - Caching-Mechanismus mit 5-Minuten-Zeitfenster für Performance-Optimierung

**3. `auto_categorizer_service.py`** - Automatisierter Lernservice

- **Hauptklasse `AutoCategorizerService`**: Orchestriert iterative Kategorisierungs- und Lernzyklen
- **Iterativer Lernzyklus** (`run_full_categorization_cycle()`):

1. Kategorisiert alle unkategorisierten Transaktionen
2. Zählt aktuelle Keywords
3. Lernt neue Keywords aus kategorisierten Transaktionen
4. Prüft ob neue Keywords hinzugefügt wurden
5. Wiederholt Prozess bis keine neuen Keywords mehr gefunden werden

- **Automatische Trigger**:
  - **Backend-Start**: Prüft beim Starten der Anwendung automatisch auf neue Transaktionen und führt bei Bedarf einen Lernzyklus aus
  - **CSV-Import**: Startet nach jedem erfolgreichen CSV-Import automatisch einen vollständigen Lernzyklus
  - **Transaktions-Schwellwert**: Löst automatisch einen Lernzyklus aus, sobald 5 neue Transaktionen hinzugefügt wurden (Wert ist konfigurierbar)
- **State-Management**:
  - `increment_transaction_counter()`: Zählt neue Transaktionen
  - `should_trigger_categorization()`: Prüft ob Auto-Kategorisierung ausgelöst werden soll (Schwellwert-basiert)
  - `get_categorization_state()`: Gibt aktuellen Status zurück
- **Singleton-Pattern**: Globale Service-Instanz über `get_auto_categorizer_service()`

**4. `rules.py`** - Regelkonfiguration

- Enthält `DEFAULT_CATEGORIZATION_RULES` mit vordefinierten Keywords für Standardkategorien
- Wird beim ersten Start automatisch in die Datenbank geladen

#### 1.3 Technische Details

**Datenbank-Integration:**

- Nutzt SQLAlchemy ORM mit `SessionLocal()`
- Tabellen: `Category`, `CategoryRules`, `Transaktion`, `CategorizationState`
- Automatische Migration und Initialisierung

**Algorithmus-Logik:**

1. **Keyword-Extraktion**: Transaktionsfelder werden zu einem Suchtext kombiniert und in Kleinbuchstaben konvertiert
2. **Pattern-Matching**: Jede Regel wird gegen den Suchtext geprüft
3. **Adaptive Regelgenerierung**: Häufig vorkommende, eindeutige Keywords werden automatisch als neue Regeln hinzugefügt
4. **Feedback-Loop**: System verbessert sich durch jede kategorisierte Transaktion

**Besondere Algorithmus-Features:**

- **Stopword-Filter**: Entfernt bedeutungslose Wörter wie "und", "für", "mit"
- **Mindestlänge**: Keywords müssen mindestens 3 Zeichen haben
- **Eindeutigkeitsprüfung**: Keywords, die in mehreren Kategorien vorkommen, werden ignoriert
- **Häufigkeitsfilter**: Nur Keywords mit Mindestanzahl an Vorkommen (default: 3) werden gelernt

---

### 2. Chatbot-Modul

#### 2.1 Zielsetzung und Funktionalität

Das Chatbot-Modul implementiert einen KI-gestützten Finanzassistenten, der natürlichsprachige Anfragen zu Finanzdaten beantwortet. Es nutzt Google Gemini API mit automatischem Function Calling, um präzise Datenbankabfragen durchzuführen und Analysen zu generieren.

#### 2.2 Komponenten und Aufbau

**Dateistruktur:**

```
src/chatbot/
├── __init__.py           # Modul-Exports
├── gemini_client.py      # Gemini API Client mit Function Calling
└── tools.py              # Database-Tools für Function Calling
```

**1. `gemini_client.py`** - Gemini API Integration

- **Hauptklasse `GeminiChatbot`**: Verwaltet Kommunikation mit Gemini API
- **Initialisierung**:
  - Benötigt API-Key und SQLAlchemy Session
  - Verwendet Modell `gemini-2.5-flash`
  - Hält Chat-Historie für Kontext
- **System Instruction**: Definiert Verhaltensregeln für den Assistenten:
  - Immer Tools verwenden, niemals raten
  - Kein manuelles Rechnen - nur Tool-basierte Berechnungen
  - Präzise Antworten ohne Erfindung von Daten
  - Unterstützung für komplexe Multi-Filter-Anfragen
- **Methoden**:
  - `send_message()`: Sendet Benutzeranfrage und erhält KI-Antwort mit automatischem Function Calling
  - `reset_chat()`: Löscht Chat-Historie

**2. `tools.py`** - Function Calling Tools

- **Session-Management**:
  - `set_db_session()`: Setzt globale Datenbank-Session
  - `get_db_session()`: Gibt aktuelle Session zurück
- **Implementierte Tools** (8 Funktionen):

**a) `get_transactions()`** - Transaktionsabfrage - Filter: Datumsbereich, Kategorie, Typ (Einnahme/Ausgabe) - Limit-Parameter (default: 100) - Sortierung nach Buchungstag (absteigend)

**b) `get_spending_by_category()`** - Ausgaben nach Kategorie - Aggregiert Ausgaben pro Kategorie - Optionaler Datumsfilter - Sortiert nach Gesamtausgaben

**c) `get_monthly_summary()`** - Monatliche Zusammenfassung - Einnahmen und Ausgaben pro Monat - Berechnet Bilanz (Einnahmen - Ausgaben) - Jahr-Parameter (default: aktuelles Jahr)

**d) `get_account_overview()`** - Kontoübersicht - Listet alle Konten mit Details - Kontostände, Kontotypen, Banknamen

**e) `get_income_vs_expenses()`** - Einnahmen vs. Ausgaben - Vergleich für definierten Zeitraum - Berechnet Gesamtbilanz

**f) `get_categories()`** - Kategorienliste - Gibt alle verfügbaren Kategorien zurück - Mit Typ (Einnahme/Ausgabe)

**g) `get_database_statistics()`** - Datenbank-Statistiken - Anzahl Transaktionen, Konten, Kategorien - Zeitraum der ersten bis letzten Transaktion - Datenbank-Status

**h) `get_transaction_stats()`** - Statistische Berechnungen - Berechnet: Summe, Anzahl, Durchschnitt, Min, Max - Alle Filter wie bei `get_transactions()` verfügbar - **Wichtig**: Soll für alle Summen-/Durchschnittsberechnungen verwendet werden

**3. `__init__.py`** - Modul-Exports

- Exportiert `GeminiChatbot` für einfachen Import

#### 2.3 Technische Details

**Function Calling Workflow:**

1. User stellt Frage
2. Gemini analysiert Anfrage und entscheidet welche Tools benötigt werden
3. API ruft automatisch relevante Tools auf
4. Tools führen Datenbankabfragen durch
5. Ergebnisse werden zurück an Gemini gegeben
6. Gemini generiert natürlichsprachige Antwort basierend auf Daten

**Automatisches Function Calling:**

- Gemini entscheidet selbstständig welche Funktionen aufgerufen werden
- Mehrere Function Calls pro Anfrage möglich
- Ergebnisse werden automatisch in Kontext integriert

**Fehlerbehandlung:**

- Try-Catch für API-Fehler
- Benutzerfreundliche Fehlermeldungen
- Robuste None-Checks bei Datenbankabfragen
