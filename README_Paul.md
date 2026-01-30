## CSV Transaction Importer

Dieses Modul ermöglicht den Import von Banktransaktionen aus CSV-Dateien in Finly. Der Ablauf ist wie folgt:

**1. Dateiauswahl:** Es wird eine CSV-Datei ausgewählt.
**2. Header & Footer:** Die Headerzeile wird angegeben, und etwaige Footerzeilen können durch Angabe der Anzahl zu entfernender Zeilen ausgeschlossen werden.
**3. Feldzuordnung:** Die relevanten Felder – Buchungstag, Begünstigter, IBAN des Begünstigten, Verwendungszweck, Betrag und Konto – werden gesetzt und mit den Daten in der CSV abgeglichen.
**4. Datenbankübertragung:** Sobald alle Felder korrekt zugeordnet sind und die Daten validiert wurden, werden die Transaktionen in die Datenbank übertragen (unter Verwendung von SQLAlchemy).

## Transaction Search

Dieses Modul stellt eine flexible Suchfunktion für die in der Datenbank gespeicherten Transaktionen in Finly bereit.

- Transaktionen können dynamisch anhand mehrerer optionaler Kriterien gefiltert werden, darunter:
**Buchungstag**, **Begünstigter**, ***Verwendungszweck**, **IBAN/Kontonummer**, **Betrag** (inklusive absoluter Beträge) und **Konto**.
- Es werden nur die Filter angewendet, die tatsächlich angegeben sind.
- Die Ergebnisse werden standardmäßig nach Buchungstag absteigend sortiert.
- Das Modul unterstützt außerdem die Validierung von Betragsbereichen und behandelt europäische Darstellung von negativen/positiven Beträgen korrekt.