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
pip install SQLAlchemy==2.0.44 fastapi>=0.104.0 uvicorn[standard]>=0.24.0 pydantic>=2.0.0 python-dotenv>=1.2.1 google-genai>=1.57.0 python-multipart>=0.0.6 -q
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
