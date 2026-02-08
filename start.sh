#!/bin/bash

echo "=============================================="
echo "     FINLY - Finanzmanager wird gestartet"
echo "=============================================="

# Pruefen ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "[FEHLER] Python ist nicht installiert oder nicht im PATH!"
    echo "Bitte Python 3.9 - 3.13 installieren: https://www.python.org/downloads/"
    exit 1
fi

echo "Python gefunden - OK"
echo ""

# Pruefen ob venv existiert
if [ -d "venv" ]; then
    echo "Aktiviere virtuelle Umgebung 'venv'..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Aktiviere virtuelle Umgebung '.venv'..."
    source .venv/bin/activate
else
    echo "[ACHTUNG] Keine virtuelle Umgebung gefunden!"
    echo "Erstelle neue virtuelle Umgebung..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Pruefen ob Dependencies installiert sind
if ! python3 -c "import uvicorn" &> /dev/null; then
    echo "Installiere Abhaengigkeiten..."
    pip install -r requirements.txt
    # Nochmal pruefen ob uvicorn jetzt importiert werden kann
    if ! python3 -c "import uvicorn" &> /dev/null; then
        echo "[FEHLER] Installation der Abhaengigkeiten fehlgeschlagen!"
        exit 1
    fi
    echo "Installation erfolgreich!"
fi

echo ""
echo "Starte Server..."
echo "(Druecke STRG+C um den Server zu stoppen)"
echo ""

# Starte Server im Hintergrund und oeffne nach 3 Sekunden den Browser
python3 -m uvicorn src.api.main:app --reload &
SERVER_PID=$!

echo "Warte auf Server-Start..."
sleep 3

echo "Oeffne Browser..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://127.0.0.1:8000
elif command -v open &> /dev/null; then
    open http://127.0.0.1:8000
fi

echo ""
echo "Server laeuft auf http://127.0.0.1:8000"
echo ""

# Warte auf Server-Prozess
wait $SERVER_PID
