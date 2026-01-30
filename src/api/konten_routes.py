# Konten API Routes für FastAPI

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import Konto
from ..database.konto_manager import KontoManager
from .schemas import KontoCreate, KontoUpdate, KontoResponse
from .dependencies import get_db
from .helpers import get_or_404


router = APIRouter(prefix="/konten", tags=["Konten"])

# ==================== ENDPUNKTE ====================

@router.get("", response_model=List[KontoResponse])
# GET /konten - Gibt eine Liste aller Konten zurück (id, kontoname, kontonummer, bankname, kontostand, kontotyp, waehrung, iban, bic, farbe).
def get_konten(db: Session = Depends(get_db)):
    """Alle Konten abrufen (mit Initialstand)"""
    konten = db.query(Konto).all()
    return konten


@router.get("/{konto_id}", response_model=KontoResponse)
# GET /konten/{id} - Gibt ein Konto-Objekt zurück (id, kontoname, kontonummer, bankname, kontostand, kontotyp, waehrung, iban, bic, farbe).
def get_konto(konto_id: int, db: Session = Depends(get_db)):
    """Ein einzelnes Konto abrufen (mit Initialstand)"""
    konto = get_or_404(db, Konto, konto_id, detail="Konto nicht gefunden")
    return konto


@router.post("", response_model=KontoResponse, status_code=201)
# POST /konten - Erstellt ein neues Konto und gibt das erstellte Konto-Objekt zurück.
def create_konto(konto: KontoCreate, db: Session = Depends(get_db)):
    """Neues Konto erstellen"""
    # Prüfe ob Kontoname schon existiert
    existing = db.query(Konto).filter(Konto.kontoname == konto.kontoname).first()
    if existing:
        raise HTTPException(status_code=400, detail="Kontoname existiert bereits")

    # Leere Kontonummer als None speichern (nicht als leerer String)
    kontonummer = konto.kontonummer.strip() if konto.kontonummer else None
    if kontonummer == "":
        kontonummer = None

    new_konto = KontoManager.erstelle_konto(
        session=db,
        kontoname=konto.kontoname,
        kontonummer=kontonummer,
        kontotyp=konto.kontotyp,
        bankname=konto.bankname,
        kontostand=konto.kontostand,
        waehrung=konto.waehrung,
        bic=konto.bic,
    )

    # Speichere die Farbe als zusätzliches Attribut
    new_konto.farbe = konto.farbe
    db.commit()
    db.refresh(new_konto)
    return new_konto


@router.put("/{konto_id}", response_model=KontoResponse)
# PUT /konten/{id} - Aktualisiert ein Konto und gibt das aktualisierte Konto-Objekt zurück.
def update_konto(
    konto_id: int,
    konto_update: KontoUpdate,
    db: Session = Depends(get_db),
):
    """Konto aktualisieren"""
    db_konto = get_or_404(db, Konto, konto_id, detail="Konto nicht gefunden")

    # Prüfe ob neuer Kontoname schon existiert (falls er geändert wird)
    if konto_update.kontoname and konto_update.kontoname != db_konto.kontoname:
        existing = db.query(Konto).filter(
            Konto.kontoname == konto_update.kontoname
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Kontoname existiert bereits")

    update_data = konto_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_konto, key, value)

    db.commit()
    db.refresh(db_konto)
    return db_konto


@router.delete("/{konto_id}",status_code=204)
# DELETE /konten/{id} - Löscht ein Konto samt Transaktionen, gibt keinen Inhalt zurück (204 No Content).
def delete_konto(konto_id: int, db: Session = Depends(get_db)):
    """Konto löschen (mit allen zugehörigen Transaktionen)"""
    success = KontoManager.lösche_konto(db, konto_id)

    if not success:
        raise HTTPException(status_code=404, detail="Konto nicht gefunden")


@router.get("/{konto_id}/saldo")
# GET /konten/{id}/saldo - Gibt ein Dict mit konto_id, initialstand und aktueller_saldo (berechnet aus Transaktionen) zurück.
def get_konto_saldo(konto_id: int, db: Session = Depends(get_db)):
    """Aktuellen Kontostand eines Kontos abrufen (Initialstand + Transaktionen)"""
    konto = get_or_404(db, Konto, konto_id, detail="Konto nicht gefunden")

    # Berechne aktuellen Kontostand aus Transaktionen
    aktueller_saldo = KontoManager.berechne_kontostand_aus_transaktionen(
        db, konto_id, initialstand=konto.kontostand
    )

    return {
        "konto_id": konto_id,
        "initialstand": konto.kontostand,
        "aktueller_saldo": round(aktueller_saldo, 2),
    }


@router.get("/stats/summary")
# GET /konten/stats/summary - Gibt ein Dict mit total_saldo, konto_count und Liste aller Konten (id, kontoname, kontostand, waehrung) zurück.
def get_konto_summary(db: Session = Depends(get_db)):
    """Konto-Zusammenfassung (Gesamtsaldo, Kontenanzahl, etc.)"""
    konten = db.query(Konto).all()

    if not konten:
        return {"total_saldo": 0.0, "konto_count": 0, "konten": []}

    return {
        "total_saldo": round(sum(k.kontostand for k in konten), 2),
        "konto_count": len(konten),
        "konten": [
            {
                "id": k.id,
                "kontoname": k.kontoname,
                "kontostand": k.kontostand,
                "waehrung": k.waehrung,
            }
            for k in konten
        ],
    }
