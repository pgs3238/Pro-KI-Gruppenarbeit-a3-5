# FastAPI REST API für Transaktionsverwaltung

from fastapi import UploadFile, File, Form, FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pathlib import Path
import tempfile, json

from ..database import init_db, Transaktion, Konto
from ..database.search import search_transaktionen
from ..database.konto_manager import KontoManager
from ..database.csv_importer import CSVTransaktionImporter
from ..categories.auto_categorizer_service import get_auto_categorizer_service
from .schemas import (
    TransaktionCreate,
    TransaktionUpdate,
    TransaktionResponse,
    TransaktionSearch,
    KontoCreate,
    KontoUpdate,
    KontoResponse,
)
from .dependencies import get_db
try:
    from . import chatbot_routes
    CHATBOT_AVAILABLE = True
except ImportError:
    CHATBOT_AVAILABLE = False
    print("⚠️ Chatbot nicht verfügbar (Gemini SDK fehlt)")

try:
    from . import category_routes
    CATEGORY_ROUTES_AVAILABLE = True
except ImportError:
    CATEGORY_ROUTES_AVAILABLE = False
    print("⚠️ Category Routes nicht verfügbar")

from . import zinsrechner_routes

# ==================== SETUP ====================

app = FastAPI(
    title="Ausgabenverwaltung API",
    description="REST API für die Verwaltung von Finanztransaktionen",
    version="1.0.0",
)

# Globale Service-Instanz
auto_categorizer = get_auto_categorizer_service()

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

    # Auto-Kategorisierung beim Start
    state = auto_categorizer.get_categorization_state()

    # Kategorisieren wenn:
    # - Transaktionen vorhanden sind UND
    # - entweder has_new_transactions > 0 ODER has_new_transactions ist None (noch nie kategorisiert)
    with next(get_db()) as db:
        transaction_count = db.query(Transaktion).count()

    if transaction_count > 0 and (
        state["has_new_transactions"] is None or state["has_new_transactions"] > 0
    ):
        auto_categorizer.run_full_categorization_cycle()


# ==================== STATIC FILES ====================

# Basis-Verzeichnis ermitteln (2 Ebenen nach oben von src/api/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Static Files (CSS, JS, Bilder)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Templates als Static Files (HTML-Dateien direkt erreichbar)
app.mount("/templates", StaticFiles(directory=str(BASE_DIR / "templates"), html=True), name="templates")

# Root-Route für index.html
@app.get("/")
async def root():
    from fastapi.responses import FileResponse
    return FileResponse(str(BASE_DIR / "templates" / "index.html"))


# ==================== ROUTER ====================

# Router registrieren
if CHATBOT_AVAILABLE:
    app.include_router(chatbot_routes.router, prefix="/api")
app.include_router(zinsrechner_routes.router, prefix="/api")

# Category-Router registrieren
if CATEGORY_ROUTES_AVAILABLE:
    app.include_router(category_routes.router)

# Mount static files und templates
# Finde das Root-Verzeichnis (2 Ebenen über dem src/api Ordner)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Mount templates (für direkten Zugriff auf HTML)
if TEMPLATES_DIR.exists():
    app.mount("/templates", StaticFiles(directory=str(TEMPLATES_DIR)), name="templates")


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


@app.get("/transactions")
def get_transactions(skip: int = 0, limit: int = 1000, days: int = 30, db: Session = Depends(get_db)):
    """Alle Transaktionen (mit optional Datumsfilter für letzte N Tage)"""
    from datetime import datetime, timedelta
    
    # Wenn days > 0, filtere nach den letzten N Tagen
    if days > 0:
        cutoff_date = datetime.now().date() - timedelta(days=days)
        return db.query(Transaktion).filter(Transaktion.buchungstag >= cutoff_date).offset(skip).limit(limit).all()
    
    return db.query(Transaktion).offset(skip).limit(limit).all()


@app.get("/transactions/formatted/list")
def get_transactions_formatted(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Alle Transaktionen mit formatierten Werten für Frontend"""
    transactions = db.query(Transaktion).order_by(Transaktion.buchungstag.desc()).offset(skip).limit(limit).all()
    konten = db.query(Konto).all()
    konto_map = {k.id: k.kontoname for k in konten}
    
    formatted = []
    for t in transactions:
        # Formatiere Datum als dd.mm.yyyy
        datum = t.buchungstag.strftime("%d.%m.%Y")
        
        # Formatiere Betrag mit + und €
        betrag_class = "positiv" if t.betrag >= 0 else "negativ"
        betrag_text = ('+' if t.betrag >= 0 else '') + f"{t.betrag:.2f}".replace('.', ',') + '€'
        
        # IBAN formatieren (mit Leerzeichen alle 4 Zeichen)
        iban = t.iban_kontonummer or '-'
        if len(iban) > 4:
            iban = ' '.join([iban[i:i+4] for i in range(0, len(iban), 4)])
        
        # Kategorie: Nutze kategorie_id und lade den Namen via Relationship
        kategorie = '-'
        if t.kategorie_id and t.kategorie:
            kategorie = t.kategorie.name
        
        # Kontoname auflösen
        kontoname = konto_map.get(t.konto_id, '-') if t.konto_id else '-'
        
        formatted.append({
            "id": t.id,
            "datum": datum,
            "beguenstigter": t.beguenstigter,
            "iban": iban,
            "konto": kontoname,
            "verwendungszweck": t.verwendungszweck or '-',
            "kategorie": kategorie,
            "betrag": betrag_text,
            "betrag_class": betrag_class
        })
    
    return formatted


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

    # Auto-Kategorisierung: Counter erhöhen und prüfen
    auto_categorizer.increment_transaction_counter()

    # Prüfe ob Schwelle erreicht (5 Transaktionen)
    if auto_categorizer.should_trigger_categorization(threshold=5):
        auto_categorizer.run_full_categorization_cycle()

    return db_transaction


@app.put("/transactions/{transaction_id}", response_model=TransaktionResponse)
def update_transaction(
    transaction_id: int,
    transaction_update: TransaktionUpdate,
    db: Session = Depends(get_db),
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
    start_date: date, end_date: date, db: Session = Depends(get_db)
):
    """Transaktionen nach Datumsbereich filtern"""
    return (
        db.query(Transaktion)
        .filter(
            Transaktion.buchungstag >= start_date, Transaktion.buchungstag <= end_date
        )
        .all()
    )


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
        "transaction_count": len(transactions),
    }


# ==================== ENDPUNKTE: SEARCH ====================


@app.post("/transactions/search", response_model=List[TransaktionResponse])
def search_transactions(
    search_params: TransaktionSearch, db: Session = Depends(get_db)
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
        konto_name=search_params.konto_name,
        beschreibung=search_params.beschreibung,
    )


# ==================== ENDPUNKTE: SANKEY DIAGRAMM ====================


@app.get("/transactions/sankey-data")
def get_sankey_data(db: Session = Depends(get_db)):
    """Liefert Daten für ein Sankey-Diagramm: Kategorien → Einnahmen/Ausgaben"""
    transactions = db.query(Transaktion).all()

    if not transactions:
        return {"nodes": [], "links": []}

    # Sammle Kategorien und Beträge
    category_flows = {}  # {kategorie_name: {expense: betrag, income: betrag}}

    for t in transactions:
        # Nutze kategorie.name falls kategorie_id gesetzt, sonst "Unbekannt"
        category = "Unbekannt"
        if t.kategorie_id and t.kategorie:
            category = t.kategorie.name
        
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
            links.append(
                {
                    "source": idx,
                    "target": len(node_names) - 2,  # Index von "Ausgaben"
                    "value": round(flows["expense"], 2),
                }
            )

        # Einnahmen-Link
        if flows["income"] > 0:
            links.append(
                {
                    "source": idx,
                    "target": len(node_names) - 1,  # Index von "Einnahmen"
                    "value": round(flows["income"], 2),
                }
            )

    # Erstelle Nodes mit Farben
    node_colors = ["#1f77b4"]  # Kategorien - Blau
    node_colors.extend(["#aec7e8"] * len(category_flows))  # Kategorien - Hellblau
    node_colors.append("#ff7f0e")  # Ausgaben - Orange
    node_colors.append("#2ca02c")  # Einnahmen - Grün

    return {
        "nodes": [
            {"name": name, "color": color}
            for name, color in zip(node_names, node_colors)
        ],
        "links": links,
    }


# ==================== ENDPUNKTE: KONTEN ====================


def get_konto_or_404(konto_id: int, db: Session):
    """Konto laden oder 404 werfen"""
    konto = db.query(Konto).filter(Konto.id == konto_id).first()
    if not konto:
        raise HTTPException(status_code=404, detail="Konto nicht gefunden")
    return konto


@app.get("/konten", response_model=List[KontoResponse])
def get_konten(db: Session = Depends(get_db)):
    """Alle Konten abrufen (mit Initialstand)"""
    konten = db.query(Konto).all()
    return konten


@app.get("/konten/{konto_id}", response_model=KontoResponse)
def get_konto(konto_id: int, db: Session = Depends(get_db)):
    """Ein einzelnes Konto abrufen (mit Initialstand)"""
    konto = get_konto_or_404(konto_id, db)
    return konto


@app.post("/konten", response_model=KontoResponse, status_code=201)
def create_konto(konto: KontoCreate, db: Session = Depends(get_db)):
    """Neues Konto erstellen"""
    # Prüfe ob Kontoname schon existiert
    existing = db.query(Konto).filter(Konto.kontoname == konto.kontoname).first()
    if existing:
        raise HTTPException(status_code=400, detail="Kontoname existiert bereits")

    # Prüfe ob Kontonummer (IBAN) schon existiert
    existing_iban = (
        db.query(Konto).filter(Konto.kontonummer == konto.kontonummer).first()
    )
    if existing_iban:
        raise HTTPException(status_code=400, detail="Kontonummer existiert bereits")

    new_konto = KontoManager.erstelle_konto(
        session=db,
        kontoname=konto.kontoname,
        kontonummer=konto.kontonummer,
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


@app.put("/konten/{konto_id}", response_model=KontoResponse)
def update_konto(
    konto_id: int, konto_update: KontoUpdate, db: Session = Depends(get_db)
):
    """Konto aktualisieren"""
    db_konto = get_konto_or_404(konto_id, db)

    # Prüfe ob neuer Kontoname schon existiert (falls er geändert wird)
    if konto_update.kontoname and konto_update.kontoname != db_konto.kontoname:
        existing = (
            db.query(Konto).filter(Konto.kontoname == konto_update.kontoname).first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Kontoname existiert bereits")

    update_data = konto_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_konto, key, value)

    db.commit()
    db.refresh(db_konto)
    return db_konto


@app.delete("/konten/{konto_id}", status_code=204)
def delete_konto(konto_id: int, db: Session = Depends(get_db)):
    """Konto löschen (mit allen zugehörigen Transaktionen)"""
    success = KontoManager.lösche_konto(db, konto_id)

    if not success:
        raise HTTPException(status_code=404, detail="Konto nicht gefunden")


@app.get("/konten/{konto_id}/saldo")
def get_konto_saldo(konto_id: int, db: Session = Depends(get_db)):
    """Aktuellen Kontostand eines Kontos abrufen (Initialstand + Transaktionen)"""
    konto = get_konto_or_404(konto_id, db)

    # Berechne aktuellen Kontostand aus Transaktionen
    aktueller_saldo = KontoManager.berechne_kontostand_aus_transaktionen(
        db, konto_id, initialstand=konto.kontostand
    )

    return {
        "konto_id": konto_id,
        "initialstand": konto.kontostand,
        "aktueller_saldo": round(aktueller_saldo, 2),
    }


@app.get("/konten/stats/summary")
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


# ==================== ENDPUNKTE: IMPORT ====================


@app.post("/transactions/import")
async def import_transactions(
    file: UploadFile = File(...),
    header_row: int = Form(...),
    skip_footer: int = Form(...),
    mapping: str = Form(...),
    konto_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """
    Importiere CSV-Transaktionen.
    frontend sendet:
      - file: CSV-Datei
      - header_row: Zeile der Spaltenüberschriften (1-basiert)
      - skip_footer: Anzahl der Zeilen am Ende, die übersprungen werden
      - mapping: JSON { "buchungstag": "Buchungstag", "beguenstigter": "Begünstigter / Auftraggeber", ... }
      - konto_id: ID des Kontos, auf das gebucht wird
    """
    try:
        # Mapping JSON parsen
        mapping_dict = json.loads(mapping)

        # Temporäre Datei speichern (UploadFile ist ein SpooledFile)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # Import starten
        importer = CSVTransaktionImporter(
            session=db,
            mapping=mapping_dict,
            header_row=header_row,
            skip_footer=skip_footer,
            konto_id=konto_id,
        )
        importer.import_csv(tmp_path)

        auto_categorizer.run_full_categorization_cycle()

        return {"message": f"Import erfolgreich für Konto {konto_id}"}

    except Exception as e:
        # Fehler zurückgeben
        #raise HTTPException(status_code=400, detail=str(e))
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": str(e)}
        )


# ==================== ENDPUNKTE: AUTO-KATEGORISIERUNG ====================


@app.post("/categories/auto-categorize")
def trigger_auto_categorization(
    max_iterations: Optional[int] = None,
    min_occurrences: int = 3,
    db: Session = Depends(get_db),
):
    """
    Manueller Trigger für Auto-Kategorisierung.
    Nützlich für Tests und Debugging.

    Args:
        max_iterations: Maximale Anzahl von Iterationen (None = unbegrenzt)
        min_occurrences: Minimale Häufigkeit für neue Keywords beim Lernen
    """

    stats = auto_categorizer.run_full_categorization_cycle(
        max_iterations=max_iterations, min_occurrences=min_occurrences
    )

    return {"message": "Auto-Kategorisierung abgeschlossen", "statistics": stats}


@app.get("/categories/auto-categorize/status")
def get_auto_categorization_status(db: Session = Depends(get_db)):
    """
    Gibt den Status der Auto-Kategorisierung zurück.
    """

    state = auto_categorizer.get_categorization_state()

    return {
        "new_transactions_count": state["has_new_transactions"],
        "last_categorization": state["last_categorization"],
        "will_trigger_at": 5,  # Schwelle
        "needs_categorization": state["has_new_transactions"] >= 5,
    }
