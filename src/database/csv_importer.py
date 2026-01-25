import csv
from datetime import datetime
from .models import Transaktion

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
