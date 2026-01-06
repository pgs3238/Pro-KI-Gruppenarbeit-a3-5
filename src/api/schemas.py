# Pydantic-Schemas für API Request/Response Validierung

from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class TransaktionBase(BaseModel):
    """Basis-Schema für Transaktionen"""
    buchungstag: date = Field(..., description="Datum der Buchung")
    beguenstigter: str = Field(..., max_length=200, description="Empfänger/Zahler")
    verwendungszweck: Optional[str] = Field(None, max_length=500, description="Verwendungszweck")
    iban_kontonummer: Optional[str] = Field(None, max_length=34, description="IBAN oder Kontonummer")
    betrag: float = Field(..., description="Betrag (positiv für Einnahmen, negativ für Ausgaben)")
    waehrung: str = Field("EUR", max_length=3, description="Währungscode")
    beschreibung: Optional[str] = Field(None, max_length=500, description="Zusätzliche Beschreibung")


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
