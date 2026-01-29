#!/bin/bash

echo "=============================================="
echo "     FINLY - Finanzmanager wird gestartet"
echo "=============================================="

# Prüfen ob venv existiert
if [ -d "venv" ]; then
  echo "Aktiviere virtuelle Umgebung 'venv'..."
  source venv/bin/activate
elif [ -d ".venv" ]; then
  echo "Aktiviere virtuelle Umgebung '.venv'..."
  source .venv/bin/activate
else
    echo "[ACHTUNG] Keine virtuelle Umgebung 'venv' gefunden!"
    echo "Bitte zuerst 'python3 -m venv venv' ausführen."
    echo "Versuche trotzdem globalen Python zu nutzen..."
fi

echo ""
echo "Starte Webbrowser..."
if which xdg-open > /dev/null; then
  xdg-open http://127.0.0.1:8000
elif which open > /dev/null; then
  open http://127.0.0.1:8000
fi

echo ""
echo "Starte Server..."
echo "(Drücke STRG+C um den Server zu stoppen)"
echo ""
python3 -m uvicorn src.api.main:app --reload
