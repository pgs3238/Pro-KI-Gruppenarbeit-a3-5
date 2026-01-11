"""
FastAPI Router für Chatbot-Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
import os
from dotenv import load_dotenv

from .dependencies import get_db
from .schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatResetResponse,
    ChatStatusResponse,
)
from ..chatbot.gemini_client import GeminiChatbot

# Environment Variables laden
load_dotenv()

# Router erstellen
router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

# Session-Management (In-Memory für Prototyp)
# Key = session_id, Value = GeminiChatbot-Instanz
chatbot_sessions: Dict[str, GeminiChatbot] = {}


def get_or_create_chatbot(session_id: str, db: Session) -> GeminiChatbot:
    """
    Holt eine existierende Chatbot-Session oder erstellt eine neue.

    Args:
        session_id: Eindeutige Session-ID
        db: Datenbank-Session

    Returns:
        GeminiChatbot-Instanz

    Raises:
        HTTPException: Wenn kein API-Key konfiguriert ist
    """
    # Prüfe ob Session existiert
    if session_id in chatbot_sessions:
        return chatbot_sessions[session_id]

    # API-Key aus Environment holen
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY nicht konfiguriert. Bitte .env-Datei prüfen.",
        )

    # Neue Chatbot-Session erstellen
    chatbot = GeminiChatbot(api_key=api_key, session=db)
    chatbot_sessions[session_id] = chatbot

    return chatbot


# ==================== ENDPOINTS ====================


@router.post("/message", response_model=ChatMessageResponse)
def send_message(request: ChatMessageRequest, db: Session = Depends(get_db)):
    """
    Sendet eine Nachricht an den Chatbot und erhält eine Antwort.

    - **message**: Benutzernachricht (z.B. "Wofür gebe ich am meisten aus?")
    - **session_id**: Optional - Ermöglicht mehrere parallele Chat-Sessions

    Der Chatbot nutzt Function Calling um auf Finanzdaten zuzugreifen.
    """
    try:
        # Chatbot-Session holen oder erstellen
        chatbot = get_or_create_chatbot(request.session_id, db)

        # Nachricht senden
        response = chatbot.send_message(request.message)

        return ChatMessageResponse(response=response, session_id=request.session_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Fehler bei Chatbot-Verarbeitung: {str(e)}"
        )


@router.post("/reset", response_model=ChatResetResponse)
def reset_chat(session_id: str = "default"):
    """
    Setzt den Chat-Verlauf einer Session zurück.

    - **session_id**: Session-ID (default: "default")

    Löscht die gesamte Chat-Historie, aber behält die Session-Konfiguration.
    """
    if session_id in chatbot_sessions:
        chatbot_sessions[session_id].reset_chat()
        status_message = "Chat-Verlauf zurückgesetzt"
    else:
        status_message = "Keine aktive Session gefunden (bereits leer)"

    return ChatResetResponse(status=status_message, session_id=session_id)


@router.get("/status", response_model=ChatStatusResponse)
def get_status():
    """
    Gibt den Status des Chatbot-Services zurück.

    Zeigt:
    - Ob ein API-Key konfiguriert ist
    - Anzahl aktiver Chat-Sessions
    - Verwendetes Modell
    """
    api_key_configured = bool(os.getenv("GEMINI_API_KEY"))

    return ChatStatusResponse(
        api_key_configured=api_key_configured,
        active_sessions=len(chatbot_sessions),
        model_name="gemini-2.5-flash",
    )
