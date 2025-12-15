from database import SessionLocal
from database.search import search_transaktionen
from datetime import date

session = SessionLocal()

# Abfrage mit einem Feld
results = search_transaktionen(
    session,
    buchungstag=date(2024, 12, 10)
)

# Abfrage mit mehreren Feldern
results = search_transaktionen(
    session,
    beguenstigter="REWE Supermarkt",
    betrag_max_abs=100.0
)

# Abfrage mit mehreren Feldern
results = search_transaktionen(
    session,
    buchungstag=date(2024, 12, 11),
    beguenstigter="Max Mustermann AG",
    waehrung="EUR"
)

session.close()