# Beispiel: transaktionen lesen und filtern
from src.database import SessionLocal, Transaction

def main():
    session = SessionLocal()
    
    try:
        all_transactions = session.query(Transaction).all()
        
        for trans in all_transactions:
            print(f"\nID: {trans.id}")
            print(f"  Datum: {trans.buchungstag}")
            print(f"  Begünstigter: {trans.beguenstigter}")
            print(f"  Betrag: {trans.betrag} {trans.waehrung}")
            print(f"  Verwendungszweck: {trans.verwendungszweck}")
        
        print(f"Gesamt: {len(all_transactions)} Transaktionen")
        
        # Nur Ausgaben (negative Beträge)
        ausgaben = session.query(Transaction).filter(Transaction.betrag < 0).all()
        for trans in ausgaben:
            print(f"  {trans.buchungstag} | {trans.beguenstigter} | {trans.betrag} EUR")
        
        # Nur Einnahmen (positive Beträge)
        print("\n=== Nur Einnahmen ===")
        einnahmen = session.query(Transaction).filter(Transaction.betrag > 0).all()
        for trans in einnahmen:
            print(f"  {trans.buchungstag} | {trans.beguenstigter} | {trans.betrag} EUR")
        
        # Summen berechnen
        summe_ausgaben = sum(t.betrag for t in ausgaben) # Generator Expression, nichts anders als: "for t in asugaben: summe_ausgaben += t.betrag"
        summe_einnahmen = sum(t.betrag for t in einnahmen)
        saldo = summe_einnahmen + summe_ausgaben
        
        print(f"  Ausgaben: {summe_ausgaben:.2f} EUR")
        print(f"  Einnahmen: {summe_einnahmen:.2f} EUR")
        print(f"  Saldo: {saldo:.2f} EUR")
        
    finally:
        session.close()


if __name__ == "__main__":
    main()
