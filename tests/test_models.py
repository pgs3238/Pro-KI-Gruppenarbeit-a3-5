"""
Unit Tests für die Datenbank-Modelle
"""

import pytest
from datetime import date, datetime
from src.database.models import Konto, Transaktion, Category, CategoryRules


class TestKontoModel:
    """Test-Suite für das Konto-Modell"""

    def test_konto_erstellen(self, test_session):
        """Test: Konto-Objekt erfolgreich erstellen"""
        # Arrange & Act
        konto = Konto(
            kontoname="Test Konto",
            kontonummer="DE89370400440532013000",
            iban="DE89370400440532013000",
            kontotyp="Girokonto",
            bankname="Test Bank",
            kontostand=500.0,
            waehrung="EUR",
            bic="COBADEFFXXX",
            farbe="#FF0000",
        )
        test_session.add(konto)
        test_session.commit()

        # Assert
        assert konto.id is not None
        assert konto.kontoname == "Test Konto"
        assert konto.erstellt_am is not None
        assert konto.aktualisiert_am is not None

    def test_konto_unique_kontoname(self, test_session, sample_konto):
        """Test: Kontoname muss eindeutig sein"""
        # Arrange & Act
        duplikat = Konto(kontoname=sample_konto.kontoname)
        test_session.add(duplikat)

        # Assert
        with pytest.raises(Exception):  # Unique Constraint Verletzung
            test_session.commit()

    def test_konto_default_werte(self, test_session):
        """Test: Default-Werte werden korrekt gesetzt"""
        # Arrange & Act
        konto = Konto(kontoname="Minimal Konto", kontotyp="Girokonto")
        test_session.add(konto)
        test_session.commit()

        # Assert
        assert konto.kontostand == 0.0
        assert konto.waehrung == "EUR"
        assert konto.kontotyp == "Girokonto"

    def test_konto_repr(self, sample_konto):
        """Test: String-Repräsentation des Kontos"""
        # Act
        repr_str = repr(sample_konto)

        # Assert
        assert "Konto" in repr_str
        assert sample_konto.kontoname in repr_str


class TestTransaktionModel:
    """Test-Suite für das Transaktions-Modell"""

    def test_transaktion_erstellen(self, test_session, sample_konto, sample_category):
        """Test: Transaktion erfolgreich erstellen"""
        # Arrange & Act
        transaktion = Transaktion(
            konto_id=sample_konto.id,
            kategorie_id=sample_category.id,
            buchungstag=date(2026, 1, 15),
            beguenstigter="Test Empfänger",
            verwendungszweck="Test Zweck",
            iban_kontonummer="DE89370400440532013001",
            betrag=-100.0,
            waehrung="EUR",
            beschreibung="Test Beschreibung",
        )
        test_session.add(transaktion)
        test_session.commit()

        # Assert
        assert transaktion.id is not None
        assert transaktion.konto_id == sample_konto.id
        assert transaktion.kategorie_id == sample_category.id
        assert transaktion.created_at is not None

    def test_transaktion_beziehung_zu_konto(
        self, test_session, sample_konto, sample_category
    ):
        """Test: Beziehung zwischen Transaktion und Konto"""
        # Arrange
        transaktion = Transaktion(
            konto_id=sample_konto.id,
            kategorie_id=sample_category.id,
            buchungstag=date(2026, 1, 15),
            beguenstigter="Test",
            betrag=-50.0,
        )
        test_session.add(transaktion)
        test_session.commit()

        # Act
        konto = test_session.query(Konto).filter(Konto.id == sample_konto.id).first()

        # Assert
        assert len(konto.transaktionen) == 1
        assert konto.transaktionen[0].betrag == -50.0

    def test_transaktion_negative_ausgabe(self, test_session, sample_konto, sample_category):
        """Test: Ausgaben haben negativen Betrag"""
        # Arrange & Act
        ausgabe = Transaktion(
            konto_id=sample_konto.id,
            kategorie_id=sample_category.id,
            buchungstag=date.today(),
            beguenstigter="Supermarkt",
            betrag=-75.50,
        )
        test_session.add(ausgabe)
        test_session.commit()

        # Assert
        assert ausgabe.betrag < 0

    def test_transaktion_positive_einnahme(self, test_session, sample_konto, sample_category):
        """Test: Einnahmen haben positiven Betrag"""
        # Arrange & Act
        einnahme = Transaktion(
            konto_id=sample_konto.id,
            kategorie_id=sample_category.id,
            buchungstag=date.today(),
            beguenstigter="Arbeitgeber",
            betrag=2500.00,
        )
        test_session.add(einnahme)
        test_session.commit()

        # Assert
        assert einnahme.betrag > 0


class TestCategoryModel:
    """Test-Suite für das Category-Modell"""

    def test_category_erstellen(self, test_session):
        """Test: Kategorie erfolgreich erstellen"""
        # Arrange & Act
        category = Category(
            name="Transport",
            category_type="Ausgabe",
            icon="🚗",
            farbe="#3498DB",
        )
        test_session.add(category)
        test_session.commit()

        # Assert
        assert category.id is not None
        assert category.name == "Transport"
        assert category.category_type == "Ausgabe"

    def test_category_unique_name(self, test_session, sample_category):
        """Test: Kategoriename muss eindeutig sein"""
        # Arrange & Act
        duplikat = Category(
            name=sample_category.name,
            category_type="Ausgabe",
        )
        test_session.add(duplikat)

        # Assert
        with pytest.raises(Exception):  # Unique Constraint
            test_session.commit()

    def test_category_types(self, test_session):
        """Test: Unterschiedliche Kategorietypen (Einnahme/Ausgabe)"""
        # Arrange & Act
        income_cat = Category(name="Gehalt", category_type="Einnahme")
        expense_cat = Category(name="Miete", category_type="Ausgabe")
        
        test_session.add_all([income_cat, expense_cat])
        test_session.commit()

        # Assert
        assert income_cat.category_type == "Einnahme"
        assert expense_cat.category_type == "Ausgabe"


class TestCategoryRulesModel:
    """Test-Suite für das CategoryRules-Modell"""

    def test_category_rule_erstellen(self, test_session, sample_category):
        """Test: Kategorieregel erfolgreich erstellen"""
        # Arrange & Act
        rule = CategoryRules(
            category_name=sample_category.name,
            keywords="edeka,rewe,aldi,lidl",
        )
        test_session.add(rule)
        test_session.commit()

        # Assert
        assert rule.id is not None
        assert rule.category_name == sample_category.name
        assert "edeka" in rule.keywords

    def test_category_rule_beziehung(self, test_session, sample_category):
        """Test: Beziehung zwischen CategoryRules und Category"""
        # Arrange
        rule = CategoryRules(
            category_name=sample_category.name,
            keywords="test,keyword",
        )
        test_session.add(rule)
        test_session.commit()

        # Act
        category = (
            test_session.query(Category)
            .filter(Category.name == sample_category.name)
            .first()
        )

        # Assert
        assert len(category.rules) == 1
        assert category.rules[0].keywords == "test,keyword"
