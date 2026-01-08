@echo off
REM Komplettes Setup: venv aktivieren, Pakete installieren, API starten

echo.
echo ========================================
echo  FINLY - Komplettes Setup
echo ========================================
echo.

REM 1. Virtuelle Umgebung aktivieren
echo [1/3] Aktiviere virtuelle Umgebung...
call venv\Scripts\activate.bat
echo ✓ venv aktiviert
echo.

REM 2. Pakete installieren
echo [2/3] Installiere Python-Pakete...
pip install fastapi uvicorn sqlalchemy requests -q
echo ✓ Pakete installiert
echo.

REM 3. API starten
echo [3/3] Starte API-Server...
echo.
echo ========================================
echo  API läuft auf http://localhost:8000
echo ========================================
echo.
echo  Dokumentation: http://localhost:8000/docs
echo.
echo  Um zu stoppen: STRG + C
echo ========================================
echo.

python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

pause
