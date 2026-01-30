# Konto-Verwaltungsfunktionen für die Datenbank

from sqlalchemy.orm import Session
from typing import List, Optional
from .models import Konto, Transaktion
from datetime import datetime
from sqlalchemy import func


class KontoManager:
    """Manager-Klasse für Konto-Operationen"""

    @staticmethod
    def erstelle_konto(
        session: Session,
        kontoname: str,
        kontonummer: Optional[str] = None,
        kontotyp: str = "Girokonto",
        bankname: Optional[str] = None,
        kontostand: float = 0.0,
        waehrung: str = "EUR",
        bic: Optional[str] = None,
    ) -> Konto:
        """
        Erstellt ein neues Konto in der Datenbank

        Args:
            session: SQLAlchemy Session
            kontoname: Name des Kontos (z.B. "Hauptkonto", "Sparkonto")
            kontonummer: IBAN des Kontos (optional)
            kontotyp: Typ des Kontos (z.B. "Girokonto", "Sparkonto", "Kreditkarte")
            bankname: Name der Bank (optional)
            kontostand: Startkontostand (default: 0.0)
            waehrung: Währung (default: "EUR")
            bic: BIC/SWIFT Code (optional)

        Returns:
            Konto: Das erstellte Konto-Objekt
        """
        neues_konto = Konto(
            kontoname=kontoname,
            kontonummer=kontonummer,
            iban=kontonummer,  # IBAN ist gleich Kontonummer (kann None sein)
            kontotyp=kontotyp,
            bankname=bankname,
            kontostand=kontostand,
            waehrung=waehrung,
            bic=bic,
        )
        session.add(neues_konto)
        session.commit()
        session.refresh(neues_konto)
        return neues_konto

    @staticmethod
    def hole_konto(session: Session, konto_id: int) -> Optional[Konto]:
        """
        Holt ein Konto nach ID

        Args:
            session: SQLAlchemy Session
            konto_id: ID des Kontos

        Returns:
            Konto oder None
        """
        return session.query(Konto).filter(Konto.id == konto_id).first()

    @staticmethod
    def hole_konto_by_iban(session: Session, iban: str) -> Optional[Konto]:
        """
        Holt ein Konto nach IBAN

        Args:
            session: SQLAlchemy Session
            iban: IBAN des Kontos

        Returns:
            Konto oder None
        """
        return session.query(Konto).filter(Konto.iban == iban).first()

    @staticmethod
    def hole_alle_konten(session: Session) -> List[Konto]:
        """
        Holt alle Konten

        Args:
            session: SQLAlchemy Session

        Returns:
            Liste aller Konten
        """
        return session.query(Konto).all()

    @staticmethod
    def aktualisiere_kontostand(
        session: Session, konto_id: int, neuer_kontostand: float
    ) -> Konto:
        """
        Aktualisiert den Kontostand eines Kontos

        Args:
            session: SQLAlchemy Session
            konto_id: ID des Kontos
            neuer_kontostand: Neuer Kontostand

        Returns:
            Das aktualisierte Konto-Objekt
        """
        konto = KontoManager.hole_konto(session, konto_id)
        if konto:
            konto.kontostand = neuer_kontostand
            konto.aktualisiert_am = datetime.now()
            session.commit()
            session.refresh(konto)
        return konto

    @staticmethod
    def aktualisiere_kontostand_by_iban(
        session: Session, iban: str, neuer_kontostand: float
    ) -> Optional[Konto]:
        """
        Aktualisiert den Kontostand eines Kontos nach IBAN

        Args:
            session: SQLAlchemy Session
            iban: IBAN des Kontos
            neuer_kontostand: Neuer Kontostand

        Returns:
            Das aktualisierte Konto-Objekt oder None
        """
        konto = KontoManager.hole_konto_by_iban(session, iban)
        if konto:
            konto.kontostand = neuer_kontostand
            konto.aktualisiert_am = datetime.now()
            session.commit()
            session.refresh(konto)
        return konto

    @staticmethod
    def erhöhe_kontostand(
        session: Session, konto_id: int, betrag: float
    ) -> Optional[Konto]:
        """
        Erhöht den Kontostand um einen Betrag

        Args:
            session: SQLAlchemy Session
            konto_id: ID des Kontos
            betrag: Betrag (positiv oder negativ)

        Returns:
            Das aktualisierte Konto-Objekt
        """
        konto = KontoManager.hole_konto(session, konto_id)
        if konto:
            konto.kontostand += betrag
            konto.aktualisiert_am = datetime.now()
            session.commit()
            session.refresh(konto)
        return konto

    @staticmethod
    def erhöhe_kontostand_by_iban(
        session: Session, iban: str, betrag: float
    ) -> Optional[Konto]:
        """
        Erhöht den Kontostand eines Kontos um einen Betrag nach IBAN

        Args:
            session: SQLAlchemy Session
            iban: IBAN des Kontos
            betrag: Betrag (positiv oder negativ)

        Returns:
            Das aktualisierte Konto-Objekt
        """
        konto = KontoManager.hole_konto_by_iban(session, iban)
        if konto:
            konto.kontostand += betrag
            konto.aktualisiert_am = datetime.now()
            session.commit()
            session.refresh(konto)
        return konto

    @staticmethod
    def lösche_konto(session: Session, konto_id: int) -> bool:
        """
        Löscht ein Konto (mit allen zugehörigen Transaktionen)

        Args:
            session: SQLAlchemy Session
            konto_id: ID des Kontos

        Returns:
            True wenn erfolgreich, False wenn nicht gefunden
        """
        konto = KontoManager.hole_konto(session, konto_id)
        if konto:
            # Lösche zuerst alle Transaktionen dieses Kontos
            for transaktion in konto.transaktionen:
                session.delete(transaktion)
            # Dann lösche das Konto
            session.delete(konto)
            session.commit()
            return True
        return False

    @staticmethod
    def aktualisiere_kontoinformationen(
        session: Session, konto_id: int, **kwargs
    ) -> Optional[Konto]:
        """
        Aktualisiert Informationen eines Kontos

        Args:
            session: SQLAlchemy Session
            konto_id: ID des Kontos
            **kwargs: Felder die aktualisiert werden sollen
                     (kontoname, bankname, kontotyp, bic, etc.)

        Returns:
            Das aktualisierte Konto-Objekt
        """
        konto = KontoManager.hole_konto(session, konto_id)
        if konto:
            # Erlaubte Felder für Updates
            erlaubte_felder = {
                "kontoname",
                "bankname",
                "kontotyp",
                "bic",
                "waehrung",
            }

            for key, value in kwargs.items():
                if key in erlaubte_felder and value is not None:
                    setattr(konto, key, value)

            konto.aktualisiert_am = datetime.now()
            session.commit()
            session.refresh(konto)
        return konto

    @staticmethod
    def berechne_kontostand_aus_transaktionen(
        session: Session, konto_id: int, initialstand: float = 0.0
    ) -> float:
        """
        Berechnet den Kontostand aus allen zugehörigen Transaktionen

        Args:
            session: SQLAlchemy Session
            konto_id: ID des Kontos
            initialstand: Startkontostand (default: 0.0)

        Returns:
            float: Berechneter Kontostand (Initialstand + Summe aller Transaktionen)
        """
        # Summiere alle Beträge der Transaktionen für dieses Konto
        summe = (
            session.query(func.sum(Transaktion.betrag))
            .filter(Transaktion.konto_id == konto_id)
            .scalar()
        )
        
        # Wenn keine Transaktionen vorhanden, ist summe None
        transaktionssumme = summe if summe is not None else 0.0
        
        # Gesamtkontostand = Initialstand + Summe aller Transaktionen
        kontostand = initialstand + transaktionssumme
        return kontostand

    @staticmethod
    def aktualisiere_kontostand_aus_transaktionen(
        session: Session, konto_id: int, initialstand: float = 0.0
    ) -> Optional[Konto]:
        """
        Aktualisiert den Kontostand eines Kontos basierend auf allen zugehörigen Transaktionen

        Args:
            session: SQLAlchemy Session
            konto_id: ID des Kontos
            initialstand: Initialstand des Kontos vor Transaktionen (default: 0.0)

        Returns:
            Das aktualisierte Konto-Objekt oder None wenn nicht gefunden
        """
        konto = KontoManager.hole_konto(session, konto_id)
        if not konto:
            return None
        
        # Berechne neuen Kontostand
        neuer_stand = KontoManager.berechne_kontostand_aus_transaktionen(
            session, konto_id, initialstand
        )
        
        # Aktualisiere Kontostand
        konto.kontostand = neuer_stand
        konto.aktualisiert_am = datetime.now()
        session.commit()
        session.refresh(konto)
        return konto

