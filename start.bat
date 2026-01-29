@echo off
echo ==============================================
echo      FINLY - Finanzmanager wird gestartet
echo ==============================================

:: Pruefen ob venv existiert
if exist "venv" (
    echo Aktiviere virtuelle Umgebung 'venv'...
    call venv\Scripts\activate
) else if exist ".venv" (
    echo Aktiviere virtuelle Umgebung '.venv'...
    call .venv\Scripts\activate
) else (
    echo [ACHTUNG] Keine virtuelle Umgebung 'venv' oder '.venv' gefunden!
    echo Bitte zuerst 'python -m venv venv' ausfuehren.
    echo Versuche trotzdem globalen Python zu nutzen...

echo.
echo Starte Webbrowser...
start http://127.0.0.1:8000

echo.
echo Starte Server...
echo (Druecke STRG+C um den Server zu stoppen)
echo.
python -m uvicorn src.api.main:app --reload

pause
