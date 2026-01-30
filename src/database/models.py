# Definition der Datenbankmodelle für die Anwendung

from sqlalchemy import (Column, Integer, String, Float, Date, DateTime, Enum, ForeignKey,)  # Importiere notwendige SQLAlchemy Datentypen
from sqlalchemy.orm import (declarative_base, relationship)  # Basisklasse für ORM-Modelle und Beziehung zwischen Tabellen
from datetime import datetime

Base = (declarative_base())  # Basisklasse für alle ORM-Modelle um Tabellen in der Datenbank zu repräsentieren

# Konto Model: Repräsentiert ein Bankkonto mit allen Stammdaten.
class Konto(Base):  # Erbt von Base und repräsentiert die "konten" Tabelle in der Datenbank

    __tablename__ = "konten"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kontoname = Column(String(100), nullable=False, unique=True)  # z.B. "Girokonto", "Sparkonto"
    kontonummer = Column(String(34), nullable=True)  # IBAN (optional)
    bankname = Column(String(200), nullable=True)  # z.B. "Sparkasse München"
    kontostand = Column(Float, nullable=False, default=0.0)  # Aktueller Kontostand
    waehrung = Column(String(3), default="EUR")  # Währung
    kontotyp = Column(
        String(50), nullable=False
    )  # z.B. "Girokonto", "Sparkonto", "Kreditkarte"
    iban = Column(String(34), nullable=True)  # IBAN für Transaktionen (optional)
    bic = Column(String(11), nullable=True)  # BIC/SWIFT Code
    farbe = Column(String(7), default="#06d6a6")  # Farbe für Darstellung (Hex-Code)
    erstellt_am = Column(DateTime, default=datetime.now)  # Erstellungsdatum
    aktualisiert_am = Column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )  # Aktualisierungsdatum

    # Relationship: Gibt dir Zugriff auf alle Transaktionen dieses Kontos
    transaktionen = relationship("Transaktion", back_populates="konto")

    def __repr__(self):
        return f"<Konto(id={self.id}, kontoname='{self.kontoname}', kontostand={self.kontostand}€, iban='{self.iban}')>"


# Transaktion Model: Einzelne Buchung (Einnahme/Ausgabe) mit Verknüpfung zu Konto und Kategorie.
class Transaktion(Base):  # Erbt von Base und repräsentiert die "transaktionen" Tabelle in der Datenbank

    __tablename__ = "transaktionen"

    id = Column(Integer, primary_key=True, autoincrement=True)
    konto_id = Column(
        Integer, ForeignKey("konten.id"), nullable=True
    )  # Fremdschlüssel zum Konto
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

    # Relationships: Gibt dir Zugriff auf das Konto und die Kategorie
    # back_populates erstellt die bidirektionale Verbindung
    konto = relationship("Konto", back_populates="transaktionen")
    kategorie = relationship("Category", back_populates="transaktionen")

    def __repr__(self):
        return f"<Transaktion(id={self.id}, buchungstag={self.buchungstag}, beguenstigter='{self.beguenstigter}', betrag={self.betrag})>"


# Category Model: Stammdaten für Kategorien (Name, Typ, Icon, Farbe).
class Category(Base):  # Erbt von Base und repräsentiert die "categories" Tabelle

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Eindeutige ID
    name = Column(
        String(100), nullable=False, unique=True
    )  # Kategoriename, muss eindeutig sein
    category_type = Column(  # Typ: entweder "Ausgabe" oder "Einnahme"
        Enum("Ausgabe", "Einnahme", name="category_type_enum", validate_strings=True),
        nullable=False,
    )
    icon = Column(String(10), nullable=True, default="🏷️")  # Icon für die Kategorie
    farbe = Column(String(7), nullable=True, default="#06d6a6")  # Farbe für die Darstellung

    # Relationship: Gibt dir Zugriff auf alle Transaktionen dieser Kategorie
    transaktionen = relationship("Transaktion", back_populates="kategorie")

    def __repr__(self):
        return f"<Category(name='{self.name}', category_type='{self.category_type}')>"


# CategoryRules Model: Speichert Keywords für die automatische Kategorisierung.
class CategoryRules(Base):

    __tablename__ = "category_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(100), ForeignKey("categories.name"), nullable=False)
    keywords = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Relationship
    category = relationship("Category", backref="rules")

    def __repr__(self):
        return f"<CategoryRules(category_name='{self.category_name}', keywords='{self.keywords}')>"


# CategorizationState Model: Singleton-Tabelle für Status der Auto-Kategorisierung (Performance-Optimierung).
class CategorizationState(Base):

    __tablename__ = "categorization_state"

    id = Column(Integer, primary_key=True, default=1)
    has_new_transactions = Column(
        Integer
    )  # Counter für neue Transaktionen seit letzter Kategorisierung
    last_categorization = Column(
        DateTime, nullable=True
    )  # Zeitstempel der letzten Kategorisierung
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )  # Letztes Update

    def __repr__(self):
        return f"<SystemState(has_new_transactions={self.has_new_transactions}, last_categorization={self.last_categorization})>"
