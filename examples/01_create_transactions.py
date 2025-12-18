# Beisiel: Erstellen und Speichern von Transaktionen in der Datenbank
from src.database import init_db, SessionLocal, Transaktion # Hier Importieren wir die Datenbank, da sie als Package definiert ist
from datetime import date

def main():
    init_db() # Initialisiert die Datenbank und erstellt alle Tabellen basierend auf den ORM-Modellen
    
    # 2. Session erstellen
    session = SessionLocal() # Erstellt eine neue Session für Datenbankoperationen
    
    try:
        # 3. Beispiel-Transaktionen erstellen
        transaction1 = Transaktion(
            buchungstag=date(2024, 12, 10),
            beguenstigter="REWE Supermarkt",
            verwendungszweck="Lebensmitteleinkauf",
            iban_kontonummer="DE89370400440532013000",
            betrag=-45.67,
            waehrung="EUR",
            beschreibung="Wocheneinkauf"
        )
        
        transaction2 = Transaktion(
            buchungstag=date(2024, 12, 11),
            beguenstigter="Max Mustermann AG",
            verwendungszweck="Gehalt Dezember",
            iban_kontonummer="DE12500105170648489890",
            betrag=2500.00,
            waehrung="EUR",
            beschreibung="Monatliches Gehalt"
        )
        
        transaction3 = Transaktion(
            buchungstag=date(2024, 12, 12),
            beguenstigter="Deutsche Bahn",
            verwendungszweck="Bahnticket Berlin-München",
            iban_kontonummer="DE44500105175407324931",
            betrag=-89.90,
            waehrung="EUR",
            beschreibung="Reisekosten"
        )
        
        # 4. Zur Session hinzufügen
        session.add(transaction1)
        session.add(transaction2)
        session.add(transaction3)
        
        # 5. In Datenbank speichern
        session.commit()
        print("✓ 3 Transaktionen erfolgreich gespeichert!")
        
    except Exception as e:
        session.rollback() # Bei Fehlern Änderungen zurückrollen
        print(f"✗ Fehler: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
