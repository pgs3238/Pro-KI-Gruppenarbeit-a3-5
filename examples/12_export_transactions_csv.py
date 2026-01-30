"""
Skript zum Exportieren der Transaktionen als CSV-Datei
"""

import csv
from pathlib import Path
from src.database.connection import SessionLocal
from src.database.models import Transaktion


def export_transactions_to_csv(output_path: str = "transaktionen_export.csv"):
    """Exportiert alle Transaktionen in eine CSV-Datei"""

    session = SessionLocal()

    try:
        # Alle Transaktionen laden
        transaktionen = session.query(Transaktion).all()

        if not transaktionen:
            print("Keine Transaktionen gefunden.")
            return

        # CSV-Datei schreiben
        with open(output_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")

            # Header schreiben
            writer.writerow(
                [
                    "ID",
                    "Buchungstag",
                    "Begünstigter",
                    "Verwendungszweck",
                    "IBAN/Kontonummer",
                    "Betrag",
                    "Währung",
                    "Beschreibung",
                    "Kategorie_ID",
                    "Konto_ID",
                    "Erstellt_am",
                ]
            )

            # Daten schreiben
            for t in transaktionen:
                writer.writerow(
                    [
                        t.id,
                        t.buchungstag,
                        t.beguenstigter,
                        t.verwendungszweck,
                        t.iban_kontonummer,
                        t.betrag,
                        t.waehrung,
                        t.beschreibung,
                        t.kategorie_id,
                        t.konto_id,
                        t.created_at,
                    ]
                )

        print(f"✓ {len(transaktionen)} Transaktionen exportiert nach: {output_path}")

    finally:
        session.close()


if __name__ == "__main__":
    # Standard-Export in den data-Ordner
    output_file = Path(__file__).parent.parent / "data" / "transaktionen_export.csv"
    export_transactions_to_csv(str(output_file))
