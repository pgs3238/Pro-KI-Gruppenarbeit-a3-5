"""
Basis-Konfiguration für Tests mit Fixtures und Hilfsfunktionen
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.database.models import Base, Konto, Transaktion, Category
from datetime import date


@pytest.fixture(scope="function")
def test_engine():
    """Erstellt eine In-Memory SQLite Datenbank für Tests"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Erstellt eine neue Session für jeden Test"""
    TestSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = TestSessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_konto(test_session):
    """Erstellt ein Beispiel-Konto für Tests"""
    konto = Konto(
        kontoname="Test Girokonto",
        kontonummer="DE89370400440532013000",
        iban="DE89370400440532013000",
        kontotyp="Girokonto",
        bankname="Test Bank",
        kontostand=1000.0,
        waehrung="EUR",
        bic="COBADEFFXXX",
    )
    test_session.add(konto)
    test_session.commit()
    test_session.refresh(konto)
    return konto


@pytest.fixture
def sample_category(test_session):
    """Erstellt eine Beispiel-Kategorie für Tests"""
    category = Category(
        name="Lebensmittel",
        category_type="Ausgabe",
        icon="🛒",
        farbe="#FF5733",
    )
    test_session.add(category)
    test_session.commit()
    test_session.refresh(category)
    return category


@pytest.fixture
def sample_transaktion(test_session, sample_konto, sample_category):
    """Erstellt eine Beispiel-Transaktion für Tests"""
    transaktion = Transaktion(
        konto_id=sample_konto.id,
        kategorie_id=sample_category.id,
        buchungstag=date(2026, 1, 15),
        beguenstigter="Supermarkt XYZ",
        verwendungszweck="Wocheneinkauf",
        betrag=-50.0,
        waehrung="EUR",
    )
    test_session.add(transaktion)
    test_session.commit()
    test_session.refresh(transaktion)
    return transaktion
