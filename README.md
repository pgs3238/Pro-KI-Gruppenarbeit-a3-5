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

Das Categories-Modul ermöglicht die automatische Zuordnung von Transaktionen zu Kategorien mittels regelbasierter Kategorisierung. Das System ist selbstlernend und verbessert sich durch Analyse bereits kategorisierter Transaktionen kontinuierlich.

**`categories.py`** - Kategorieverwaltung

- **Standard-Kategorien**: Automatisches Laden von vordefinierten Kategorien (Lebensmittel, Miete, Gehalt, etc.) bei erster Nutzung
- **CRUD-Operationen**:
  - `add_category()`: Erstellt neue Kategorien mit Validierung
  - `remove_category()`: Löscht Kategorien inklusive zugehöriger Regeln
  - `get_categories()`: Ruft alle verfügbaren Kategorien ab
  - `assign_category_to_transaction()`: Weist Transaktionen Kategorien zu

**`categorizer_rules.py`** - Kategorisierungs-Engine

- **Hauptklasse `Categorizer`**: Regelbasierte Kategorisierung

- **Kernfunktionen**:
  - `suggest_category()`: Schlägt Kategorie basierend auf Keywords vor
  - `categorize_all()`: Kategorisiert alle oder nur unkategorisierte Transaktionen
  - `learn_from_categorized_transactions()`: Lernt neue Keywords aus bereits kategorisierten Daten
  - `add_keyword_to_rule()` / `remove_keyword_from_rule()`: Dynamische Regelverwaltung
- **Features**:
  - Keyword-Matching über mehrere Transaktionsfelder
  - Filter zur Vermeidung von generischen Keywords
  - Eindeutigkeitsprüfung: Keywords werden nur gelernt, wenn sie eindeutig einer Kategorie zugeordnet sind
  - Caching-Mechanismus mit 5-Minuten-Zeitfenster für Performance-Optimierung

**`auto_categorizer_service.py`** - Automatisierter Lernservice

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
  - **Transaktions-Schwellwert**: Löst automatisch einen Lernzyklus aus, sobald 5 neue Transaktionen hinzugefügt wurden

**`rules.py`** - Regelkonfiguration

- Enthält `DEFAULT_CATEGORIZATION_RULES` mit vordefinierten Keywords für Standardkategorien
- Wird beim ersten Start automatisch in die Datenbank geladen

**Kategorisierungslogik:**

1. **Keyword-Extraktion**: Transaktionsfelder werden zu einem Suchtext kombiniert und in Kleinbuchstaben konvertiert
2. **Pattern-Matching**: Jede Regel wird gegen den Suchtext geprüft
3. **Adaptive Regelgenerierung**: Häufig vorkommende, eindeutige Keywords werden automatisch als neue Regeln hinzugefügt
4. **Feedback-Loop**: System verbessert sich durch jede kategorisierte Transaktion

---

### Chatbot-Modul

Das Chatbot-Modul implementiert einen KI-gestützten Finanzassistenten, der natürlichsprachige Anfragen zu Finanzdaten beantwortet. Es nutzt Google Gemini API mit automatischem Function Calling, um präzise Datenbankabfragen durchzuführen und Analysen zu generieren.

#### Komponenten und Aufbau

**`gemini_client.py`** - Gemini API Integration

- **Hauptklasse `GeminiChatbot`**: Verwaltet Kommunikation mit Gemini API
- **Initialisierung**:
  - Benötigt API-Key und SQLAlchemy Session
  - Verwendet Modell `gemini-2.5-flash`
  - Hält Chat-Historie für Kontext
- **System Instruction**:
  - Definiert Verhaltensregeln für den Assistenten
- **Methoden**:
  - `send_message()`: Sendet Benutzeranfrage und erhält KI-Antwort mit automatischem Function Calling
  - `reset_chat()`: Löscht Chat-Historie

**`tools.py`** - Function Calling Tools

- **Session-Management**: Globale Datenbank-Session Verwaltung
- **Datenbankabfrage-Funktionen**: Implementierte Tools für Transaktionsabfragen, Kategorieauswertungen, Kontoübersichten und Auswertungen
