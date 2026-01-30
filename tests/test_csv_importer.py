"""
Unit Tests für das CSV-Importer-Modul
"""

import pytest
from datetime import date
import tempfile
import os
from src.database.models import Transaktion
from src.database.csv_importer import CSVTransaktionImporter
from src.database import SessionLocal


class TestCSVImporterParseMethods:
    """Test-Suite für Parse-Methoden"""

    def test_parse_date_valid(self):
        """Test: Gültiges Datum parsen"""
        # Arrange
        with SessionLocal() as session:
            importer = CSVTransaktionImporter(session, {})

            # Act
            result = importer.parse_date("15.01.2026")

            # Assert
            assert result == date(2026, 1, 15)

    def test_parse_float_positive(self):
        """Test: Positive Zahl parsen"""
        # Arrange
        with SessionLocal() as session:
            importer = CSVTransaktionImporter(session, {})

            # Act
            result = importer.parse_float("1.234,56")

            # Assert
            assert result == 1234.56

    def test_parse_float_negative(self):
        """Test: Negative Zahl parsen"""
        # Arrange
        with SessionLocal() as session:
            importer = CSVTransaktionImporter(session, {})

            # Act
            result = importer.parse_float("-50,30")

            # Assert
            assert result == -50.30

    def test_parse_float_ohne_tausender(self):
        """Test: Zahl ohne Tausendertrennzeichen"""
        # Arrange
        with SessionLocal() as session:
            importer = CSVTransaktionImporter(session, {})

            # Act
            result = importer.parse_float("45,99")

            # Assert
            assert result == 45.99


class TestCSVImporterDetectDelimiter:
    """Test-Suite für detect_delimiter Funktion"""

    def test_detect_delimiter_semicolon(self):
        """Test: Semikolon als Delimiter erkennen"""
        # Arrange
        csv_content = """Datum;Empfänger;Betrag
15.01.2026;REWE;-50,00
16.01.2026;ALDI;-30,00"""

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv", encoding="utf-8"
        ) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with SessionLocal() as session:
                importer = CSVTransaktionImporter(session, {})
                
                # Act
                delimiter = importer.detect_delimiter(temp_path)

                # Assert
                assert delimiter == ";"
        finally:
            os.unlink(temp_path)

    def test_detect_delimiter_comma(self):
        """Test: Komma als Delimiter erkennen"""
        # Arrange
        csv_content = """Date,Recipient,Amount
2026-01-15,REWE,-50.00
2026-01-16,ALDI,-30.00"""

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv", encoding="utf-8"
        ) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with SessionLocal() as session:
                importer = CSVTransaktionImporter(session, {})
                
                # Act
                delimiter = importer.detect_delimiter(temp_path)

                # Assert
                assert delimiter == ","
        finally:
            os.unlink(temp_path)


class TestCSVImporterImportCSV:
    """Test-Suite für import_csv Funktion"""

    def test_import_basic_csv(self, sample_konto):
        """Test: Einfachen CSV-Import"""
        # Arrange
        csv_content = """Buchungstag;Begünstigter / Auftraggeber;Verwendungszweck;Kontonummer / IBAN;Betrag;Währung
15.01.2026;REWE Markt;Lebensmittel;DE89370400440532013000;-50,30;EUR
16.01.2026;ALDI Süd;Einkauf;DE89370400440532013001;-35,99;EUR"""

        mapping = {
            "buchungstag": "Buchungstag",
            "beguenstigter": "Begünstigter / Auftraggeber",
            "verwendungszweck": "Verwendungszweck",
            "iban_kontonummer": "Kontonummer / IBAN",
            "betrag": "Betrag",
            "waehrung": "Währung",
        }

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv", encoding="utf-8"
        ) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with SessionLocal() as session:
                importer = CSVTransaktionImporter(
                    session, mapping, header_row=1, konto_id=sample_konto.id
                )

                # Act
                importer.import_csv(temp_path)
                session.commit()

                # Assert
                transaktionen = session.query(Transaktion).filter_by(konto_id=sample_konto.id).all()
                assert len(transaktionen) >= 2

                # Prüfe erste Transaktion
                rewe = next((t for t in transaktionen if "REWE" in t.beguenstigter), None)
                assert rewe is not None
                assert rewe.betrag == -50.30
                assert rewe.buchungstag == date(2026, 1, 15)
        finally:
            os.unlink(temp_path)

    def test_import_positive_betrag(self, sample_konto):
        """Test: Import mit positiven Beträgen (Einnahmen)"""
        # Arrange
        csv_content = """Buchungstag;Begünstigter;Betrag
25.01.2026;Arbeitgeber;2500,00"""

        mapping = {
            "buchungstag": "Buchungstag",
            "beguenstigter": "Begünstigter",
            "betrag": "Betrag",
        }

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv", encoding="utf-8"
        ) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with SessionLocal() as session:
                importer = CSVTransaktionImporter(
                    session, mapping, konto_id=sample_konto.id
                )

                # Act
                importer.import_csv(temp_path)
                session.commit()

                # Assert
                transaktion = session.query(Transaktion).filter_by(beguenstigter="Arbeitgeber").first()
                assert transaktion is not None
                assert transaktion.betrag == 2500.00
        finally:
            os.unlink(temp_path)
