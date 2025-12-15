from typing import Optional, List, Literal
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import Transaktion


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
) -> List[Transaktion]:

    # Transaktionen werden dynamisch durchsucht
    # Es werden nur die Filter angewendet, in denen eine Eingabe vorliegt.

    query = session.query(Transaktion)

    if buchungstag is not None:
        query = query.filter(Transaktion.buchungstag == buchungstag)

    if beguenstigter is not None:
        query = query.filter(Transaktion.beguenstigter.ilike(f"%{beguenstigter}%"))

    if verwendungszweck is not None:
        query = query.filter(Transaktion.verwendungszweck.ilike(f"%{verwendungszweck}%"))

    if iban_kontonummer is not None:
        query = query.filter(Transaktion.iban_kontonummer == iban_kontonummer)

    # Diese Überprüfung wird aus code sicht nicht benötigt, da die SQL abfrage keine Ergebnisse liefern würde wenn der Minimalbetrag größer als der Maximalbetrag ist. 
    # Diese Überprüfung dient lediglich dazu eine Fehlermeldung an das User Interface zu übergeben. 
    if betrag_min is not None and betrag_max is not None:
        if betrag_min > betrag_max:
            raise ValueError("betrag_min cannot be greater than betrag_max")
    
    # Alte Abfrage. Werte können zwischen - unendlich und + unendlich eingegeben werden. 
    # Problem: betrag_min bei Negativen zahlen heißt bspw. zwischen -50 und plus unendlich | betrag_max bei negativen Zahlen zwischen -50 und - unendlich
    if betrag_min is not None:
        query = query.filter(Transaktion.betrag >= betrag_min)

    if betrag_max is not None:
        query = query.filter(Transaktion.betrag <= betrag_max)

    # Filtern nach Einnahmen (income) und Ausgaben (expense)
    if typ == "expense":
        query = query.filter(Transaktion.betrag < 0)
    elif typ == "income":
        query = query.filter(Transaktion.betrag > 0)

    # Diese Überprüfung wird aus code sicht nicht benötigt, da die SQL abfrage keine Ergebnisse liefern würde wenn der Minimalbetrag größer als der Maximalbetrag ist. 
    # Diese Überprüfung dient lediglich dazu eine Fehlermeldung an das User Interface zu übergeben.
    if betrag_min_abs is not None and betrag_max_abs is not None:
        if betrag_min_abs > betrag_max_abs:
            raise ValueError("betrag_min_abs cannot be greater than betrag_max_abs")

    # Neue Abfrage. Um das Problem mit den negativen Zahlen zu beheben werden die Werte aus der SQL für die Abfrage in Absolute Werte umgewandelt.
    # Aus -50 wird +50. Infolge dessen kann auch im negativen Bereich zwischen 0 und -50 gefiltert werden. 
    # Wird diese Suche angewendet, muss die GUI negative Werte in positive umwandeln, da mit dieser Funktion nicht mehr nach -50 gesucht werden kann     
    if betrag_min_abs is not None:
        query = query.filter(func.abs(Transaktion.betrag) >= betrag_min_abs)

    if betrag_max_abs is not None:
        query = query.filter(func.abs(Transaktion.betrag) <= betrag_max_abs)

    if waehrung is not None:
        query = query.filter(Transaktion.waehrung == waehrung)



    return query.all()