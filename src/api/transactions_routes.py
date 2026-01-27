from datetime import date, datetime, timedelta
from typing import List, Optional
import tempfile
import json
import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from ..database import Transaktion, Konto
from ..database.search import search_transaktionen
from ..database.konto_manager import KontoManager
from ..database.csv_importer import CSVTransaktionImporter
from ..categories.auto_categorizer_service import get_auto_categorizer_service
from ..constants import CHART_COLOR_PALETTE, EXPENSE_COLOR
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
from .helpers import get_or_404

router = APIRouter(tags=["Transactions"])

# Globale Service-Instanz (Singleton kommt aus get_auto_categorizer_service)
auto_categorizer = get_auto_categorizer_service()


# ==================== HILFSFUNKTIONEN ====================


def get_transaction_or_404(transaction_id: int, db: Session):
    """Transaktion laden oder 404 werfen"""
    return get_or_404(db, Transaktion, transaction_id, detail="Transaktion nicht gefunden")


def get_konto_or_404(konto_id: int, db: Session):
    """Konto laden oder 404 werfen"""
    return get_or_404(db, Konto, konto_id, detail="Konto nicht gefunden")


# ==================== ENDPUNKTE: BASIC ====================


@router.get(
    "/transactions",
)
def get_transactions(
    skip: int = 0,
    limit: int = 1000,
    days: int = 30,
    db: Session = Depends(get_db),
):
    """Alle Transaktionen (mit optional Datumsfilter für letzte N Tage)"""

    # Wenn days > 0, filtere nach den letzten N Tagen
    if days > 0:
        cutoff_date = datetime.now().date() - timedelta(days=days)
        return (
            db.query(Transaktion)
            .filter(Transaktion.buchungstag >= cutoff_date)
            .offset(skip)
            .limit(limit)
            .all()
        )

    return db.query(Transaktion).offset(skip).limit(limit).all()


@router.get("/transactions/formatted/list")
def get_transactions_formatted(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Alle Transaktionen mit formatierten Werten für Frontend"""
    transactions = (
        db.query(Transaktion)
        .order_by(Transaktion.buchungstag.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    konten = db.query(Konto).all()
    konto_map = {k.id: k.kontoname for k in konten}

    formatted = []
    for t in transactions:
        # Formatiere Datum als dd.mm.yyyy
        datum = t.buchungstag.strftime("%d.%m.%Y")

        # Formatiere Betrag mit + und €
        betrag_class = "positiv" if t.betrag >= 0 else "negativ"
        betrag_text = ("+" if t.betrag >= 0 else "") + f"{t.betrag:.2f}".replace(
            ".", ","
        ) + "€"

        # IBAN formatieren (mit Leerzeichen alle 4 Zeichen)
        iban = t.iban_kontonummer or "-"
        if len(iban) > 4:
            iban = " ".join([iban[i : i + 4] for i in range(0, len(iban), 4)])

        # Kategorie: Nutze kategorie_id und lade den Namen via Relationship
        kategorie = "-"
        if t.kategorie_id and t.kategorie:
            kategorie = t.kategorie.name

        # Kontoname auflösen
        kontoname = konto_map.get(t.konto_id, "-") if t.konto_id else "-"

        formatted.append(
            {
                "id": t.id,
                "datum": datum,
                "beguenstigter": t.beguenstigter,
                "iban": iban,
                "konto": kontoname,
                "verwendungszweck": t.verwendungszweck or "-",
                "kategorie": kategorie,
                "betrag": betrag_text,
                "betrag_class": betrag_class,
            }
        )

    return formatted


# ==================== ENDPUNKTE: SANKEY DIAGRAMM ====================
# WICHTIG: Muss vor /transactions/{transaction_id} stehen, sonst wird "sankey-data" als ID interpretiert


@router.get("/transactions/sankey-data")
def get_sankey_data(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Liefert Daten für ein Sankey-Diagramm: Ausgaben → Kategorien

    Struktur für Plotly:
    - nodes: Liste mit Label und Farbe für jeden Node
    - links: source, target, value, color für jeden Flow

    Args:
        year: Jahr für die Filterung (Standard: aktuelles Jahr)
        month: Monat für die Filterung 1-12 (Standard: aktueller Monat)
    """
    from calendar import monthrange
    from ..database.models import Category

    # Standardwerte: aktueller Monat
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    # Berechne Start- und Enddatum des Monats
    first_day = datetime(year, month, 1).date()
    last_day_num = monthrange(year, month)[1]
    last_day = datetime(year, month, last_day_num).date()

    # Lade Transaktionen des Monats (nur Ausgaben)
    transactions = (
        db.query(Transaktion)
        .filter(
            Transaktion.buchungstag >= first_day,
            Transaktion.buchungstag <= last_day,
            Transaktion.betrag < 0,  # Nur Ausgaben
        )
        .all()
    )

    if not transactions:
        return {
            "nodes": [],
            "links": [],
            "total_expenses": 0,
            "category_count": 0,
        }

    # Lade alle Kategorien für Lookup
    categories = {c.id: c for c in db.query(Category).all()}

    # Sammle Ausgaben pro Kategorie
    category_expenses = {}  # {kategorie_name: betrag}

    for t in transactions:
        # Kategorie-Name ermitteln
        category_name = "Sonstiges"
        if t.kategorie_id and t.kategorie_id in categories:
            category_name = categories[t.kategorie_id].name

        if category_name not in category_expenses:
            category_expenses[category_name] = 0

        category_expenses[category_name] += abs(t.betrag)

    # Sortiere nach Betrag (größte zuerst)
    sorted_categories = sorted(
        category_expenses.items(), key=lambda x: x[1], reverse=True
    )

    # Berechne Gesamtausgaben
    total_expenses = sum(amount for _, amount in sorted_categories)

    # Erstelle Nodes
    # Node 0: Ausgaben (links)
    nodes = [{"label": "💸 Ausgaben", "color": EXPENSE_COLOR}]

    # Nodes 1 bis N: Kategorien (rechts)
    for idx, (name, amount) in enumerate(sorted_categories):
        color = CHART_COLOR_PALETTE[idx % len(CHART_COLOR_PALETTE)]
        nodes.append(
            {
                "label": name,
                "color": color,
                "value": round(amount, 2),
            }
        )

    # Erstelle Links: Ausgaben → Kategorien
    links = []
    for idx, (name, amount) in enumerate(sorted_categories):
        color = CHART_COLOR_PALETTE[idx % len(CHART_COLOR_PALETTE)]
        # Füge Transparenz hinzu (66 = 40% opacity in hex)
        link_color = color + "66"

        links.append(
            {
                "source": 0,  # Von "Ausgaben"
                "target": idx + 1,  # Zur Kategorie
                "value": round(amount, 2),
                "color": link_color,
            }
        )

    return {
        "nodes": nodes,
        "links": links,
        "total_expenses": round(total_expenses, 2),
        "category_count": len(sorted_categories),
        "year": year,
        "month": month,
    }


@router.get(
    "/transactions/{transaction_id}",
    response_model=TransaktionResponse,
)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Eine Transaktion abrufen"""
    return get_transaction_or_404(transaction_id, db)


@router.post(
    "/transactions",
    response_model=TransaktionResponse,
    status_code=201,
)
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


@router.put(
    "/transactions/{transaction_id}",
    response_model=TransaktionResponse,
)
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


@router.delete(
    "/transactions/{transaction_id}",
    status_code=204,
)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Transaktion löschen"""
    db_transaction = get_transaction_or_404(transaction_id, db)
    db.delete(db_transaction)
    db.commit()


# ==================== ENDPUNKTE: FILTER & STATISTIKEN ====================


@router.get(
    "/transactions/filter/date-range",
    response_model=List[TransaktionResponse],
)
def get_transactions_by_date_range(
    start_date: date, end_date: date, db: Session = Depends(get_db)
):
    """Transaktionen nach Datumsbereich filtern"""
    return (
        db.query(Transaktion)
        .filter(
            Transaktion.buchungstag >= start_date,
            Transaktion.buchungstag <= end_date,
        )
        .all()
    )


@router.get("/transactions/stats/summary")
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


@router.post(
    "/transactions/search",
    response_model=List[TransaktionResponse],
)
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
        kategorie_name=search_params.kategorie_name,
    )


# ==================== ENDPUNKTE: KONTEN ====================


@router.get(
    "/konten",
    response_model=List[KontoResponse],
)
def get_konten(db: Session = Depends(get_db)):
    """Alle Konten abrufen (mit Initialstand)"""
    konten = db.query(Konto).all()
    return konten


@router.get(
    "/konten/{konto_id}",
    response_model=KontoResponse,
)
def get_konto(konto_id: int, db: Session = Depends(get_db)):
    """Ein einzelnes Konto abrufen (mit Initialstand)"""
    konto = get_konto_or_404(konto_id, db)
    return konto


@router.post(
    "/konten",
    response_model=KontoResponse,
    status_code=201,
)
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


@router.put(
    "/konten/{konto_id}",
    response_model=KontoResponse,
)
def update_konto(
    konto_id: int,
    konto_update: KontoUpdate,
    db: Session = Depends(get_db),
):
    """Konto aktualisieren"""
    db_konto = get_konto_or_404(konto_id, db)

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


@router.delete(
    "/konten/{konto_id}",
    status_code=204,
)
def delete_konto(konto_id: int, db: Session = Depends(get_db)):
    """Konto löschen (mit allen zugehörigen Transaktionen)"""
    success = KontoManager.lösche_konto(db, konto_id)

    if not success:
        raise HTTPException(status_code=404, detail="Konto nicht gefunden")


@router.get("/konten/{konto_id}/saldo")
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


@router.get("/konten/stats/summary")
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


@router.post("/transactions/import")
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
    tmp_path = None
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
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Temporäre Datei immer bereinigen
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


