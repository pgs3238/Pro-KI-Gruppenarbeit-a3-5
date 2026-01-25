#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fügt Transaktionen ohne Kategorien hinzu
Erstellt realistische Test-Transaktionen ohne kategorie_id
"""

import random
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Füge das Parent-Verzeichnis (Projekt-Root) zu sys.path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionLocal, Transaktion, init_db


# ==================== DATEN POOLS ====================

EXPENSE_RECIPIENTS = [
    "Supermarkt REWE", "Supermarkt EDEKA", "Supermarkt Aldi", "Supermarkt Lidl",
    "Amazon", "eBay", "Netflix", "Spotify", "Apple Music",
    "Stadtwerke München", "Vodafone", "Telekom", "O2",
    "Fitnessstudio FitX", "Fitnessstudio McFit",
    "Restaurant Ristorante", "Restaurant Pizzeria", "Restaurant Asia",
    "ÖPNV München", "Deutsche Bahn",
    "Zahnarzt Dr. Schmidt", "Apotheke am Markt",
    "H&M", "Zara", "Nike", "Adidas",
    "Miete Wohnung", "Nebenkosten", "Versicherung",
]

INCOME_RECIPIENTS = [
    "Arbeitgeber GmbH", "Gehalt", "Bonus",
    "Freiberufliche Arbeit",
    "Steuererstattung", "Kapitalerträge",
]

EXPENSE_PURPOSES = [
    "Lebensmittel", "Haushalt", "Shopping", "Unterhaltung",
    "Miete", "Nebenkosten", "Strom", "Gas", "Wasser",
    "Internet", "Telefon", "Versicherung",
    "Restaurant", "Kino", "Theater",
    "Fitness", "Friseur", "Apotheke",
    "Auto", "Tanken", "Parkgebühr",
    "Bahnticket", "Flugticket", "Uber",
    "Zahlungsmittel", "Kontogebühren",
]

# Beispiel IBANs
IBANS = [
    "DE89370400440532013000",
    "DE91100000000123456789",
    "DE75512108001234567890",
    "DE68800400040532013000",
    "AT611904300234573201",
]

# ==================== FUNKTIONEN ====================

def generate_amount(transaction_type: str = "expense") -> float:
    """Generiert einen realistischen Betrag"""
    if transaction_type == "expense":
        # Ausgaben: -0.50 bis -500
        amount = -round(random.uniform(0.50, 50), 2)
    else:  # income
        # Einnahmen: +500 bis +5000
        amount = round(random.uniform(500, 5000), 2)
    
    return amount


def generate_iban() -> str:
    """Generiert eine zufällige IBAN"""
    return random.choice(IBANS)


def generate_date(days_back_max: int = 30):
    """Generiert ein zufälliges Datum"""
    days_back = random.randint(0, days_back_max)
    date = datetime.now() - timedelta(days=days_back)
    return date.date()


def generate_transaction(transaction_type: str = "random", days_back_max: int = 30):
    """Generiert eine zufällige Transaktion OHNE Kategorie"""
    
    # Bestimme Typ
    if transaction_type == "random":
        transaction_type = random.choice(["expense", "income"])
    
    # Generiere Felder basierend auf Typ
    if transaction_type == "expense":
        recipient = random.choice(EXPENSE_RECIPIENTS)
        purpose = random.choice(EXPENSE_PURPOSES)
    else:
        recipient = random.choice(INCOME_RECIPIENTS)
        purpose = random.choice(EXPENSE_PURPOSES)
    
    amount = generate_amount(transaction_type)
    
    return {
        "buchungstag": generate_date(days_back_max),
        "beguenstigter": recipient,
        "verwendungszweck": purpose,
        "iban_kontonummer": generate_iban(),
        "betrag": amount,
        "waehrung": "EUR",
        "beschreibung": None,  # KEINE KATEGORIE!
        "konto_id": 1,
    }


def print_summary(count: int, expenses: int, income: int, total_expense: float, total_income: float):
    """Zeigt eine Zusammenfassung der erstellten Einträge"""
    print("\n" + "="*60)
    print("✓ ZUSAMMENFASSUNG")
    print("="*60)
    print(f"Insgesamt erstellt:    {count} Transaktionen")
    print(f"  └─ Ausgaben:         {expenses} ({total_expense:.2f}€)")
    print(f"  └─ Einnahmen:        {income} ({total_income:.2f}€)")
    print(f"Netto-Saldo:           {total_income + total_expense:.2f}€")
    print("="*60 + "\n")


def interactive_generate():
    """Hauptfunktion für die interaktive Test-Daten-Generierung"""
    
    print("\n" + "="*60)
    print("📊 TRANSAKTIONEN OHNE KATEGORIEN")
    print("="*60)
    print("\nFügt Transaktionen hinzu, ohne Kategorien zu setzen\n")
    
    # Anzahl erfragen
    while True:
        try:
            count_str = input("🔢 Wie viele Transaktionen sollen erstellt werden? ")
            count = int(count_str)
            if count < 1:
                print("⚠️  Bitte eine Zahl größer als 0 eingeben\n")
                continue
            break
        except ValueError:
            print("⚠️  Ungültige Eingabe\n")
            continue
    
    # Anzahl der Tage erfragen
    while True:
        try:
            days_str = input("📅 Über wie viele Tage sollen die Transaktionen verteilt werden? (Default: 30) ")
            days = int(days_str) if days_str else 30
            if days < 1:
                print("⚠️  Bitte eine Zahl größer als 0 eingeben\n")
                continue
            break
        except ValueError:
            print("⚠️  Ungültige Eingabe\n")
            continue
    
    # Datenbank initialisieren
    print("\n⏳ Generiere Transaktionen...")
    init_db()
    session = SessionLocal()
    
    try:
        transactions = []
        total_expense = 0
        total_income = 0
        expense_count = 0
        income_count = 0
        
        # Generiere Transaktionen
        for i in range(count):
            trans_data = generate_transaction(days_back_max=days)
            
            transaction = Transaktion(
                buchungstag=trans_data["buchungstag"],
                beguenstigter=trans_data["beguenstigter"],
                verwendungszweck=trans_data["verwendungszweck"],
                iban_kontonummer=trans_data["iban_kontonummer"],
                betrag=trans_data["betrag"],
                waehrung=trans_data["waehrung"],
                beschreibung=trans_data["beschreibung"],
                konto_id=trans_data["konto_id"]
                # kategorie_id bleibt None!
            )
            
            session.add(transaction)
            transactions.append(trans_data)
            
            # Statistik
            if trans_data["betrag"] < 0:
                total_expense += abs(trans_data["betrag"])
                expense_count += 1
            else:
                total_income += trans_data["betrag"]
                income_count += 1
        
        # Speichern
        session.commit()
        print_summary(count, expense_count, income_count, total_expense, total_income)
        
    except Exception as e:
        session.rollback()
        print(f"\n✗ Fehler: {e}\n")
    finally:
        session.close()


if __name__ == "__main__":
    interactive_generate()
