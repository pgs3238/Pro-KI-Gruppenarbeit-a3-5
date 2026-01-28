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
    *(Achte auf das grüne `(venv)` am Zeilenanfang)*

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
