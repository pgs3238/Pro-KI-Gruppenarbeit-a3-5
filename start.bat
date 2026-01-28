@echo off
echo ==============================================
echo      FINLY - Finanzmanager wird gestartet
echo ==============================================

:: Pruefen ob venv existiert
if not exist "venv" (
    echo [ACHTUNG] Keine virtuelle Umgebung 'venv' gefunden!
    echo Bitte zuerst 'python -m venv venv' ausfuehren.
    echo Versuche trotzdem globalen Python zu nutzen...
) else (
    echo Aktiviere virtuelle Umgebung...
    call venv\Scripts\activate
)

echo.
echo Starte Webbrowser...
start http://127.0.0.1:8000

echo.
echo Starte Server...
echo (Druecke STRG+C um den Server zu stoppen)
echo.
python -m uvicorn src.api.main:app --reload

pause
