#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Kategorisiert unkategorisierte Transaktionen automatisch
Nutzt die regelbasierte Kategorisierung anhand von Keywords
"""

import sys
from pathlib import Path

# Füge das Parent-Verzeichnis (Projekt-Root) zu sys.path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionLocal, Transaktion, init_db, Category
from src.categories.categorizer_rules import Categorizer


def print_summary(categorized_count: int, total_transactions: int):
    """Zeigt eine Zusammenfassung der Kategorisierung"""
    print("\n" + "="*60)
    print("✓ KATEGORISIERUNG ABGESCHLOSSEN")
    print("="*60)
    print(f"Insgesamt Transaktionen:    {total_transactions}")
    print(f"Kategorisiert:              {categorized_count}")
    print(f"Nicht kategorisiert:        {total_transactions - categorized_count}")
    print("="*60 + "\n")


def categorize_transactions(overwrite: bool = False):
    """Kategorisiert Transaktionen automatisch"""
    
    print("\n" + "="*60)
    print("📊 TRANSAKTIONEN KATEGORISIEREN")
    print("="*60)
    
    if overwrite:
        print("\nModus: Alle Transaktionen (auch bereits kategorisierte)\n")
    else:
        print("\nModus: Nur unkategorisierte Transaktionen\n")
    
    # Datenbank initialisieren
    init_db()
    session = SessionLocal()
    
    try:
        # Zähle Transaktionen
        total_transactions = session.query(Transaktion).count()
        uncategorized = session.query(Transaktion).filter_by(kategorie_id=None).count()
        
        print(f"Transaktionen insgesamt:    {total_transactions}")
        print(f"Unkategorisiert:            {uncategorized}\n")
        
        if total_transactions == 0:
            print("⚠️  Keine Transaktionen in der Datenbank vorhanden!\n")
            return
        
        # Kategorisiere Transaktionen
        print("⏳ Kategorisiere...")
        categorizer = Categorizer()
        categorization_results = categorizer.categorize_all(overwrite=overwrite)
        
        # Lese die Daten erneut aus der Datenbank (die Category-Objekte sind detached)
        # Verwende die Transaktion-IDs um die aktualisierten Daten zu laden
        transaction_ids = [trans.id for trans, _ in categorization_results if trans]
        
        if transaction_ids:
            # Lade die aktualisierten Transaktionen mit ihren Kategorien neu
            categorization_info = []
            for trans, _ in categorization_results:
                if trans and trans.id in transaction_ids:
                    # Die Kategorisierung wurde in categorize_transactions() durchgeführt
                    # Wir können die Info aus dem ursprünglichen Objekt extrahieren
                    if trans.kategorie_id:  # Wurde kategorisiert
                        # Bekomme den Kategorienamen aus der aktuellen Transaction
                        categorization_info.append({
                            "beguenstigter": trans.beguenstigter,
                            "category_id": trans.kategorie_id,
                            "betrag": trans.betrag
                        })
            
            # Lade die Kategorienamen aus der DB
            categorized_count = 0
            for info in categorization_info:
                cat = session.query(Category).get(info["category_id"])
                if cat:
                    info["category_name"] = cat.name
                    categorized_count += 1
                else:
                    info["category_name"] = "Unbekannt"
        else:
            categorization_info = []
            categorized_count = 0
        print_summary(categorized_count, total_transactions)
        
        if categorized_count > 0:
            print("Top kategorisierte Transaktionen:")
            # Zeige die ersten 20
            for i, info in enumerate(categorization_info[:20], 1):
                betrag_str = f"{info['betrag']:+.2f}€".replace("+", "✓ +").replace("-", "✓ -")
                print(f"  {i:2d}. {info['beguenstigter']:30s} → {info['category_name']:20s} {betrag_str}")
            
            if len(categorization_info) > 20:
                print(f"  ... und {len(categorization_info) - 20} weitere")
        else:
            print("ℹ️  Keine neuen Kategorisierungen durchgeführt")
        
    except Exception as e:
        print(f"\n✗ Fehler: {e}\n")
    finally:
        session.close()


def interactive_categorize():
    """Interaktive Kategorisierung mit Optionen"""
    
    print("\n" + "="*60)
    print("📊 TRANSAKTIONEN KATEGORISIEREN")
    print("="*60)
    print("\nWählen Sie einen Modus:\n")
    print("1. Nur unkategorisierte Transaktionen kategorisieren (Standard)")
    print("2. Alle Transaktionen erneut kategorisieren (Überschreiben)\n")
    
    while True:
        try:
            choice = input("Wählen Sie eine Option (1 oder 2): ").strip()
            if choice == "1":
                categorize_transactions(overwrite=False)
                break
            elif choice == "2":
                print("\n⚠️  Warnung: Dies wird bereits kategorisierte Transaktionen überschreiben!\n")
                confirm = input("Fortfahren? (ja/nein): ").strip().lower()
                if confirm in ["ja", "yes", "j", "y"]:
                    categorize_transactions(overwrite=True)
                else:
                    print("Abgebrochen.\n")
                break
            else:
                print("⚠️  Ungültige Eingabe. Bitte 1 oder 2 eingeben.\n")
        except Exception as e:
            print(f"Fehler: {e}\n")


if __name__ == "__main__":
    interactive_categorize()
