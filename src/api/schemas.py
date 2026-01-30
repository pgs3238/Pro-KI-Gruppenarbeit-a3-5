# Pydantic-Schemas für API Request/Response Validierung

from pydantic import BaseModel, Field, computed_field
from datetime import date, datetime
from typing import Optional, List


# Basis-Schema: Enthält alle gemeinsamen Felder für Transaktionen (buchungstag, beguenstigter, betrag, etc.).
class TransaktionBase(BaseModel):
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


# Request-Schema: Zum Erstellen neuer Transaktionen, erbt alle Felder von TransaktionBase.
class TransaktionCreate(TransaktionBase):
    pass


# Request-Schema: Zum Aktualisieren von Transaktionen, alle Felder optional.
class TransaktionUpdate(BaseModel):
    buchungstag: Optional[date] = None
    beguenstigter: Optional[str] = Field(None, max_length=200)
    verwendungszweck: Optional[str] = Field(None, max_length=500)
    iban_kontonummer: Optional[str] = Field(None, max_length=34)
    betrag: Optional[float] = None
    waehrung: Optional[str] = Field(None, max_length=3)
    beschreibung: Optional[str] = Field(None, max_length=500)
    konto_id: Optional[int] = None
    kategorie_id: Optional[int] = None


# Response-Schema: Gibt Transaktion mit id und created_at zurück, wird von SQLAlchemy-Model konvertiert.
class TransaktionResponse(TransaktionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Ermöglicht die Konvertierung von SQLAlchemy-Modellen


# Request-Schema: Für erweiterte Suche mit optionalen Filtern (datum, betrag, kategorie, etc.).
class TransaktionSearch(BaseModel):
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
    kategorie_name: Optional[str] = None


# ==================== KONTO SCHEMAS ====================


# Basis-Schema: Enthält alle gemeinsamen Felder für Konten (kontoname, kontotyp, bankname, kontostand, etc.).
class KontoBase(BaseModel):
    kontoname: str = Field(..., max_length=100, description="Name des Kontos")
    kontotyp: str = Field(
        ..., description="Typ des Kontos (Girokonto, Sparkonto, etc.)"
    )
    bankname: Optional[str] = Field(None, max_length=200, description="Name der Bank")
    kontonummer: Optional[str] = Field(None, max_length=34, description="IBAN des Kontos (optional)")
    kontostand: float = Field(0.0, description="Aktueller Kontostand")
    waehrung: str = Field("EUR", max_length=3, description="Währungscode")
    bic: Optional[str] = Field(None, max_length=11, description="BIC/SWIFT Code")
    farbe: str = Field("#06d6a6", description="Farbe für die Darstellung")


# Request-Schema: Zum Erstellen neuer Konten, erbt alle Felder von KontoBase.
class KontoCreate(KontoBase):
    pass


# Request-Schema: Zum Aktualisieren von Konten, alle Felder optional.
class KontoUpdate(BaseModel):
    kontoname: Optional[str] = Field(None, max_length=100)
    kontotyp: Optional[str] = None
    bankname: Optional[str] = Field(None, max_length=200)
    kontonummer: Optional[str] = Field(None, max_length=34)  # IBAN
    kontostand: Optional[float] = None
    waehrung: Optional[str] = Field(None, max_length=3)
    bic: Optional[str] = Field(None, max_length=11)
    farbe: Optional[str] = None


# Response-Schema: Gibt Konto mit id, iban, iban_kurz, erstellt_am, aktualisiert_am zurück.
class KontoResponse(KontoBase):
    id: int
    iban: Optional[str] = None
    erstellt_am: datetime
    aktualisiert_am: datetime

    @computed_field
    @property
    def iban_kurz(self) -> Optional[str]:
        """Gibt die gekürzte IBAN-Darstellung zurück"""
        if not self.iban:
            return None
        return f"{self.iban[:4]}...{self.iban[-4:]}" if len(self.iban) > 8 else self.iban

    class Config:
        from_attributes = True


# ==================== CHATBOT SCHEMAS ====================


# Request-Schema: Für Chatbot-Nachrichten mit message und optionaler session_id.
class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Wofür gebe ich am meisten Geld aus?",
                "session_id": "user123",
            }
        }


# Response-Schema: Chatbot-Antwort mit response-Text und session_id.
class ChatMessageResponse(BaseModel):
    response: str
    session_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Du gibst am meisten für Lebensmittel aus...",
                "session_id": "user123",
            }
        }


# Response-Schema: Bestätigung für Chat-Reset mit status und session_id.
class ChatResetResponse(BaseModel):
    status: str
    session_id: str

    class Config:
        json_schema_extra = {
            "example": {"status": "Chat-Verlauf zurückgesetzt", "session_id": "user123"}
        }


# Response-Schema: Chatbot-Status mit api_key_configured, active_sessions, model_name.
class ChatStatusResponse(BaseModel):
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


# ==================== CATEGORY SCHEMAS ====================


# Request-Schema: Zum Erstellen von Kategorien mit name, category_type, icon, farbe.
class CategoryCreate(BaseModel):
    name: str
    category_type: str  # "Ausgabe" oder "Einnahme"
    icon: str = "🏷️"  # Default Icon
    farbe: str = "#06d6a6"  # Default Farbe


# Response-Schema: Gibt Kategorie mit id, name, category_type, icon, farbe zurück.
class CategoryResponse(BaseModel):
    id: int
    name: str
    category_type: str
    icon: str = "🏷️"
    farbe: str = "#06d6a6"

    class Config:
        from_attributes = True


# Response-Schema: Gibt Kategorie-Regeln mit id, category_name, keywords zurück.
class CategoryRulesResponse(BaseModel):
    id: int
    category_name: str
    keywords: list[str]

    class Config:
        from_attributes = True


# Request-Schema: Enthält ein einzelnes Keyword für Kategorie-Regeln.
class KeywordRequest(BaseModel):
    keyword: str


# ==================== SETTINGS SCHEMAS ====================


class ApiKeyUpdate(BaseModel):
    """Schema für API-Key Update"""
    api_key: str


class ApiKeyResponse(BaseModel):
    """Schema für API-Key Response"""
    success: bool
    message: str


# ==================== ZINSRECHNER SCHEMAS ====================


class VergleichParameter(BaseModel):
    startkapital: float
    zinssatz: float
    intervall: str
    einzahlung: float
    laufzeit: int
    kontostandTyp: str


class VergleichPunkt(BaseModel):
    jahr: int
    periode: int
    kapital: float
    einzahlungGesamt: float
    zinsenGesamt: float


class VergleichSpeichern(BaseModel):
    db_nummer: int
    verlauf: List[VergleichPunkt]
    parameter: VergleichParameter


class KontoInfo(BaseModel):
    iban: str
    iban_kurz: str
    kontostand: float
    anzahl_transaktionen: int
    waehrung: str

