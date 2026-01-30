# Konto-Verwaltungsfunktionen für die Datenbank

from sqlalchemy.orm import Session
from typing import List, Optional
from .models import Konto, Transaktion
from datetime import datetime
from sqlalchemy import func


class KontoManager:
    @staticmethod
    # erstelle_konto - Legt ein neues Konto an und speichert es in der Datenbank.
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
    # hole_konto - Lädt ein Konto anhand der ID aus der Datenbank.
    def hole_konto(session: Session, konto_id: int) -> Optional[Konto]:
        return session.query(Konto).filter(Konto.id == konto_id).first()

    @staticmethod
    # hole_konto_by_iban - Sucht ein Konto anhand der IBAN.
    def hole_konto_by_iban(session: Session, iban: str) -> Optional[Konto]:
        return session.query(Konto).filter(Konto.iban == iban).first()

    @staticmethod
    # hole_alle_konten - Gibt eine Liste aller Konten zurück.
    def hole_alle_konten(session: Session) -> List[Konto]:
        return session.query(Konto).all()

    @staticmethod
    # aktualisiere_kontostand - Setzt den Kontostand eines Kontos auf einen festen Wert.
    def aktualisiere_kontostand(session: Session, konto_id: int, neuer_kontostand: float) -> Konto:
        konto = KontoManager.hole_konto(session, konto_id)
        if konto:
            konto.kontostand = neuer_kontostand
            konto.aktualisiert_am = datetime.now()
            session.commit()
            session.refresh(konto)
        return konto

    @staticmethod
    # aktualisiere_kontostand_by_iban - Setzt den Kontostand anhand der IBAN.
    def aktualisiere_kontostand_by_iban(session: Session, iban: str, neuer_kontostand: float) -> Optional[Konto]:
        konto = KontoManager.hole_konto_by_iban(session, iban)
        if konto:
            konto.kontostand = neuer_kontostand
            konto.aktualisiert_am = datetime.now()
            session.commit()
            session.refresh(konto)
        return konto

    @staticmethod
    # erhöhe_kontostand - Addiert einen Betrag zum aktuellen Kontostand (für Transaktionen).
    def erhöhe_kontostand(session: Session, konto_id: int, betrag: float) -> Optional[Konto]:
        konto = KontoManager.hole_konto(session, konto_id)
        if konto:
            konto.kontostand += betrag
            konto.aktualisiert_am = datetime.now()
            session.commit()
            session.refresh(konto)
        return konto

    @staticmethod
    # erhöhe_kontostand_by_iban - Erhöht den Kontostand anhand der IBAN (für Transaktionen).
    def erhöhe_kontostand_by_iban(session: Session, iban: str, betrag: float) -> Optional[Konto]:
        konto = KontoManager.hole_konto_by_iban(session, iban)
        if konto:
            konto.kontostand += betrag
            konto.aktualisiert_am = datetime.now()
            session.commit()
            session.refresh(konto)
        return konto

    @staticmethod
    # lösche_konto - Entfernt Konto und alle zugehörigen Transaktionen.
    def lösche_konto(session: Session, konto_id: int) -> bool:
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
    # aktualisiere_kontoinformationen - Ändert Stammdaten eines Kontos (Name, Typ, etc.).
    def aktualisiere_kontoinformationen(session: Session, konto_id: int, **kwargs) -> Optional[Konto]:
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
    # berechne_kontostand_aus_transaktionen - Summiert alle Transaktionen eines Kontos für Neuberechnung bei Fehlern.
    def berechne_kontostand_aus_transaktionen(session: Session, konto_id: int, initialstand: float = 0.0) -> float:
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
    # aktualisiere_kontostand_aus_transaktionen - Berechnet und setzt Kontostand basierend auf Transaktionshistorie.
    def aktualisiere_kontostand_aus_transaktionen(session: Session, konto_id: int, initialstand: float = 0.0) -> Optional[Konto]:
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

