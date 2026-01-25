# Pydantic-Schemas für API Request/Response Validierung

from pydantic import BaseModel, Field, computed_field
from datetime import date, datetime
from typing import Optional


class TransaktionBase(BaseModel):
    """Basis-Schema für Transaktionen"""

    buchungstag: date = Field(..., description="Datum der Buchung")
    beguenstigter: str = Field(..., max_length=200, description="Empfänger/Zahler")
    verwendungszweck: Optional[str] = Field(
        None, max_length=500, description="Verwendungszweck"
    )
    iban_kontonummer: Optional[str] = Field(
        None, max_length=34, description="IBAN oder Kontonummer"
    )
    betrag: float = Field(
        ..., description="Betrag (positiv für Einnahmen, negativ für Ausgaben)"
    )
    waehrung: str = Field("EUR", max_length=3, description="Währungscode")
    beschreibung: Optional[str] = Field(
        None, max_length=500, description="Zusätzliche Beschreibung"
    )
    konto_id: Optional[int] = Field(None, description="ID des zugehörigen Kontos")
    kategorie_id: Optional[int] = Field(None, description="ID der zugeordneten Kategorie")


class TransaktionCreate(TransaktionBase):
    """Schema für das Erstellen einer neuen Transaktion"""

    pass


class TransaktionUpdate(BaseModel):
    """Schema für das Aktualisieren einer bestehenden Transaktion"""

    buchungstag: Optional[date] = None
    beguenstigter: Optional[str] = Field(None, max_length=200)
    verwendungszweck: Optional[str] = Field(None, max_length=500)
    iban_kontonummer: Optional[str] = Field(None, max_length=34)
    betrag: Optional[float] = None
    waehrung: Optional[str] = Field(None, max_length=3)
    beschreibung: Optional[str] = Field(None, max_length=500)
    konto_id: Optional[int] = None
    kategorie_id: Optional[int] = None


class TransaktionResponse(TransaktionBase):
    """Schema für Transaktion-Responses"""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Ermöglicht die Konvertierung von SQLAlchemy-Modellen


class TransaktionSearch(BaseModel):
    """Schema für die Suche nach Transaktionen"""

    buchungstag: Optional[date] = None
    beguenstigter: Optional[str] = None
    verwendungszweck: Optional[str] = None
    iban_kontonummer: Optional[str] = None
    betrag_min: Optional[float] = None
    betrag_max: Optional[float] = None
    typ: Optional[str] = None
    betrag_min_abs: Optional[float] = None
    betrag_max_abs: Optional[float] = None
    waehrung: Optional[str] = None
    konto_name: Optional[str] = None
    beschreibung: Optional[str] = None


# ==================== KONTO SCHEMAS ====================


class KontoBase(BaseModel):
    """Basis-Schema für Konten"""

    kontoname: str = Field(..., max_length=100, description="Name des Kontos")
    kontotyp: str = Field(
        ..., description="Typ des Kontos (Girokonto, Sparkonto, etc.)"
    )
    bankname: Optional[str] = Field(None, max_length=200, description="Name der Bank")
    kontonummer: str = Field(..., max_length=34, description="IBAN des Kontos")
    kontostand: float = Field(0.0, description="Aktueller Kontostand")
    waehrung: str = Field("EUR", max_length=3, description="Währungscode")
    bic: Optional[str] = Field(None, max_length=11, description="BIC/SWIFT Code")
    farbe: str = Field("#06d6a6", description="Farbe für die Darstellung")


class KontoCreate(KontoBase):
    """Schema für das Erstellen eines neuen Kontos"""

    pass


class KontoUpdate(BaseModel):
    """Schema für das Aktualisieren eines Kontos"""

    kontoname: Optional[str] = Field(None, max_length=100)
    kontotyp: Optional[str] = None
    bankname: Optional[str] = Field(None, max_length=200)
    kontonummer: Optional[str] = Field(None, max_length=34)  # IBAN
    kontostand: Optional[float] = None
    waehrung: Optional[str] = Field(None, max_length=3)
    bic: Optional[str] = Field(None, max_length=11)
    farbe: Optional[str] = None


class KontoResponse(KontoBase):
    """Schema für Konto-Responses"""

    id: int
    iban: str
    erstellt_am: datetime
    aktualisiert_am: datetime

    @computed_field
    @property
    def iban_kurz(self) -> str:
        """Gibt die gekürzte IBAN-Darstellung zurück"""
        return f"{self.iban[:4]}...{self.iban[-4:]}" if len(self.iban) > 8 else self.iban

    class Config:
        from_attributes = True


# ==================== CHATBOT SCHEMAS ====================


class ChatMessageRequest(BaseModel):
    """Request-Schema für Chatbot-Nachricht"""

    message: str
    session_id: Optional[str] = "default"

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Wofür gebe ich am meisten Geld aus?",
                "session_id": "user123",
            }
        }


class ChatMessageResponse(BaseModel):
    """Response-Schema für Chatbot-Antwort"""

    response: str
    session_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Du gibst am meisten für Lebensmittel aus...",
                "session_id": "user123",
            }
        }


class ChatResetResponse(BaseModel):
    """Response-Schema für Chat-Reset"""

    status: str
    session_id: str

    class Config:
        json_schema_extra = {
            "example": {"status": "Chat-Verlauf zurückgesetzt", "session_id": "user123"}
        }


class ChatStatusResponse(BaseModel):
    """Response-Schema für Chatbot-Status"""

    api_key_configured: bool
    active_sessions: int
    model_name: str

    class Config:
        json_schema_extra = {
            "example": {
                "api_key_configured": True,
                "active_sessions": 3,
                "model_name": "gemini-2.5-flash",
            }
        }
