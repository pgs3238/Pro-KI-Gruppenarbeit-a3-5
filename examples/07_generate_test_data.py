#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generiert realistische Test-Daten für die Datenbank
Erstellt zufällige Transaktionen mit passenden Werten
"""

import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

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

CATEGORIES = [
    "Lebensmittel", "Shopping", "Wohnen & Energie", "Verkehr",
    "Unterhaltung", "Gesundheit", "Bildung", "Sonstiges"
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
        amount = round(random.uniform(50, 500), 2)
    
    return amount


def generate_iban() -> str:
    """Generiert eine zufällige IBAN"""
    return random.choice(IBANS)


def generate_date() -> datetime:
    """Generiert ein zufälliges Datum aus den letzten 2 Jahren"""
    days_back = random.randint(0, 730)
    date = datetime.now() - timedelta(days=days_back)
    return date.date()


def generate_transaction(transaction_type: str = "random"):
    """Generiert eine zufällige Transaktion"""
    
    # Bestimme Typ
    if transaction_type == "random":
        transaction_type = random.choice(["expense", "income"])
    
    # Generiere Felder basierend auf Typ
    if transaction_type == "expense":
        recipient = random.choice(EXPENSE_RECIPIENTS)
        purpose = random.choice(EXPENSE_PURPOSES)
        category = random.choice(CATEGORIES)
    else:
        recipient = random.choice(INCOME_RECIPIENTS)
        purpose = random.choice(EXPENSE_PURPOSES)
        category = "Gehalt"
    
    amount = generate_amount(transaction_type)
    
    return {
        "buchungstag": generate_date(),
        "beguenstigter": recipient,
        "verwendungszweck": purpose,
        "iban_kontonummer": generate_iban(),
        "betrag": amount,
        "waehrung": "EUR",
        "beschreibung": category,
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
    print("📊 TEST-DATEN GENERATOR")
    print("="*60)
    print("\nGeneriert realistische Test-Daten für die Datenbank\n")
    
    # Anzahl erfragen
    while True:
        try:
            count_str = input("🔢 Wie viele Transaktionen sollen erstellt werden? ")
            count = int(count_str)
            if count < 1:
                print("⚠️  Bitte eine Zahl größer als 0 eingeben\n")
                continue
            if count > 10000:
                confirm = input(f"⚠️  Das sind viele Einträge ({count}). Fortfahren? (j/n): ")
                if confirm.lower() != 'j':
                    continue
            break
        except ValueError:
            print("⚠️  Ungültige Eingabe. Bitte geben Sie eine Zahl ein\n")
    
    # Verteilung erfragen
    print("\n📋 Verteilung der Transaktionstypen:")
    while True:
        try:
            expense_pct_str = input("   Anteil Ausgaben in Prozent (0-100, standard 60): ")
            expense_pct = int(expense_pct_str) if expense_pct_str else 60
            if not 0 <= expense_pct <= 100:
                print("⚠️  Bitte Wert zwischen 0-100 eingeben\n")
                continue
            break
        except ValueError:
            print("⚠️  Ungültige Eingabe\n")
    
    income_pct = 100 - expense_pct
    
    # Datenbank initialisieren
    init_db()
    session: Session = SessionLocal()
    
    try:
        print(f"\n⏳ Generiere {count} Transaktionen...\n")
        
        transactions_to_create = []
        expenses = 0
        income = 0
        total_expense = 0.0
        total_income = 0.0
        
        # Generiere Transaktionen
        for i in range(count):
            # Bestimme Typ basierend auf Prozentverteilung
            if random.random() * 100 < expense_pct:
                trans_type = "expense"
                expenses += 1
            else:
                trans_type = "income"
                income += 1
            
            # Generiere Transaktion
            trans_data = generate_transaction(trans_type)
            transactions_to_create.append(Transaktion(**trans_data))
            
            # Aktualisiere Statistiken
            if trans_data["betrag"] < 0:
                total_expense += trans_data["betrag"]
            else:
                total_income += trans_data["betrag"]
            
            # Fortschrittsanzeige
            if (i + 1) % 100 == 0:
                print(f"  ✓ {i + 1}/{count} erstellt...")
        
        # Speichere alle Transaktionen
        session.add_all(transactions_to_create)
        session.commit()
        
        print(f"\n✓ Alle {count} Transaktionen erfolgreich erstellt!")
        
        # Zeige Zusammenfassung
        print_summary(count, expenses, income, total_expense, total_income)
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Fehler beim Erstellen der Transaktionen: {e}\n")
    finally:
        session.close()


def main():
    """Hauptprogramm"""
    while True:
        interactive_generate()
        
        wieder = input("🔄 Weitere Daten generieren? (j/n): ").strip().lower()
        if wieder != 'j':
            print("\n👋 Auf Wiedersehen!\n")
            break


if __name__ == "__main__":
    main()
