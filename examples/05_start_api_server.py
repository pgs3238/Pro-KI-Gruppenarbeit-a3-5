# Beispiel: Starten des API-Servers

"""
Dieses Skript startet den FastAPI-Server zur Bereitstellung der REST API.

Verwendung:
    python examples/05_start_api_server.py
    
Oder direkt mit uvicorn:
    uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
"""

import sys
import os
from pathlib import Path

# Füge das Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn

if __name__ == "__main__":
    print("🚀 Starte API Server...")
    print("📖 API Dokumentation: http://localhost:8000/docs")
    print("📊 Alternative Dokumentation: http://localhost:8000/redoc")
    print("\nDrücke CTRL+C zum Beenden\n")
    
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Automatischer Reload bei Code-Änderungen
    )
