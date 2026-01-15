import csv
from datetime import datetime
from .models import Transaktion


# # CSV-Feldzuordnung: Hier werden Felder in der CSV-Datei mit den Feldern der Datenbank zugeordnet. 
# CSV_TO_MODEL_MAPPING = {
#     "Buchungstag": "buchungstag",
#     "Begünstigter / Auftraggeber": "beguenstigter",
#     "Verwendungszweck": "verwendungszweck",
#     "IBAN / Kontonummer": "iban_kontonummer",
#     "Betrag": "betrag",
#     "Währung": "waehrung",
# }

# # Klasse zum Einlesen von CSV-Transaktionen, Konvertieren und Speichern dieser in die Datenbank.
# class CSVTransaktionImporter:
#     def __init__(self, session):
#         self.session = session

#     def parse_date(self, value):
#         return datetime.strptime(value, "%d.%m.%Y").date()

#     def parse_float(self, value):
#         # Umgang mit deutschem Zahlenformat: "1.234,56"
#         # SQLite kann das deutsche Zahlenformat nicht verarbeiten, daher wird es hier in das englische Zahlenformat umgewandelt.
#         value = value.replace(".", "").replace(",", ".")
#         return float(value)

#     def import_csv(self, file_path):
#         with open(file_path, newline="", encoding="utf-8-sig") as csvfile:
#             # Delimiter = Zeichen, das in der CSV-Datei die einzelnen Spalten voneinander trennt.
#             reader = csv.DictReader(csvfile, delimiter=';')

#             for row in reader:
#                 # print(row)  # <-- DEBUG
#                 data = {}

#                 for csv_col, model_col in CSV_TO_MODEL_MAPPING.items():
#                     value = row.get(csv_col)

#                     if value is None or value == "":
#                         continue

#                     if model_col == "buchungstag":
#                         value = self.parse_date(value)
#                     elif model_col == "betrag":
#                         value = self.parse_float(value)

#                     data[model_col] = value

#                 transaktion = Transaktion(**data)
#                 self.session.add(transaktion)

#             self.session.commit()

class CSVTransaktionImporter:
    def __init__(self, session, mapping, header_row=1, skip_footer=0, konto_id=None):
        self.session = session
        self.mapping = mapping
        self.header_row = header_row - 1
        self.skip_footer = skip_footer
        self.konto_id = konto_id

    def parse_date(self, value):
        return datetime.strptime(value, "%d.%m.%Y").date()

    def parse_float(self, value):
        return float(value.replace(".", "").replace(",", "."))

    def import_csv(self, file_path):
        with open(file_path, encoding="utf-8-sig") as f:
            rows = list(csv.reader(f, delimiter=";"))

        data_rows = rows[self.header_row + 1:]
        if self.skip_footer:
            data_rows = data_rows[:-self.skip_footer]

        headers = rows[self.header_row]

        for row in data_rows:
            record = {}
            for model_field, csv_header in self.mapping.items():
                idx = headers.index(csv_header)
                value = row[idx].strip()

                if model_field == "buchungstag":
                    value = self.parse_date(value)
                elif model_field == "betrag":
                    value = self.parse_float(value)

                record[model_field] = value

            record["konto_id"] = self.konto_id
            record["waehrung"] = "EUR"

            self.session.add(Transaktion(**record))

        self.session.commit()
