"""
FastAPI Router für Einstellungen (z.B. API-Keys)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from pathlib import Path
from dotenv import load_dotenv, set_key

# Router erstellen
router = APIRouter(prefix="/settings", tags=["Settings"])


class ApiKeyUpdate(BaseModel):
    """Schema für API-Key Update"""
    api_key: str


class ApiKeyResponse(BaseModel):
    """Schema für API-Key Response"""
    success: bool
    message: str


def get_env_path() -> Path:
    """Gibt den Pfad zur .env-Datei zurück"""
    # Gehe von src/api nach root
    current_dir = Path(__file__).parent
    root_dir = current_dir.parent.parent
    env_path = root_dir / ".env"
    
    # Erstelle .env falls nicht vorhanden
    if not env_path.exists():
        env_path.touch()
        
    return env_path


@router.post("/api-key", response_model=ApiKeyResponse)
def update_api_key(data: ApiKeyUpdate):
    """
    Speichert den Gemini API-Key in der .env-Datei.
    
    - **api_key**: Der neue Gemini API-Key
    
    Der Key wird in der .env-Datei als GEMINI_API_KEY gespeichert.
    """
    try:
        # Validierung
        if not data.api_key or len(data.api_key.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="API-Key darf nicht leer sein"
            )
        
        # .env-Datei Pfad ermitteln
        env_path = get_env_path()
        
        # API-Key in .env speichern/aktualisieren
        set_key(str(env_path), "GEMINI_API_KEY", data.api_key.strip())
        
        # Environment Variable direkt aktualisieren
        os.environ["GEMINI_API_KEY"] = data.api_key.strip()
        
        return ApiKeyResponse(
            success=True,
            message="API-Key erfolgreich gespeichert"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Speichern des API-Keys: {str(e)}"
        )


@router.get("/api-key/status")
def get_api_key_status():
    """
    Prüft ob ein API-Key konfiguriert ist (ohne den Key preiszugeben).
    """
    # Environment neu laden
    load_dotenv(override=True)
    
    api_key = os.getenv("GEMINI_API_KEY")
    is_configured = bool(api_key and len(api_key.strip()) > 0)
    
    # Zeige nur ersten und letzten 4 Zeichen wenn konfiguriert
    masked_key = None
    if is_configured and api_key:
        if len(api_key) > 8:
            masked_key = f"{api_key[:4]}...{api_key[-4:]}"
        else:
            masked_key = "****"
    
    return {
        "configured": is_configured,
        "masked_key": masked_key
    }


@router.get("/db-status")
def get_db_status():
    """
    Prüft den Status der Datenbankverbindung.
    Gibt connected=True zurück wenn die DB erreichbar ist.
    """
    from sqlalchemy import text
    from ..database import SessionLocal
    
    try:
        # Versuche eine Verbindung herzustellen und eine einfache Query auszuführen
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "connected": True,
            "status": "online",
            "message": "Datenbankverbindung aktiv"
        }
    except Exception as e:
        return {
            "connected": False,
            "status": "offline",
            "message": f"Datenbankfehler: {str(e)}"
        }

