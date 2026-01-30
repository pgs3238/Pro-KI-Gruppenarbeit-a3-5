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
)

echo.
echo Starte Server...
echo (Druecke STRG+C um den Server zu stoppen)
echo.

:: Starte Server im Hintergrund und oeffne nach 3 Sekunden den Browser
start /B python -m uvicorn src.api.main:app --reload

echo Warte auf Server-Start...
timeout /t 3 /nobreak >nul

echo Öffne Browser...
start http://127.0.0.1:8000

echo.
echo Server laeuft auf http://127.0.0.1:8000
echo.

pause
