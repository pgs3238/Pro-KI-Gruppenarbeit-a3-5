"""
Auto-Kategorisierungs-Service mit iterativem Lernzyklus.

Dieser Service kombiniert Kategorisierung und Lernen in einer Schleife:
1. Kategorisiere alle unkategorisierten Transaktionen
2. Zähle Keywords vor dem Lernen
3. Lerne neue Keywords aus kategorisierten Transaktionen
4. Zähle Keywords nach dem Lernen
5. Wenn neue Keywords gefunden wurden → wiederhole ab 1
6. Sonst → fertig
"""

from datetime import datetime
from typing import Optional

from src.database import SessionLocal, CategorizationState, CategoryRules, Transaktion
from src.categories.categorizer_rules import Categorizer


class AutoCategorizerService:
    """
    Service für automatische Kategorisierung mit iterativem Lernen.

    Features:
    - Kategorisiert nur unkategorisierte Transaktionen
    - Lernt automatisch neue Keywords
    - Wiederholt den Prozess bis keine neuen Keywords mehr gefunden werden
    - Aktualisiert SystemState nach jeder Ausführung
    """

    def __init__(self):
        self.categorizer = Categorizer()

    def _count_total_keywords(self) -> int:
        """
        Zählt die Gesamtanzahl aller Keywords über alle Kategorien.

        Returns:
            Anzahl der Keywords
        """
        with SessionLocal() as session:
            rules = session.query(CategoryRules).all()
            total_keywords = 0

            for rule in rules:
                keywords = [kw.strip() for kw in rule.keywords.split(",") if kw.strip()]
                total_keywords += len(keywords)

            return total_keywords

    def _get_uncategorized_count(self) -> int:
        """
        Zählt die Anzahl unkategorisierter Transaktionen.

        Returns:
            Anzahl der Transaktionen ohne Kategorie
        """
        with SessionLocal() as session:
            count = session.query(Transaktion).filter_by(kategorie_id=None).count()
            return count

    def run_full_categorization_cycle(
        self, max_iterations: Optional[int] = None, min_occurrences: int = 3
    ) -> dict:
        """
        Führt einen vollständigen Kategorisierungs- und Lernzyklus durch.

        Ablauf:
        1. Kategorisiere alle unkategorisierten Transaktionen
        2. Zähle aktuelle Keywords
        3. Lerne neue Keywords aus kategorisierten Transaktionen
        4. Zähle Keywords erneut
        5. Wenn sich Keyword-Anzahl geändert hat → wiederhole ab 1
        6. Sonst → beende Schleife

        Args:
            max_iterations: Maximale Anzahl von Durchläufen (None = unbegrenzt)
            min_occurrences: Minimale Häufigkeit für neues Keyword beim Lernen

        Returns:
            Dict mit Statistiken über den Durchlauf
        """

        iteration = 0
        total_categorized = 0
        stats = {
            "iterations": 0,
            "total_categorized": 0,
            "keywords_added": 0,
            "started_at": datetime.now(),
        }

        while True:
            iteration += 1

            # Sicherheitscheck: Maximale Iterationen
            if max_iterations is not None and iteration > max_iterations:
                break

            # Schritt 1: Wie viele unkategorisierte Transaktionen gibt es?
            uncategorized_count = self._get_uncategorized_count()

            if uncategorized_count == 0:
                break

            # Schritt 2: Kategorisiere alle unkategorisierten
            results = self.categorizer.categorize_all(overwrite=False)
            newly_categorized = sum(
                1 for _, category in results if category is not None
            )
            total_categorized += newly_categorized

            # Schritt 3: Zähle Keywords vor dem Lernen
            keywords_before = self._count_total_keywords()

            # Schritt 4: Lerne neue Keywords
            self.categorizer.learn_from_categorized_transactions(
                min_occurrences=min_occurrences
            )

            # Schritt 5: Zähle Keywords nach dem Lernen
            keywords_after = self._count_total_keywords()
            keywords_learned = keywords_after - keywords_before

            # Schritt 6: Entscheide ob weiter iteriert werden soll
            if keywords_learned == 0:
                break
            else:
                stats["keywords_added"] += keywords_learned

        # Aktualisiere CategorizationState
        self._update_categorization_state()

        # Finalisiere Statistiken
        stats["iterations"] = iteration
        stats["total_categorized"] = total_categorized
        stats["completed_at"] = datetime.now()
        stats["duration_seconds"] = (
            stats["completed_at"] - stats["started_at"]
        ).total_seconds()

        return stats

    def _update_categorization_state(self):
        """
        Aktualisiert den CategorizationState nach erfolgter Kategorisierung.
        Setzt den Counter auf 0 und updated den Zeitstempel.
        """
        with SessionLocal() as session:
            state = session.query(CategorizationState).filter_by(id=1).first()
            if state:
                state.has_new_transactions = 0
                state.last_categorization = datetime.now()
                session.commit()

    def increment_transaction_counter(self):
        """
        Erhöht den Transaction-Counter im CategorizationState um 1.
        Wird aufgerufen wenn eine neue Transaktion erstellt wird.
        """
        with SessionLocal() as session:
            state = session.query(CategorizationState).filter_by(id=1).first()
            if state:
                state.has_new_transactions += 1
                session.commit()

    def should_trigger_categorization(self, threshold: int = 5) -> bool:
        """
        Prüft ob die Auto-Kategorisierung getriggert werden soll.

        Args:
            threshold: Anzahl neuer Transaktionen ab der kategorisiert wird

        Returns:
            True wenn kategorisiert werden soll, sonst False
        """
        with SessionLocal() as session:
            state = session.query(CategorizationState).filter_by(id=1).first()
            if state and state.has_new_transactions >= threshold:
                return True
            return False

    def get_categorization_state(self) -> dict:
        """
        Gibt den aktuellen CategorizationState zurück.

        Returns:
            Dict mit CategorizationState-Informationen
        """
        with SessionLocal() as session:
            state = session.query(CategorizationState).filter_by(id=1).first()
            if state:
                return {
                    "has_new_transactions": state.has_new_transactions,
                    "last_categorization": state.last_categorization,
                    "updated_at": state.updated_at,
                }
            return {
                "has_new_transactions": 0,
                "last_categorization": None,
                "updated_at": None,
            }


# Globale Singleton-Instanz
_auto_categorizer_service = None


def get_auto_categorizer_service() -> AutoCategorizerService:
    """
    Gibt die globale AutoCategorizerService-Instanz zurück.
    Erstellt sie beim ersten Aufruf (Singleton-Pattern).

    Returns:
        AutoCategorizerService Instanz
    """
    global _auto_categorizer_service
    if _auto_categorizer_service is None:
        _auto_categorizer_service = AutoCategorizerService()
    return _auto_categorizer_service
