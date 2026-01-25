import csv
from datetime import datetime
from .models import Transaktion

"""
Imports transaction data from CSV files into the database using SQLAlchemy sessions.

Attributes: 
session:                SQLAlchemy session for database operations. 
mapping:                Dictionary mapping model fields to CSV column headers.
header_row:             Index for the CSV-header row (0-based).
skip_footer:            Number of rows at the end of the file to skip.
konto_id:               Optional account ID to assign to each transaction.
candidate_delimiters:   List of possible CSV delimiters to try during detection.
"""
class CSVTransaktionImporter:
    def __init__(self, session, mapping, header_row=1, skip_footer=0, konto_id=None):
        self.session = session
        self.mapping = mapping
        self.header_row = header_row - 1
        self.skip_footer = skip_footer
        self.konto_id = konto_id
        self.candidate_delimiters = [",", ";", "\t", "|"]

    """
    Parses a string into a Python date object.
    Args:       value: Date string in the format 'dd.mm.yyyy'.
    Returns:    datetime.date object.
    """
    def parse_date(self, value):
        return datetime.strptime(value, "%d.%m.%Y").date()

    """
    Converts a CSV string representing a number into a float.
    Handles European-style numbers with '.' as thousands separator
    and ',' as decimal separator.
    Args:       value: Numeric string, e.g., '1.234,56'.
    Returns:    float value.
    """
    def parse_float(self, value):
        return float(value.replace(".", "").replace(",", "."))
    
    """
    Detects the delimiter used in a CSV file.
    Reads the first few lines of the file and determines which candidate
    delimiter is most consistent across lines. Falls back to semicolon
    if detection fails.
    Args:       file_path:      Path to the CSV file.
                sample_lines:   Number of lines to sample for detection (default 10).
    Returns:    Detected delimiter as a string.
    """
    def detect_delimiter(self, file_path, sample_lines=10):
        lines = []
        with open(file_path, encoding="utf-8-sig") as f:
            for _ in range(sample_lines):
                line = f.readline()
                if not line:
                    break
                lines.append(line)

        delimiter_scores = {}
        for delim in self.candidate_delimiters:
            counts = [line.count(delim) for line in lines]
            # Prefer delimiters with consistent count across lines
            if len(set(counts)) == 1 and counts[0] > 0:
                delimiter_scores[delim] = counts[0]

        if delimiter_scores:
            # Pick delimiter with highest count (most columns)
            print(f"DEBUG: Delimiter scores detected: {delimiter_scores}")
            detected = max(delimiter_scores, key=lambda k: delimiter_scores[k])
            print(f"DEBUG: Chosen delimiter: '{detected}'")
        else:
            # fallback
            print(f"DEBUG: No suitable delimiter found, falling back to default '{self.default_delimiter}'")
            detected = ";"

        return detected
    
    """
    Imports transactions from a CSV file into the database.
    1. Detects the CSV delimiter automatically.
    2. Reads the CSV and applies the header mapping.
    3. Converts date and amount fields to proper Python types.
    4. Adds konto_id and sets currency to EUR.
    5. Inserts all transactions into the database and commits.
    Args:        file_path:     Path to the CSV file to import.
    """
    def import_csv(self, file_path):
        delimiter = self.detect_delimiter(file_path)


        with open(file_path, encoding="utf-8-sig") as f:
            #rows = list(csv.reader(f, delimiter=";"))
            rows = list(csv.reader(f, delimiter=delimiter))

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
