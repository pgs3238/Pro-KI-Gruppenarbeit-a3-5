# FastAPI REST API für Transaktionsverwaltung

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from ..database import init_db, SessionLocal, Transaktion
from .schemas import TransaktionCreate, TransaktionUpdate, TransaktionResponse

# FastAPI App initialisieren
app = FastAPI(
    title="Ausgabenverwaltung API",
    description="REST API für die Verwaltung von Finanztransaktionen",
    version="1.0.0"
)

# CORS Middleware für Frontend-Kommunikation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion spezifische Origins angeben
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Datenbank initialisieren beim Start
@app.on_event("startup")
def startup_event():
    init_db()
    print("✓ API gestartet und Datenbank initialisiert")


# Dependency für Datenbank-Session
def get_db():
    """Erstellt eine Datenbank-Session für jeden Request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== API ENDPUNKTE ====================

@app.get("/")
def root():
    """Basis-Endpunkt zur Überprüfung der API"""
    return {
        "message": "Ausgabenverwaltung API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/transactions", response_model=List[TransaktionResponse])
def get_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Gibt alle Transaktionen zurück
    
    - **skip**: Anzahl der Einträge zum Überspringen (Pagination)
    - **limit**: Maximale Anzahl der zurückzugebenden Einträge
    """
    transactions = db.query(Transaktion).offset(skip).limit(limit).all()
    return transactions


@app.get("/transactions/{transaction_id}", response_model=TransaktionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Gibt eine einzelne Transaktion anhand der ID zurück"""
    transaction = db.query(Transaktion).filter(Transaktion.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaktion nicht gefunden")
    return transaction


@app.post("/transactions", response_model=TransaktionResponse, status_code=201)
def create_transaction(
    transaction: TransaktionCreate,
    db: Session = Depends(get_db)
):
    """Erstellt eine neue Transaktion"""
    db_transaction = Transaktion(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@app.put("/transactions/{transaction_id}", response_model=TransaktionResponse)
def update_transaction(
    transaction_id: int,
    transaction_update: TransaktionUpdate,
    db: Session = Depends(get_db)
):
    """Aktualisiert eine bestehende Transaktion"""
    db_transaction = db.query(Transaktion).filter(Transaktion.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaktion nicht gefunden")
    
    # Nur die Felder aktualisieren, die übergeben wurden
    update_data = transaction_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_transaction, key, value)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@app.delete("/transactions/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Löscht eine Transaktion"""
    db_transaction = db.query(Transaktion).filter(Transaktion.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaktion nicht gefunden")
    
    db.delete(db_transaction)
    db.commit()
    return None


@app.get("/transactions/filter/date-range", response_model=List[TransaktionResponse])
def get_transactions_by_date_range(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """Filtert Transaktionen nach Datumsbereich"""
    transactions = db.query(Transaktion).filter(
        Transaktion.buchungstag >= start_date,
        Transaktion.buchungstag <= end_date
    ).all()
    return transactions


@app.get("/transactions/stats/summary")
def get_transaction_summary(db: Session = Depends(get_db)):
    """
    Gibt eine Zusammenfassung der Transaktionen zurück
    - Gesamtsumme Einnahmen
    - Gesamtsumme Ausgaben
    - Saldo
    - Anzahl Transaktionen
    """
    all_transactions = db.query(Transaktion).all()
    
    total_income = sum(t.betrag for t in all_transactions if t.betrag > 0)
    total_expenses = sum(abs(t.betrag) for t in all_transactions if t.betrag < 0)
    balance = total_income - total_expenses
    count = len(all_transactions)
    
    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "balance": round(balance, 2),
        "transaction_count": count
    }
