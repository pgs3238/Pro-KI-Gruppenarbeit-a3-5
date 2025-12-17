import csv
from datetime import datetime
from .models import Transaktion


# CSV-Feldzuordnung: Hier werden Felder in der CSV-Datei mit den Feldern der Datenbank zugeordnet. 
CSV_TO_MODEL_MAPPING = {
    "Buchungstag": "buchungstag",
    "Begünstigter / Auftraggeber": "beguenstigter",
    "Verwendungszweck": "verwendungszweck",
    "IBAN / Kontonummer": "iban_kontonummer",
    "Betrag": "betrag",
    "Währung": "waehrung",
}

# Klasse zum Einlesen von CSV-Transaktionen, Konvertieren und Speichern dieser in die Datenbank.
class CSVTransaktionImporter:
    def __init__(self, session):
        self.session = session

    def parse_date(self, value):
        return datetime.strptime(value, "%d.%m.%Y").date()

    def parse_float(self, value):
        # Umgang mit deutschem Zahlenformat: "1.234,56"
        # SQLite kann das deutsche Zahlenformat nicht verarbeiten, daher wird es hier in das englische Zahlenformat umgewandelt.
        value = value.replace(".", "").replace(",", ".")
        return float(value)

    def import_csv(self, file_path):
        with open(file_path, newline="", encoding="utf-8-sig") as csvfile:
            # Delimiter = Zeichen, das in der CSV-Datei die einzelnen Spalten voneinander trennt.
            reader = csv.DictReader(csvfile, delimiter=';')

            for row in reader:
                # print(row)  # <-- DEBUG
                data = {}

                for csv_col, model_col in CSV_TO_MODEL_MAPPING.items():
                    value = row.get(csv_col)

                    if value is None or value == "":
                        continue

                    if model_col == "buchungstag":
                        value = self.parse_date(value)
                    elif model_col == "betrag":
                        value = self.parse_float(value)

                    data[model_col] = value

                transaktion = Transaktion(**data)
                self.session.add(transaktion)

            self.session.commit()
