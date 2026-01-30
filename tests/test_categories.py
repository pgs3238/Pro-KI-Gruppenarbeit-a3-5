"""
Unit Tests für das Categories-Modul (Kategorieverwaltung)

Hinweis: Die Funktionen in categories.py verwenden intern SessionLocal()
und arbeiten mit ValueErrors statt Return-Werten
"""

import pytest
from sqlalchemy.orm import Session
from src.database.models import Category, CategoryRules, Transaktion
from src.categories.categories import (
    add_category,
    remove_category,
    get_categories,
    assign_category_to_transaction,
)
from src.database import SessionLocal
from datetime import date


@pytest.fixture(autouse=True)
def cleanup_test_categories():
    """Auto-cleanup: Lösche Test-Kategorien vor jedem Test"""
    test_names = ["Shopping", "Duplicate", "Minimal", "Bonus", "GetKat1", "GetKat2", "GetKat3", 
                  "AssignTest", "OldCat", "NewCat", "ToDelete", "WithRules"]
    with SessionLocal() as session:
        for name in test_names:
            try:
                session.query(CategoryRules).filter_by(category_name=name).delete()
                session.query(Category).filter_by(name=name).delete()
            except:
                pass
        session.commit()
    yield
    # Cleanup nach Test
    with SessionLocal() as session:
        for name in test_names:
            try:
                session.query(CategoryRules).filter_by(category_name=name).delete()
                session.query(Category).filter_by(name=name).delete()
            except:
                pass
        session.commit()


class TestAddCategory:
    """Test-Suite für add_category Funktion"""

    def test_add_category_erfolg(self):
        """Test: Neue Kategorie erfolgreich hinzufügen"""
        # Act
        add_category(
            name="Shopping",
            category_type="Ausgabe",
            icon="🛍️",
            farbe="#FF5733",
        )

        # Assert
        with SessionLocal() as session:
            kategorie = session.query(Category).filter_by(name="Shopping").first()
            assert kategorie is not None
            assert kategorie.name == "Shopping"
            assert kategorie.category_type == "Ausgabe"
            assert kategorie.icon == "🛍️"
            assert kategorie.farbe == "#FF5733"

    def test_add_category_duplicate_name(self):
        """Test: Doppelter Name wird abgelehnt"""
        # Arrange
        add_category(name="Duplicate", category_type="Ausgabe")

        # Act & Assert
        with pytest.raises(ValueError, match="existiert bereits"):
            add_category(name="Duplicate", category_type="Ausgabe")

    def test_add_category_minimal(self):
        """Test: Kategorie mit minimalen Angaben"""
        # Act
        add_category(name="Minimal", category_type="Ausgabe")

        # Assert
        with SessionLocal() as session:
            kategorie = session.query(Category).filter_by(name="Minimal").first()
            assert kategorie is not None
            assert kategorie.icon == "🏷️"  # Default icon

    def test_add_category_einnahme(self):
        """Test: Einnahme-Kategorie hinzufügen"""
        # Act
        add_category(name="Bonus", category_type="Einnahme", icon="💰")

        # Assert
        with SessionLocal() as session:
            kategorie = session.query(Category).filter_by(name="Bonus").first()
            assert kategorie.category_type == "Einnahme"


class TestRemoveCategory:
    """Test-Suite für remove_category Funktion"""

    def test_remove_category_erfolg(self):
        """Test: Kategorie erfolgreich löschen"""
        # Arrange
        add_category(name="ToDelete", category_type="Ausgabe")

        # Act
        remove_category(name="ToDelete")

        # Assert
        with SessionLocal() as session:
            kategorie = session.query(Category).filter_by(name="ToDelete").first()
            assert kategorie is None

    def test_remove_category_nicht_gefunden(self):
        """Test: Nicht existierende Kategorie löschen"""
        # Act & Assert
        with pytest.raises(ValueError, match="nicht gefunden"):
            remove_category(name="NICHT_EXISTENT")

    def test_remove_category_mit_regeln(self):
        """Test: Kategorie mit Regeln wird gelöscht (inkl. Regeln)"""
        # Arrange: Kategorie und Regel erstellen
        add_category(name="WithRules", category_type="Ausgabe")
        
        with SessionLocal() as session:
            rule = CategoryRules(category_name="WithRules", keywords="test,keywords")
            session.add(rule)
            session.commit()

        # Act
        remove_category(name="WithRules")

        # Assert
        with SessionLocal() as session:
            # Kategorie gelöscht
            kategorie = session.query(Category).filter_by(name="WithRules").first()
            assert kategorie is None
            # Regeln auch gelöscht
            regeln = (
                session.query(CategoryRules)
                .filter_by(category_name="WithRules")
                .all()
            )
            assert len(regeln) == 0


class TestGetCategories:
    """Test-Suite für get_categories Funktion"""

    def test_get_all_categories(self):
        """Test: Alle Kategorien abrufen"""
        # Arrange: Kategorien hinzufügen
        add_category(name="GetKat1", category_type="Ausgabe")
        add_category(name="GetKat2", category_type="Einnahme")
        add_category(name="GetKat3", category_type="Ausgabe")

        # Act
        result = get_categories()

        # Assert
        assert len(result) >= 3
        names = [k.name for k in result]
        assert "GetKat1" in names
        assert "GetKat2" in names
        assert "GetKat3" in names


class TestAssignCategoryToTransaction:
    """Test-Suite für assign_category_to_transaction Funktion"""

    def test_assign_category_erfolg(self, sample_konto):
        """Test: Kategorie erfolgreich zuweisen"""
        # Arrange
        add_category(name="AssignTest", category_type="Ausgabe")
        
        transaktion_id = None
        with SessionLocal() as session:
            transaktion = Transaktion(
                konto_id=sample_konto.id,
                buchungstag=date(2026, 1, 15),
                beguenstigter="Test",
                betrag=-50.0,
            )
            session.add(transaktion)
            session.commit()
            transaktion_id = transaktion.id

        # Act - Lade Transaktion frisch in der Funktion
        with SessionLocal() as session:
            transaktion = session.query(Transaktion).get(transaktion_id)
            session.expunge(transaktion)  # Entferne aus dieser Session
            assign_category_to_transaction(
                transaktion, category_name="AssignTest"
            )
        
        # Assert
        with SessionLocal() as session:
            transaktion = session.query(Transaktion).get(transaktion_id)
            kategorie = session.query(Category).filter_by(name="AssignTest").first()
            assert transaktion.kategorie_id == kategorie.id

    def test_assign_category_kategorie_nicht_gefunden(self, sample_konto):
        """Test: Kategorie nicht gefunden"""
        # Arrange
        with SessionLocal() as session:
            transaktion = Transaktion(
                konto_id=sample_konto.id,
                buchungstag=date(2026, 1, 15),
                beguenstigter="Test",
                betrag=-50.0,
            )
            session.add(transaktion)
            session.commit()
            transaktion_id = transaktion.id

        # Act & Assert
        with SessionLocal() as session:
            transaktion = session.query(Transaktion).get(transaktion_id)
            with pytest.raises(ValueError, match="nicht gefunden"):
                assign_category_to_transaction(transaktion, category_name="NICHT_EXISTENT")

    def test_assign_category_update_existing(self, sample_konto):
        """Test: Bestehende Kategorie überschreiben"""
        # Arrange
        add_category(name="OldCat", category_type="Ausgabe")
        add_category(name="NewCat", category_type="Ausgabe")
        
        transaktion_id = None
        with SessionLocal() as session:
            old_cat = session.query(Category).filter_by(name="OldCat").first()
            transaktion = Transaktion(
                konto_id=sample_konto.id,
                kategorie_id=old_cat.id,
                buchungstag=date(2026, 1, 15),
                beguenstigter="Test",
                betrag=-50.0,
            )
            session.add(transaktion)
            session.commit()
            transaktion_id = transaktion.id

        # Act
        with SessionLocal() as session:
            transaktion = session.query(Transaktion).get(transaktion_id)
            session.expunge(transaktion)  # Entferne aus Session
            assign_category_to_transaction(transaktion, category_name="NewCat")

        # Assert
        with SessionLocal() as session:
            transaktion = session.query(Transaktion).get(transaktion_id)
            new_cat = session.query(Category).filter_by(name="NewCat").first()
            assert transaktion.kategorie_id == new_cat.id
