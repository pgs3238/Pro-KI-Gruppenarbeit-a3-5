# Beispiel: Eine bestehende Transaktion aktualisieren
from src.database import SessionLocal, Transaction

def main():
    session = SessionLocal()
    
    try:
        # 1. Transaktion mit ID 1 suchen 
        transaction1 = session.query(Transaction).filter(Transaction.id == 1).first() # .first() gibt das erste Ergebnis zurück oder None, wenn nichts gefunden wurde
        
        if transaction1:
            print(f"Vorher: {transaction1.beschreibung}")
            # Beschreibung ändern
            transaction1.beschreibung = "Wocheneinkauf - AKTUALISIERT"
            # Speichern
            session.commit()
            print(f"Nachher: {transaction1.beschreibung}")
        else:
            print("Transaktion 1 nicht gefunden\n")
        
        # 2. Transaktion nach Verwendungszweck suchen
        transaction2 = session.query(Transaction).filter(Transaction.verwendungszweck == "Gehalt Dezember").first()
        if transaction2:
            print(f"Vorher: Betrag = {transaction2.betrag} EUR")
            # Betrag ändern
            transaction2.betrag = 2600.00
            # Speichern
            session.commit()
            print(f"Nachher: Betrag = {transaction2.betrag} EUR")
        else:
            print("Transaktion 2 nicht gefunden")
        
    finally:
        session.close()


if __name__ == "__main__":
    main()
