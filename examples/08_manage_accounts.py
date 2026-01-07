#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Beispiel-Script zum Erstellen und Verwalten von Konten
"""

import sys
from pathlib import Path

# Füge das Parent-Verzeichnis (Projekt-Root) zu sys.path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionLocal, init_db, KontoManager, Konto


def main():
    """Hauptprogramm"""

    # Datenbank initialisieren
    init_db()
    session = SessionLocal()

    try:
        print("\n" + "=" * 60)
        print("📊 KONTO-VERWALTUNG BEISPIEL")
        print("=" * 60 + "\n")

        # Beispiel 1: Neues Konto erstellen
        print("1️⃣  Erstelle Girokonto...")
        girokonto = KontoManager.erstelle_konto(
            session=session,
            kontoname="Hauptkonto",
            kontonummer="DE89370400440532013000",
            kontotyp="Girokonto",
            bankname="Sparkasse München",
            kontostand=5000.00,
            waehrung="EUR",
            bic="SOLADEST",
        )
        print(f"   ✓ Konto erstellt: {girokonto}\n")

        # Beispiel 2: Sparkonto erstellen
        print("2️⃣  Erstelle Sparkonto...")
        sparkonto = KontoManager.erstelle_konto(
            session=session,
            kontoname="Ersparnisse",
            kontonummer="DE91100000000123456789",
            kontotyp="Sparkonto",
            bankname="Commerzbank",
            kontostand=25000.00,
            waehrung="EUR",
            bic="COBADEFF",
        )
        print(f"   ✓ Konto erstellt: {sparkonto}\n")

        # Beispiel 3: Kreditkarte erstellen
        print("3️⃣  Erstelle Kreditkarte...")
        kreditkarte = KontoManager.erstelle_konto(
            session=session,
            kontoname="Visa Kreditkarte",
            kontonummer="DE75512108001234567890",
            kontotyp="Kreditkarte",
            bankname="Visa Bank",
            kontostand=0.00,
            waehrung="EUR",
        )
        print(f"   ✓ Konto erstellt: {kreditkarte}\n")

        # Beispiel 4: Alle Konten abrufen
        print("4️⃣  Hole alle Konten...")
        alle_konten = KontoManager.hole_alle_konten(session)
        print(f"   Insgesamt {len(alle_konten)} Konten vorhanden:\n")
        for konto in alle_konten:
            print(
                f"   • {konto.kontoname:20} | Typ: {konto.kontotyp:15} | Kontostand: {konto.kontostand:10.2f}€ | {konto.iban}"
            )
        print()

        # Beispiel 5: Kontostand aktualisieren
        print("5️⃣  Aktualisiere Kontostand des Girokontos...")
        KontoManager.erhöhe_kontostand(session, girokonto.id, 500.50)
        aktualisiert = KontoManager.hole_konto(session, girokonto.id)
        print(f"   ✓ Neuer Kontostand: {aktualisiert.kontostand:.2f}€\n")

        # Beispiel 6: Konto nach IBAN suchen und aktualisieren
        print("6️⃣  Suche Sparkonto nach IBAN und erhöhe Kontostand...")
        konto_by_iban = KontoManager.hole_konto_by_iban(
            session, "DE91100000000123456789"
        )
        if konto_by_iban:
            KontoManager.erhöhe_kontostand_by_iban(
                session, "DE91100000000123456789", -100.00
            )
            print(f"   ✓ Neuer Kontostand: {konto_by_iban.kontostand:.2f}€\n")

        # Beispiel 7: Kontoinformationen aktualisieren
        print("7️⃣  Aktualisiere Kontoinformationen der Kreditkarte...")
        KontoManager.aktualisiere_kontoinformationen(
            session, kreditkarte.id, bankname="Mastercard GmbH", kontotyp="Mastercard"
        )
        aktualisiert = KontoManager.hole_konto(session, kreditkarte.id)
        print(f"   ✓ Bank: {aktualisiert.bankname}, Typ: {aktualisiert.kontotyp}\n")

        # Zusammenfassung
        print("=" * 60)
        print("✓ ZUSAMMENFASSUNG")
        print("=" * 60)
        konten = KontoManager.hole_alle_konten(session)
        gesamt = sum(k.kontostand for k in konten)
        print(f"Anzahl Konten: {len(konten)}")
        print(f"Gesamtvermögen: {gesamt:.2f}€\n")

    except Exception as e:
        print(f"\n❌ Fehler: {e}\n")
    finally:
        session.close()


if __name__ == "__main__":
    main()
