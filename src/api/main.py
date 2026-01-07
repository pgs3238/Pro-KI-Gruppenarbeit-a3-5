# FastAPI REST API für Transaktionsverwaltung

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Literal
from datetime import date

from ..database import init_db, SessionLocal, Transaktion
from ..database.search import search_transaktionen
from .schemas import TransaktionCreate, TransaktionUpdate, TransaktionResponse, TransaktionSearch

# ==================== SETUP ====================

app = FastAPI(
    title="Ausgabenverwaltung API",
    description="REST API für die Verwaltung von Finanztransaktionen",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()
    print("✓ API gestartet")


def get_db():
    """Datenbank-Session für jeden Request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== HILFSFUNKTIONEN ====================

def get_transaction_or_404(transaction_id: int, db: Session):
    """Transaktion laden oder 404 werfen"""
    transaction = db.query(Transaktion).filter(Transaktion.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaktion nicht gefunden")
    return transaction


# ==================== ENDPUNKTE: BASIC ====================

@app.get("/")
def root():
    """API Status"""
    return {"message": "Ausgabenverwaltung API", "version": "1.0.0", "docs": "/docs"}


# ==================== ENDPUNKTE: CRUD ====================

@app.get("/transactions", response_model=List[TransaktionResponse])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Alle Transaktionen (mit Pagination)"""
    return db.query(Transaktion).offset(skip).limit(limit).all()


@app.get("/transactions/{transaction_id}", response_model=TransaktionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Eine Transaktion abrufen"""
    return get_transaction_or_404(transaction_id, db)


@app.post("/transactions", response_model=TransaktionResponse, status_code=201)
def create_transaction(transaction: TransaktionCreate, db: Session = Depends(get_db)):
    """Neue Transaktion erstellen"""
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
    """Transaktion aktualisieren"""
    db_transaction = get_transaction_or_404(transaction_id, db)
    
    update_data = transaction_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_transaction, key, value)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@app.delete("/transactions/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Transaktion löschen"""
    db_transaction = get_transaction_or_404(transaction_id, db)
    db.delete(db_transaction)
    db.commit()


# ==================== ENDPUNKTE: FILTER & STATISTIKEN ====================

@app.get("/transactions/filter/date-range", response_model=List[TransaktionResponse])
def get_transactions_by_date_range(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """Transaktionen nach Datumsbereich filtern"""
    return db.query(Transaktion).filter(
        Transaktion.buchungstag >= start_date,
        Transaktion.buchungstag <= end_date
    ).all()


@app.get("/transactions/stats/summary")
def get_transaction_summary(db: Session = Depends(get_db)):
    """Finanz-Zusammenfassung"""
    transactions = db.query(Transaktion).all()
    
    total_income = sum(t.betrag for t in transactions if t.betrag > 0)
    total_expenses = sum(abs(t.betrag) for t in transactions if t.betrag < 0)
    
    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "balance": round(total_income - total_expenses, 2),
        "transaction_count": len(transactions)
    }


# ==================== ENDPUNKTE: SEARCH ====================

@app.post("/transactions/search", response_model=List[TransaktionResponse])
def search_transactions(
    search_params: TransaktionSearch,
    db: Session = Depends(get_db)
):
    """Transaktionen mit erweiterten Suchfiltern"""
    return search_transaktionen(
        session=db,
        buchungstag=search_params.buchungstag,
        beguenstigter=search_params.beguenstigter,
        verwendungszweck=search_params.verwendungszweck,
        iban_kontonummer=search_params.iban_kontonummer,
        betrag_min=search_params.betrag_min,
        betrag_max=search_params.betrag_max,
        typ=search_params.typ,
        betrag_min_abs=search_params.betrag_min_abs,
        betrag_max_abs=search_params.betrag_max_abs,
        waehrung=search_params.waehrung,
    )

# ==================== ENDPUNKTE: SANKEY DIAGRAMM ====================

@app.get("/transactions/sankey-data")
def get_sankey_data(db: Session = Depends(get_db)):
    """Liefert Daten für ein Sankey-Diagramm: Kategorien → Einnahmen/Ausgaben"""
    transactions = db.query(Transaktion).all()
    
    if not transactions:
        return {"nodes": [], "links": []}
    
    # Sammle Kategorien und Beträge
    category_flows = {}  # {kategorie: {expense: betrag, income: betrag}}
    
    for t in transactions:
        category = t.beschreibung or "Sonstiges"
        if category not in category_flows:
            category_flows[category] = {"expense": 0, "income": 0}
        
        if t.betrag < 0:
            category_flows[category]["expense"] += abs(t.betrag)
        else:
            category_flows[category]["income"] += t.betrag
    
    # Definiere Node-Namen
    node_names = ["Kategorien"]
    node_names.extend(sorted(category_flows.keys()))
    node_names.extend(["Ausgaben", "Einnahmen"])
    
    # Erstelle Links (Kategorien → Ausgaben/Einnahmen)
    links = []
    
    for idx, (category, flows) in enumerate(sorted(category_flows.items()), 1):
        # Ausgaben-Link
        if flows["expense"] > 0:
            links.append({
                "source": idx,
                "target": len(node_names) - 2,  # Index von "Ausgaben"
                "value": round(flows["expense"], 2)
            })
        
        # Einnahmen-Link
        if flows["income"] > 0:
            links.append({
                "source": idx,
                "target": len(node_names) - 1,  # Index von "Einnahmen"
                "value": round(flows["income"], 2)
            })
    
    # Erstelle Nodes mit Farben
    node_colors = ["#1f77b4"]  # Kategorien - Blau
    node_colors.extend(["#aec7e8"] * len(category_flows))  # Kategorien - Hellblau
    node_colors.append("#ff7f0e")  # Ausgaben - Orange
    node_colors.append("#2ca02c")  # Einnahmen - Grün
    
    return {
        "nodes": [{"name": name, "color": color} for name, color in zip(node_names, node_colors)],
        "links": links
    }