"""
Unit Tests für das Konto-Manager Modul
"""

import pytest
from src.database.konto_manager import KontoManager
from src.database.models import Konto, Transaktion
from datetime import date


class TestKontoManager:
    """Test-Suite für KontoManager-Funktionen"""

    def test_erstelle_konto(self, test_session):
        """Test: Konto erfolgreich erstellen"""
        # Arrange & Act
        konto = KontoManager.erstelle_konto(
            session=test_session,
            kontoname="Sparkonto Test",
            kontonummer="DE89370400440532013001",
            kontotyp="Sparkonto",
            bankname="Sparkasse",
            kontostand=500.0,
            waehrung="EUR",
            bic="COBADEFFXXX",
        )

        # Assert
        assert konto is not None
        assert konto.id is not None
        assert konto.kontoname == "Sparkonto Test"
        assert konto.kontonummer == "DE89370400440532013001"
        assert konto.kontotyp == "Sparkonto"
        assert konto.bankname == "Sparkasse"
        assert konto.kontostand == 500.0
        assert konto.waehrung == "EUR"
        assert konto.bic == "COBADEFFXXX"

    def test_erstelle_konto_minimal(self, test_session):
        """Test: Konto mit minimalen Angaben erstellen"""
        # Arrange & Act
        konto = KontoManager.erstelle_konto(
            session=test_session, kontoname="Minimalkonto"
        )

        # Assert
        assert konto is not None
        assert konto.kontoname == "Minimalkonto"
        assert konto.kontotyp == "Girokonto"  # Default-Wert
        assert konto.kontostand == 0.0  # Default-Wert
        assert konto.waehrung == "EUR"  # Default-Wert

    def test_hole_konto(self, test_session, sample_konto):
        """Test: Konto nach ID abrufen"""
        # Act
        konto = KontoManager.hole_konto(test_session, sample_konto.id)

        # Assert
        assert konto is not None
        assert konto.id == sample_konto.id
        assert konto.kontoname == sample_konto.kontoname

    def test_hole_konto_nicht_vorhanden(self, test_session):
        """Test: Nicht vorhandenes Konto abrufen gibt None zurück"""
        # Act
        konto = KontoManager.hole_konto(test_session, 999)

        # Assert
        assert konto is None

    def test_hole_konto_by_iban(self, test_session, sample_konto):
        """Test: Konto nach IBAN abrufen"""
        # Act
        konto = KontoManager.hole_konto_by_iban(test_session, sample_konto.iban)

        # Assert
        assert konto is not None
        assert konto.iban == sample_konto.iban
        assert konto.kontoname == sample_konto.kontoname

    def test_hole_alle_konten(self, test_session):
        """Test: Alle Konten abrufen"""
        # Arrange
        KontoManager.erstelle_konto(test_session, "Konto 1")
        KontoManager.erstelle_konto(test_session, "Konto 2")
        KontoManager.erstelle_konto(test_session, "Konto 3")

        # Act
        konten = KontoManager.hole_alle_konten(test_session)

        # Assert
        assert len(konten) == 3
        assert all(isinstance(k, Konto) for k in konten)

    def test_aktualisiere_kontostand(self, test_session, sample_konto):
        """Test: Kontostand aktualisieren"""
        # Arrange
        neuer_stand = 1500.0

        # Act
        konto = KontoManager.aktualisiere_kontostand(
            test_session, sample_konto.id, neuer_stand
        )

        # Assert
        assert konto.kontostand == neuer_stand

    def test_berechne_kontostand_ohne_transaktionen(self, test_session, sample_konto):
        """Test: Kontostand berechnen ohne Transaktionen"""
        # Act
        kontostand = KontoManager.berechne_kontostand_aus_transaktionen(
            test_session, sample_konto.id, initialstand=sample_konto.kontostand
        )

        # Assert
        assert kontostand == sample_konto.kontostand  # Initial-Kontostand

    def test_berechne_kontostand_mit_transaktionen(
        self, test_session, sample_konto, sample_category
    ):
        """Test: Kontostand mit Transaktionen berechnen"""
        # Arrange
        initial_stand = sample_konto.kontostand

        # Transaktion 1: -50 EUR
        t1 = Transaktion(
            konto_id=sample_konto.id,
            kategorie_id=sample_category.id,
            buchungstag=date(2026, 1, 15),
            beguenstigter="Supermarkt",
            verwendungszweck="Einkauf",
            betrag=-50.0,
            waehrung="EUR",
        )
        test_session.add(t1)

        # Transaktion 2: +200 EUR
        t2 = Transaktion(
            konto_id=sample_konto.id,
            kategorie_id=sample_category.id,
            buchungstag=date(2026, 1, 16),
            beguenstigter="Arbeitgeber",
            verwendungszweck="Gehalt",
            betrag=200.0,
            waehrung="EUR",
        )
        test_session.add(t2)
        test_session.commit()

        # Act
        kontostand = KontoManager.berechne_kontostand_aus_transaktionen(
            test_session, sample_konto.id, initialstand=initial_stand
        )

        # Assert
        # Initial: 1000, -50, +200 = 1150
        assert kontostand == initial_stand + (-50.0) + 200.0

    def test_loesche_konto_ohne_transaktionen(self, test_session, sample_konto):
        """Test: Konto ohne Transaktionen löschen"""
        # Arrange
        konto_id = sample_konto.id

        # Act
        erfolg = KontoManager.lösche_konto(test_session, konto_id)

        # Assert
        assert erfolg is True
        assert KontoManager.hole_konto(test_session, konto_id) is None

    def test_loesche_konto_mit_transaktionen(self, test_session, sample_transaktion):
        """Test: Konto mit Transaktionen wird gelöscht (inkl. Transaktionen)"""
        # Arrange
        konto_id = sample_transaktion.konto_id

        # Act
        erfolg = KontoManager.lösche_konto(test_session, konto_id)

        # Assert
        assert erfolg is True
        assert KontoManager.hole_konto(test_session, konto_id) is None

    def test_aktualisiere_konto_details(self, test_session, sample_konto):
        """Test: Konto-Details aktualisieren"""
        # Arrange
        neue_daten = {
            "kontoname": "Neuer Name",
            "bankname": "Neue Bank",
            "kontotyp": "Sparkonto",
        }

        # Act
        konto = KontoManager.aktualisiere_kontoinformationen(
            test_session, sample_konto.id, **neue_daten
        )

        # Assert
        assert konto.kontoname == "Neuer Name"
        assert konto.bankname == "Neue Bank"
        assert konto.kontotyp == "Sparkonto"

    def test_hole_konten_nach_typ(self, test_session):
        """Test: Konten nach Typ filtern"""
        # Arrange
        KontoManager.erstelle_konto(test_session, "Giro 1", kontotyp="Girokonto")
        KontoManager.erstelle_konto(test_session, "Giro 2", kontotyp="Girokonto")
        KontoManager.erstelle_konto(test_session, "Spar 1", kontotyp="Sparkonto")

        # Act
        girokonten = (
            test_session.query(Konto).filter(Konto.kontotyp == "Girokonto").all()
        )

        # Assert
        assert len(girokonten) == 2
        assert all(k.kontotyp == "Girokonto" for k in girokonten)
