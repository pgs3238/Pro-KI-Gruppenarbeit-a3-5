"""
Unit Tests für das Search-Modul (Transaktionssuche)
"""

import pytest
from datetime import date
from src.database.models import Transaktion, Konto, Category
from src.database.search import search_transaktionen


class TestSearchTransaktionen:
    """Test-Suite für die search_transaktionen Funktion"""

    @pytest.fixture
    def setup_test_data(self, test_session, sample_konto, sample_category):
        """Erstellt umfangreiche Test-Transaktionen"""
        # Kategorie für Einnahmen
        income_cat = Category(name="Gehalt", category_type="Einnahme", icon="💼")
        test_session.add(income_cat)
        test_session.commit()

        # Verschiedene Transaktionen erstellen
        transaktionen = [
            Transaktion(
                konto_id=sample_konto.id,
                kategorie_id=sample_category.id,
                buchungstag=date(2026, 1, 15),
                beguenstigter="REWE Supermarkt",
                verwendungszweck="Lebensmittel Einkauf",
                iban_kontonummer="DE89370400440532013000",
                betrag=-75.50,
                waehrung="EUR",
                beschreibung="Wocheneinkauf",
            ),
            Transaktion(
                konto_id=sample_konto.id,
                kategorie_id=sample_category.id,
                buchungstag=date(2026, 1, 20),
                beguenstigter="ALDI Süd",
                verwendungszweck="Einkauf",
                betrag=-45.30,
                waehrung="EUR",
            ),
            Transaktion(
                konto_id=sample_konto.id,
                kategorie_id=income_cat.id,
                buchungstag=date(2026, 1, 25),
                beguenstigter="ABC GmbH",
                verwendungszweck="Gehalt Januar",
                betrag=2500.00,
                waehrung="EUR",
            ),
            Transaktion(
                konto_id=sample_konto.id,
                kategorie_id=sample_category.id,
                buchungstag=date(2026, 1, 10),
                beguenstigter="Amazon EU",
                verwendungszweck="Bestellung 123-456",
                betrag=-29.99,
                waehrung="EUR",
            ),
            Transaktion(
                konto_id=sample_konto.id,
                kategorie_id=sample_category.id,
                buchungstag=date(2026, 1, 5),
                beguenstigter="Stadtwerke München",
                verwendungszweck="Strom Abschlag",
                betrag=-120.00,
                waehrung="EUR",
            ),
        ]
        test_session.add_all(transaktionen)
        test_session.commit()
        return transaktionen

    def test_search_alle_transaktionen(self, test_session, setup_test_data):
        """Test: Alle Transaktionen ohne Filter abrufen"""
        # Act
        ergebnis = search_transaktionen(test_session)

        # Assert
        assert len(ergebnis) == 5
        assert all(isinstance(t, Transaktion) for t in ergebnis)

    def test_search_by_buchungstag(self, test_session, setup_test_data):
        """Test: Suche nach spezifischem Buchungstag"""
        # Act
        ergebnis = search_transaktionen(test_session, buchungstag=date(2026, 1, 15))

        # Assert
        assert len(ergebnis) == 1
        assert ergebnis[0].beguenstigter == "REWE Supermarkt"

    def test_search_by_beguenstigter_partial(self, test_session, setup_test_data):
        """Test: Teilstring-Suche nach Begünstigtem"""
        # Act
        ergebnis = search_transaktionen(test_session, beguenstigter="REWE")

        # Assert
        assert len(ergebnis) == 1
        assert "REWE" in ergebnis[0].beguenstigter

    def test_search_by_beguenstigter_case_insensitive(
        self, test_session, setup_test_data
    ):
        """Test: Case-insensitive Suche"""
        # Act
        ergebnis = search_transaktionen(test_session, beguenstigter="rewe")

        # Assert
        assert len(ergebnis) == 1
        assert "REWE" in ergebnis[0].beguenstigter

    def test_search_by_verwendungszweck(self, test_session, setup_test_data):
        """Test: Suche nach Verwendungszweck"""
        # Act
        ergebnis = search_transaktionen(test_session, verwendungszweck="Gehalt")

        # Assert
        assert len(ergebnis) == 1
        assert "Gehalt" in ergebnis[0].verwendungszweck

    def test_search_by_betrag_min(self, test_session, setup_test_data):
        """Test: Suche mit Mindestbetrag"""
        # Act
        ergebnis = search_transaktionen(test_session, betrag_min=100.0)

        # Assert
        assert len(ergebnis) == 1
        assert ergebnis[0].betrag == 2500.00

    def test_search_by_betrag_max(self, test_session, setup_test_data):
        """Test: Suche mit Maximalbetrag"""
        # Act
        ergebnis = search_transaktionen(test_session, betrag_max=-100.0)

        # Assert
        assert len(ergebnis) == 1
        assert ergebnis[0].betrag == -120.00

    def test_search_by_betrag_range(self, test_session, setup_test_data):
        """Test: Suche mit Betragsbereich"""
        # Act
        ergebnis = search_transaktionen(
            test_session, betrag_min=-80.0, betrag_max=-40.0
        )

        # Assert
        assert len(ergebnis) == 2
        betraege = [t.betrag for t in ergebnis]
        assert all(-80.0 <= b <= -40.0 for b in betraege)

    def test_search_by_betrag_abs_min(self, test_session, setup_test_data):
        """Test: Suche nach absolutem Mindestbetrag"""
        # Act
        ergebnis = search_transaktionen(test_session, betrag_min_abs=100.0)

        # Assert
        assert len(ergebnis) == 2  # -120 und 2500
        abs_betraege = [abs(t.betrag) for t in ergebnis]
        assert all(b >= 100.0 for b in abs_betraege)

    def test_search_by_betrag_abs_max(self, test_session, setup_test_data):
        """Test: Suche nach absolutem Maximalbetrag"""
        # Act
        ergebnis = search_transaktionen(test_session, betrag_max_abs=50.0)

        # Assert
        assert len(ergebnis) == 2  # -45.30 und -29.99
        abs_betraege = [abs(t.betrag) for t in ergebnis]
        assert all(b <= 50.0 for b in abs_betraege)

    def test_search_by_typ_expense(self, test_session, setup_test_data):
        """Test: Nur Ausgaben (negative Beträge)"""
        # Act
        ergebnis = search_transaktionen(test_session, typ="expense")

        # Assert
        assert len(ergebnis) == 4
        assert all(t.betrag < 0 for t in ergebnis)

    def test_search_by_typ_income(self, test_session, setup_test_data):
        """Test: Nur Einnahmen (positive Beträge)"""
        # Act
        ergebnis = search_transaktionen(test_session, typ="income")

        # Assert
        assert len(ergebnis) == 1
        assert all(t.betrag > 0 for t in ergebnis)

    def test_search_by_waehrung(self, test_session, setup_test_data):
        """Test: Suche nach Währung"""
        # Act
        ergebnis = search_transaktionen(test_session, waehrung="EUR")

        # Assert
        assert len(ergebnis) == 5
        assert all(t.waehrung == "EUR" for t in ergebnis)

    def test_search_by_kategorie(self, test_session, setup_test_data, sample_category):
        """Test: Suche nach Kategorie-Name"""
        # Act
        ergebnis = search_transaktionen(
            test_session, kategorie_name=sample_category.name
        )

        # Assert
        assert len(ergebnis) == 4
        assert all(t.kategorie.name == sample_category.name for t in ergebnis)

    def test_search_by_beschreibung(self, test_session, setup_test_data):
        """Test: Suche in Beschreibung"""
        # Act
        ergebnis = search_transaktionen(test_session, beschreibung="Wocheneinkauf")

        # Assert
        assert len(ergebnis) == 1
        assert ergebnis[0].beschreibung == "Wocheneinkauf"

    def test_search_multiple_filters(self, test_session, setup_test_data):
        """Test: Kombinierte Filter"""
        # Act
        ergebnis = search_transaktionen(
            test_session,
            typ="expense",
            betrag_min_abs=40.0,
            betrag_max_abs=80.0,
        )

        # Assert
        assert len(ergebnis) == 2  # -75.50 und -45.30
        assert all(t.betrag < 0 for t in ergebnis)
        assert all(40.0 <= abs(t.betrag) <= 80.0 for t in ergebnis)

    def test_search_no_results(self, test_session, setup_test_data):
        """Test: Suche ohne Ergebnisse"""
        # Act
        ergebnis = search_transaktionen(test_session, beguenstigter="NICHT_EXISTENT")

        # Assert
        assert len(ergebnis) == 0

    def test_search_invalid_betrag_range(self, test_session, setup_test_data):
        """Test: Fehler bei ungültigem Betragsbereich (min > max)"""
        # Act & Assert
        with pytest.raises(ValueError):
            search_transaktionen(test_session, betrag_min=100.0, betrag_max=50.0)

    def test_search_invalid_betrag_abs_range(self, test_session, setup_test_data):
        """Test: Fehler bei ungültigem absoluten Betragsbereich"""
        # Act & Assert
        with pytest.raises(ValueError):
            search_transaktionen(
                test_session, betrag_min_abs=100.0, betrag_max_abs=50.0
            )

    def test_search_order_by_datum(self, test_session, setup_test_data):
        """Test: Ergebnisse sind nach Datum sortiert"""
        # Act
        ergebnis = search_transaktionen(test_session)

        # Assert
        assert len(ergebnis) == 5
        # Sollte nach Buchungstag absteigend sortiert sein
        buchungstage = [t.buchungstag for t in ergebnis]
        assert buchungstage == sorted(buchungstage, reverse=True)
