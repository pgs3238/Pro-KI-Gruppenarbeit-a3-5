"""
Database Tools für den Chatbot
Standalone-Funktionen für automatisches Function Calling mit Gemini
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime
from typing import List, Dict, Optional, Any
from ..database.models import Transaktion, Konto, Category


# Globale Session (wird von get_db_session() verwaltet)
_session: Optional[Session] = None


def set_db_session(session: Session):
    """Setzt die aktuelle Datenbank-Session für alle Tool-Funktionen"""
    global _session
    _session = session


def get_db_session() -> Session:
    """Gibt die aktuelle Datenbank-Session zurück"""
    if _session is None:
        raise RuntimeError(
            "Keine Datenbank-Session gesetzt. Rufe set_db_session() auf."
        )
    return _session


def get_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Ruft Transaktionen mit optionalen Filtern ab.

    Args:
        start_date: Startdatum im Format YYYY-MM-DD (optional)
        end_date: Enddatum im Format YYYY-MM-DD (optional)
        category: Kategoriename zum Filtern (optional)
        transaction_type: "Einnahme" oder "Ausgabe" (optional)
        limit: Maximale Anzahl Ergebnisse (default: 100)

    Returns:
        Liste von Transaktions-Dictionaries
    """
    session = get_db_session()
    query = session.query(Transaktion)

    # Filter: Datumsbereich
    if start_date:
        query = query.filter(
            Transaktion.buchungstag >= datetime.strptime(start_date, "%Y-%m-%d").date()
        )
    if end_date:
        query = query.filter(
            Transaktion.buchungstag <= datetime.strptime(end_date, "%Y-%m-%d").date()
        )

    # Filter: Kategorie
    if category:
        query = query.join(Category).filter(Category.name == category)

    # Filter: Transaktionstyp
    if transaction_type:
        if transaction_type.lower() == "einnahme":
            query = query.filter(Transaktion.betrag > 0)
        elif transaction_type.lower() == "ausgabe":
            query = query.filter(Transaktion.betrag < 0)

    # Limit anwenden und sortieren
    transactions = query.order_by(Transaktion.buchungstag.desc()).limit(limit).all()

    return [
        {
            "id": t.id,
            "buchungstag": t.buchungstag.isoformat() if t.buchungstag else None,
            "beguenstigter": t.beguenstigter,
            "verwendungszweck": t.verwendungszweck,
            "betrag": float(t.betrag),
            "waehrung": t.waehrung,
            "kategorie": t.kategorie.name if t.kategorie else "Unbekannt",
            "konto_id": t.konto_id,
        }
        for t in transactions
    ]


def get_spending_by_category(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Gibt aggregierte Ausgaben nach Kategorie zurück.

    Args:
        start_date: Startdatum im Format YYYY-MM-DD (optional)
        end_date: Enddatum im Format YYYY-MM-DD (optional)

    Returns:
        Liste mit Kategorien und Gesamtausgaben
    """
    session = get_db_session()
    query = session.query(
        Category.name, func.sum(Transaktion.betrag).label("total")
    ).join(Transaktion)

    # Nur Ausgaben
    query = query.filter(Transaktion.betrag < 0)

    # Filter: Datumsbereich
    if start_date:
        query = query.filter(
            Transaktion.buchungstag >= datetime.strptime(start_date, "%Y-%m-%d").date()
        )
    if end_date:
        query = query.filter(
            Transaktion.buchungstag <= datetime.strptime(end_date, "%Y-%m-%d").date()
        )

    results = query.group_by(Category.name).order_by(func.sum(Transaktion.betrag)).all()

    return [
        {"kategorie": r.name, "total_ausgaben": abs(float(r.total)), "waehrung": "EUR"}
        for r in results
    ]


def get_monthly_summary(year: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Gibt monatliche Zusammenfassung von Einnahmen und Ausgaben zurück.

    Args:
        year: Jahr (z.B. 2024), falls None wird aktuelles Jahr verwendet

    Returns:
        Liste mit monatlichen Zusammenfassungen
    """
    session = get_db_session()
    if year is None:
        year = datetime.now().year

    query = (
        session.query(
            extract("month", Transaktion.buchungstag).label("monat"),
            func.sum(func.abs(Transaktion.betrag))
            .filter(Transaktion.betrag < 0)
            .label("ausgaben"),
            func.sum(Transaktion.betrag)
            .filter(Transaktion.betrag > 0)
            .label("einnahmen"),
        )
        .filter(extract("year", Transaktion.buchungstag) == year)
        .group_by("monat")
        .order_by("monat")
    )

    results = query.all()
    monatsnamen = [
        "Januar",
        "Februar",
        "März",
        "April",
        "Mai",
        "Juni",
        "Juli",
        "August",
        "September",
        "Oktober",
        "November",
        "Dezember",
    ]

    return [
        {
            "monat": monatsnamen[int(r.monat) - 1] if r.monat else "Unbekannt",
            "monat_nummer": int(r.monat) if r.monat else 0,
            "ausgaben": float(r.ausgaben) if r.ausgaben else 0.0,
            "einnahmen": float(r.einnahmen) if r.einnahmen else 0.0,
            "bilanz": float(r.einnahmen or 0.0) - float(r.ausgaben or 0.0),
            "jahr": year,
        }
        for r in results
    ]


def get_account_overview() -> List[Dict[str, Any]]:
    """
    Gibt eine Übersicht aller Konten mit Kontoständen zurück.

    Returns:
        Liste aller Konten mit Details
    """
    session = get_db_session()
    konten = session.query(Konto).all()

    return [
        {
            "id": k.id,
            "kontoname": k.kontoname,
            "kontonummer": k.kontonummer,
            "bankname": k.bankname,
            "kontostand": float(k.kontostand),
            "waehrung": k.waehrung,
            "kontotyp": k.kontotyp,
            "erstellt_am": k.erstellt_am.isoformat() if k.erstellt_am else None,
        }
        for k in konten
    ]


def get_income_vs_expenses(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Vergleicht Einnahmen und Ausgaben für einen Zeitraum.

    Args:
        start_date: Startdatum im Format YYYY-MM-DD (optional)
        end_date: Enddatum im Format YYYY-MM-DD (optional)

    Returns:
        Dictionary mit Einnahmen, Ausgaben und Bilanz
    """
    session = get_db_session()
    query = session.query(Transaktion)

    # Filter: Datumsbereich
    if start_date:
        query = query.filter(
            Transaktion.buchungstag >= datetime.strptime(start_date, "%Y-%m-%d").date()
        )
    if end_date:
        query = query.filter(
            Transaktion.buchungstag <= datetime.strptime(end_date, "%Y-%m-%d").date()
        )

    transactions = query.all()
    total_income = sum(t.betrag for t in transactions if t.betrag > 0)
    total_expenses = sum(abs(t.betrag) for t in transactions if t.betrag < 0)

    return {
        "einnahmen": float(total_income),
        "ausgaben": float(total_expenses),
        "bilanz": float(total_income - total_expenses),
        "waehrung": "EUR",
        "zeitraum": {"von": start_date, "bis": end_date},
    }


def get_categories() -> List[Dict[str, str]]:
    """
    Gibt alle verfügbaren Kategorien zurück.

    Returns:
        Liste aller Kategorien mit Name und Typ
    """
    session = get_db_session()
    categories = session.query(Category).all()

    return [{"name": c.name, "typ": c.category_type} for c in categories]
