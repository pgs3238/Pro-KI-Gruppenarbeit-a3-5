# Beispiel: Löschen einer Transaktion aus der Datenbank
from src.database import SessionLocal, Transaction

def main():
    session = SessionLocal()
    
    try:
        # Transaktion mit ID 3 suchen
        transaction = session.query(Transaction).filter(Transaction.id == 3).first()        
        if transaction:
            print(f"Zu löschen: {transaction.beguenstigter} | {transaction.betrag} EUR")
            # Löschen
            session.delete(transaction)
            session.commit()
            print("Transaktion erfolgreich gelöscht!")
        else:
            print("Transaktion nicht gefunden")
        
        # Überprüfen
        count = session.query(Transaction).count()
        print(f"\nVerbleibende Transaktionen: {count}")
        
    finally:
        session.close()


if __name__ == "__main__":
    main()
