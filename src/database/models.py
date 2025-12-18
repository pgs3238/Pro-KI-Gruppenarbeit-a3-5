# Definiotn der Datenbankmodelle für die Anwendung

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
)  # Importiere notwendige SQLAlchemy Datentypen
from sqlalchemy.orm import declarative_base  # Basisklasse für ORM-Modelle
from datetime import datetime

Base = (
    declarative_base()
)  # Basisklasse für alle ORM-Modelle um Tabellen in der Datenbank zu repräsentieren


class Transaktion(
    Base
):  # Erbt von Base und repräsentiert die "transaktionen" Tabelle in der Datenbank
    """Transaktion für Einnahmen und Ausgaben"""

    __tablename__ = "transaktionen"

    id = Column(Integer, primary_key=True, autoincrement=True)
    buchungstag = Column(Date, nullable=False)
    beguenstigter = Column(String(200), nullable=True)
    verwendungszweck = Column(String(500))
    iban_kontonummer = Column(String(34))
    betrag = Column(Float, nullable=False)
    waehrung = Column(String(3), default="EUR")
    beschreibung = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Transaktion(id={self.id}, buchungstag={self.buchungstag}, beguenstigter='{self.beguenstigter}', betrag={self.betrag})>"


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    category_type = Column(String, nullable=False)

    def __repr__(self):
        return f"<Category(name='{self.name}', category_type='{self.category_type}')>"
