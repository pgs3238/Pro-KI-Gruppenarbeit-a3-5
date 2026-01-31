"""
Author: Paul-Gerhard Siegel
Course: Programmieren für KI
Description:
    This module provides a search function for transactions stored in the database.
    It allows filtering transactions dynamically based on multiple optional criteria
    such as date, beneficiary, amount, transaction type, currency, and account.
"""
from typing import Optional, List, Literal
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import Transaktion, Konto, Category


def search_transaktionen(
    session: Session,
    buchungstag: Optional[date] = None,
    beguenstigter: Optional[str] = None,
    verwendungszweck: Optional[str] = None,
    iban_kontonummer: Optional[str] = None,
    betrag_min: Optional[float] = None,
    betrag_max: Optional[float] = None,
    typ: Optional[Literal["expense", "income"]] = None,
    betrag_min_abs: Optional[float] = None,
    betrag_max_abs: Optional[float] = None,
    waehrung: Optional[str] = None,
    konto_name: Optional[str] = None,
    beschreibung: Optional[str] = None,
    kategorie_name: Optional[str] = None,
) -> List[Transaktion]:
    """
    Searches transactions in the database based on multiple optional filters.

    Only filters that are provided (non-None) are applied. Filters include 
    booking date, beneficiary, purpose, IBAN/account number, amounts (absolute or normal),
    transaction type (income/expense), currency, and account name.

    Special features:
        - Handles European-style negative and positive amounts.
        - Provides absolute value filtering for amounts (betrag_min_abs / betrag_max_abs).
        - Raises ValueError if min > max for amount filters, to help the UI show errors.

    Args:
        session: SQLAlchemy session for database queries.
        buchungstag:        Filter by booking date.
        beguenstigter:      Filter by beneficiary name (case-insensitive, partial match).
        verwendungszweck:   Filter by purpose/description (case-insensitive, partial match).
        iban_kontonummer:   Filter by IBAN or account number (spaces ignored, partial match).
        betrag_min:         Minimum transaction amount (normal values).
        betrag_max:         Maximum transaction amount (normal values).
        typ:                "expense" to filter negative amounts, "income" for positive amounts.
        betrag_min_abs:     Minimum absolute transaction amount (ignores sign).
        betrag_max_abs:     Maximum absolute transaction amount (ignores sign).
        waehrung:           Filter by currency (e.g., "EUR").
        konto_name:         Filter by account name (case-insensitive, partial match).

    Returns:
        List of Transaktion objects matching the provided filters, ordered by
        booking date descending.
    """

    # Verwende outerjoin statt join, um auch Transaktionen ohne Konto/Kategorie zu finden
    query = session.query(Transaktion).outerjoin(Konto, Transaktion.konto_id == Konto.id).outerjoin(Category, Transaktion.kategorie_id == Category.id)

    # Filter by Buchungstag
    if buchungstag is not None:
        query = query.filter(Transaktion.buchungstag == buchungstag)
    
    # Filter by Beguenstigter
    if beguenstigter is not None:
        query = query.filter(Transaktion.beguenstigter.ilike(f"%{beguenstigter}%"))

    # Filter by Verwendungszweck
    if verwendungszweck is not None:
        query = query.filter(Transaktion.verwendungszweck.ilike(f"%{verwendungszweck}%"))

    # Filter by IBAN
    if iban_kontonummer is not None:
        iban_clean = iban_kontonummer.replace(' ', '')
        query = query.filter(func.replace(Transaktion.iban_kontonummer, ' ', '').like(f"%{iban_clean}%"))
 
    # Note: The following filters (typ, betrag_min, betrag_max) are not used
    # in our current scope but are kept to avoid breaking other parts of the project.
    if betrag_min is not None and betrag_max is not None:
        if betrag_min > betrag_max:
            raise ValueError("betrag_min cannot be greater than betrag_max")
    
    if betrag_min is not None:
        query = query.filter(Transaktion.betrag >= betrag_min)

    if betrag_max is not None:
        query = query.filter(Transaktion.betrag <= betrag_max)

    
    if typ == "expense":
        query = query.filter(Transaktion.betrag < 0)
    elif typ == "income":
        query = query.filter(Transaktion.betrag > 0)

    # Check if Minimalbetrag absolut is not greater than Maximalbetrag absolut
    if betrag_min_abs is not None and betrag_max_abs is not None:
        if betrag_min_abs > betrag_max_abs:
            raise ValueError("betrag_min_abs cannot be greater than betrag_max_abs")

    # Minimalbetrag in absoluten Zahlen    
    if betrag_min_abs is not None:
        query = query.filter(func.abs(Transaktion.betrag) >= betrag_min_abs)

    # Maximalbetrag in absoluten Zahlen
    if betrag_max_abs is not None:
        query = query.filter(func.abs(Transaktion.betrag) <= betrag_max_abs)

    if waehrung is not None:
        query = query.filter(Transaktion.waehrung == waehrung)

    # Filter by Beschreibung (Freitextfeld)
    if beschreibung is not None:
        query = query.filter(Transaktion.beschreibung.ilike(f"%{beschreibung}%"))

    # Filter by Kategorie-Name (über die Category-Tabelle)
    if kategorie_name is not None:
        query = query.filter(Category.name.ilike(f"%{kategorie_name}%"))

    # Filter by Konto
    if konto_name is not None:
        query = query.filter(Konto.kontoname.ilike(f"%{konto_name}%"))

    # Order query by descending dates
    query = query.order_by(Transaktion.buchungstag.desc())

    return query.all()