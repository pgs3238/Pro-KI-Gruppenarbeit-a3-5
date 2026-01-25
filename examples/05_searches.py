"""
Author: Paul-Gerhard Siegel
Course: Programmieren für KI
Description:
    Example script demonstrating how to use the transaction search function.
    The script performs several example queries with different filter combinations
    and prints the results to the console.
"""
from src.database import SessionLocal
from src.database.search import search_transaktionen
from datetime import date

session = SessionLocal()

# Abfrage mit einem Feld
results = search_transaktionen(
    session,
    buchungstag=date(2025, 8, 14)
)
print("---------")
print("Abfrage: bestimmtes Datum")
for r in results:
    print(r)
print("---------")

# Abfrage mit mehreren Feldern
results = search_transaktionen(
    session,
    beguenstigter="REWE",
    betrag_max_abs=100.0
)
print("Abfrage: REWE + max betrag 100€")
for r in results:
    print(r)
print("---------")

# Abfrage mit mehreren Feldern
results = search_transaktionen(
    session,
    beguenstigter="REWE",
    betrag_max_abs=100.0,
    betrag_min_abs=20.0
)
print("Abfrage: REWE + max 100€ min 20€")
for r in results:
    print(r)
print("---------")


# Abfrage mit mehreren Feldern
results = search_transaktionen(
    session,
    buchungstag=date(2024, 12, 11),
    beguenstigter="Max Mustermann AG",
    waehrung="EUR"
)
print("Abfrage: Genaue abfrage mit mehreren Daten")
for r in results:
    print(r)
print("---------")

session.close()