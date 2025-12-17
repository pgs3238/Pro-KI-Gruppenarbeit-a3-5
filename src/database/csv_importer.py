import csv
from datetime import datetime
from models import Transaktion

CSV_TO_MODEL_MAPPING = {
    "Buchungstag": "buchungstag",
    "Begünstigter / Auftraggeber": "beguenstigter",
    "Verwendungszweck": "verwendungszweck",
    "IBAN / Kontonummer": "iban_kontonummer",
    "Betrag": "betrag",
    "Währung": "waehrung",
}

class CSVTransaktionImporter:
    def __init__(self, session):
        self.session = session

    def parse_date(self, value):
        # Adjust format if your bank uses a different one
        return datetime.strptime(value, "%d.%m.%Y").date()

    def parse_float(self, value):
        # Handle German number format: "1.234,56"
        value = value.replace(".", "").replace(",", ".")
        return float(value)

    def import_csv(self, file_path):
        with open(file_path, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')

            for row in reader:
                print(row)  # <-- DEBUG
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

# # 3. Usage Example

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from models import Base

# engine = create_engine("sqlite:///database.db")
# Session = sessionmaker(bind=engine)
# session = Session()

# Base.metadata.create_all(engine)

# importer = CSVTransaktionImporter(session)
# importer.import_csv("transaktionen.csv")