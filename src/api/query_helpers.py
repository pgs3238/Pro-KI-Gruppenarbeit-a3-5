# Hilfsfunktionen für Datenbankabfragen

from datetime import datetime
from typing import Optional


def parse_date(date_str: str) -> datetime.date:
    """
    Parst einen Datumsstring im Format YYYY-MM-DD zu einem date-Objekt.

    Args:
        date_str: Datumsstring im Format YYYY-MM-DD

    Returns:
        datetime.date Objekt
    """
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def apply_date_filters(query, model, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Wendet Datumsfilter auf eine SQLAlchemy-Query an.

    Args:
        query: SQLAlchemy Query-Objekt
        model: SQLAlchemy Model mit buchungstag-Attribut
        start_date: Startdatum im Format YYYY-MM-DD (optional)
        end_date: Enddatum im Format YYYY-MM-DD (optional)

    Returns:
        Gefilterte Query
    """
    if start_date:
        query = query.filter(model.buchungstag >= parse_date(start_date))
    if end_date:
        query = query.filter(model.buchungstag <= parse_date(end_date))
    return query
