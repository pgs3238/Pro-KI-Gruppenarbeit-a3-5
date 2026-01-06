# Definition der Datenbankmodelle für die Anwendung

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    Enum,
    ForeignKey,
)  # Importiere notwendige SQLAlchemy Datentypen
from sqlalchemy.orm import (
    declarative_base,  # Basisklasse für ORM-Modelle
    relationship,  # Beziehung zwischen Tabellen
)
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
    kategorie_id = Column(
        Integer, ForeignKey("categories.id"), nullable=True
    )  # Fremdschlüssel zur Kategorie
    created_at = Column(DateTime, default=datetime.now)

    # Relationship: Gibt dir Zugriff auf das Category-Objekt
    # back_populates erstellt die bidirektionale Verbindung
    kategorie = relationship("Category", back_populates="transaktionen")

    def __repr__(self):
        return f"<Transaktion(id={self.id}, buchungstag={self.buchungstag}, beguenstigter='{self.beguenstigter}', betrag={self.betrag})>"


class Category(Base):  # Erbt von Base und repräsentiert die "categories" Tabelle
    """
    Kategorie-Modell für die Klassifizierung von Transaktionen.
    Jede Transaktion kann einer Kategorie zugeordnet werden (z.B. Lebensmittel, Miete, Gehalt).
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Eindeutige ID
    name = Column(
        String(100), nullable=False, unique=True
    )  # Kategoriename, muss eindeutig sein
    category_type = Column(  # Typ: entweder "Ausgabe" oder "Einnahme"
        Enum("Ausgabe", "Einnahme", name="category_type_enum", validate_strings=True),
        nullable=False,
    )

    # Relationship: Gibt dir Zugriff auf alle Transaktionen dieser Kategorie
    transaktionen = relationship("Transaktion", back_populates="kategorie")

    def __repr__(self):
        return f"<Category(name='{self.name}', category_type='{self.category_type}')>"


class CategoryRules(Base):
    """
    Kategorisierungsregeln für automatische Zuordnung von Transaktionen zu Kategorien basierend auf Schlüsselwörtern.
    Erweitert oder überschreibt Standard-Regeld aus dem Code.
    """

    __tablename__ = "category_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(100), ForeignKey("categories.name"), nullable=False)
    keywords = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Relationship
    category = relationship("Category", backref="rules")

    def __repr__(self):
        return f"<CategoryRules(category='{self.category.name}', keyword='{self.keyword}', source='{self.source}')>"
