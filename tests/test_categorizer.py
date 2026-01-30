"""
Unit Tests für das Categorizer-Modul (Regelbasierte Kategorisierung)

Hinweis: Die Categorizer-Klasse verwaltet ihre eigene Session intern
"""

import pytest
from datetime import date
from src.database.models import Category, CategoryRules, Transaktion
from src.categories.categorizer_rules import Categorizer
from src.categories.categories import add_category
from src.database import SessionLocal


@pytest.fixture
def categorizer():
    """Fixture: Erstelle Categorizer-Instanz"""
    return Categorizer()


@pytest.fixture
def setup_categorizer_rules():
    """Fixture: Erstelle Testkategorien und Regeln"""
    # Lösche alte Test-Kategorien falls vorhanden
    with SessionLocal() as session:
        session.query(CategoryRules).filter(CategoryRules.category_name.in_(["TestFood", "TestSalary"])).delete(synchronize_session=False)
        session.query(Category).filter(Category.name.in_(["TestFood", "TestSalary"])).delete(synchronize_session=False)
        session.commit()
    
    # Erstelle neue Kategorien mit eindeutigen Keywords
    add_category(name="TestFood", category_type="Ausgabe", icon="🍔")
    add_category(name="TestSalary", category_type="Einnahme", icon="💼")
    
    # Erstelle Regeln mit eindeutigen Keywords
    with SessionLocal() as session:
        rule1 = CategoryRules(
            category_name="TestFood",
            keywords="testfood,uniquemarket,specialshop"
        )
        rule2 = CategoryRules(
            category_name="TestSalary",
            keywords="testsalary,uniqueemployer,testcompany"
        )
        session.add_all([rule1, rule2])
        session.commit()
    
    yield
    
    # Cleanup
    with SessionLocal() as session:
        session.query(CategoryRules).filter(CategoryRules.category_name.in_(["TestFood", "TestSalary"])).delete(synchronize_session=False)
        session.query(Category).filter(Category.name.in_(["TestFood", "TestSalary"])).delete(synchronize_session=False)
        session.commit()


class TestCategorizerSuggestCategory:
    """Test-Suite für suggest_category Methode"""

    def test_suggest_category_rewe(self, categorizer, setup_categorizer_rules, sample_konto):
        """Test: UniqueMarket wird als TestFood kategorisiert"""
        # Arrange
        with SessionLocal() as session:
            transaktion = Transaktion(
                konto_id=sample_konto.id,
                buchungstag=date(2026, 1, 15),
                beguenstigter="UniqueMarket Store",
                verwendungszweck="Einkauf",
                betrag=-50.30,
            )
            session.add(transaktion)
            session.commit()
            transaktion_id = transaktion.id

        # Act
        with SessionLocal() as session:
            transaktion = session.query(Transaktion).get(transaktion_id)
            kategorie = categorizer.suggest_category(transaktion)

        # Assert
        assert kategorie is not None
        assert kategorie.name == "TestFood"

    def test_suggest_category_case_insensitive(self, categorizer, setup_categorizer_rules, sample_konto):
        """Test: Case-insensitive matching"""
        # Arrange
        with SessionLocal() as session:
            transaktion = Transaktion(
                konto_id=sample_konto.id,
                buchungstag=date(2026, 1, 16),
                beguenstigter="SPECIALSHOP Premium",
                verwendungszweck="Shopping",
                betrag=-35.99,
            )
            session.add(transaktion)
            session.commit()
            transaktion_id = transaktion.id

        # Act
        with SessionLocal() as session:
            transaktion = session.query(Transaktion).get(transaktion_id)
            kategorie = categorizer.suggest_category(transaktion)

        # Assert
        assert kategorie is not None
        assert kategorie.name == "TestFood"

    def test_suggest_category_keine_regel(self, categorizer, setup_categorizer_rules, sample_konto):
        """Test: Keine Regel passt - None zurückgeben"""
        # Arrange
        with SessionLocal() as session:
            transaktion = Transaktion(
                konto_id=sample_konto.id,
                buchungstag=date(2026, 1, 20),
                beguenstigter="Unbekannt",
                verwendungszweck="Irgendwas",
                betrag=-10.00,
            )
            session.add(transaktion)
            session.commit()
            transaktion_id = transaktion.id

        # Act
        with SessionLocal() as session:
            transaktion = session.query(Transaktion).get(transaktion_id)
            kategorie = categorizer.suggest_category(transaktion)

        # Assert
        assert kategorie is None


class TestCategorizerAddKeyword:
    """Test-Suite für add_keyword_to_rule Methode"""

    def test_add_keyword_erfolg(self, categorizer, setup_categorizer_rules):
        """Test: Keyword erfolgreich hinzufügen"""
        # Act
        categorizer.add_keyword_to_rule("TestFood", ["newkeyword", "another"])

        # Assert
        with SessionLocal() as session:
            rule = (
                session.query(CategoryRules)
                .filter_by(category_name="TestFood")
                .first()
            )
            assert "newkeyword" in rule.keywords.lower()
            assert "another" in rule.keywords.lower()
