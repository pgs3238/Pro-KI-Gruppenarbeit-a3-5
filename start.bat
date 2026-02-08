@echo off
echo ==============================================
echo      FINLY - Finanzmanager wird gestartet
echo ==============================================

:: Pruefen ob Python installiert ist
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [FEHLER] Python ist nicht installiert oder nicht im PATH!
    echo Bitte Python 3.9 - 3.13 installieren: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python gefunden - OK
echo.

:: Pruefen ob venv existiert
if exist "venv" (
    echo Aktiviere virtuelle Umgebung 'venv'...
    call venv\Scripts\activate
) else if exist ".venv" (
    echo Aktiviere virtuelle Umgebung '.venv'...
    call .venv\Scripts\activate
) else (
    echo [ACHTUNG] Keine virtuelle Umgebung gefunden!
    echo Erstelle neue virtuelle Umgebung...
    python -m venv venv
    call venv\Scripts\activate
)

:: Pruefen ob Dependencies installiert sind
python -c "import uvicorn" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installiere Abhaengigkeiten...
    pip install -r requirements.txt
    :: Nochmal pruefen ob uvicorn jetzt importiert werden kann
    python -c "import uvicorn" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [FEHLER] Installation der Abhaengigkeiten fehlgeschlagen!
        pause
        exit /b 1
    )
    echo Installation erfolgreich!
)

echo.
echo Starte Server...
echo (Druecke STRG+C um den Server zu stoppen)
echo.

:: Starte Server im Hintergrund und oeffne nach 3 Sekunden den Browser
start /B python -m uvicorn src.api.main:app --reload

echo Warte auf Server-Start...
timeout /t 3 /nobreak >nul

echo Oeffne Browser...
start http://127.0.0.1:8000

echo.
echo Server laeuft auf http://127.0.0.1:8000
echo.

pause
