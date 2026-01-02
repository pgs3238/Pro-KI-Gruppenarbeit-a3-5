"""
Automatische regelbasierte Kategorisierung von Transaktionen.

Dieses Modul stellt die Categorizer-Klasse bereit, die Transaktionen basierend
auf vordefinierten Regeln automatisch kategorisiert.
"""

from src.database import SessionLocal, Category, Transaktion, CategoryRules
from datetime import datetime, timedelta


class Categorizer:
    """
    Engine für automatische Kategorisierung von Transaktionen.

    Die Klasse verwendet regelbasierte Kategorisierung mit Keywords und Betragsbereichen.
    """

    def __init__(self):
        self._rules_cache = None
        self._cache_timestamp = None

    def _get_rules(self) -> dict:
        """
        Lädt alle Kategorisierungsregeln aus der Datenbank.
        Caching wird verwendet, um wiederholte Datenbankabfragen zu vermeiden.
        """
        # Cache leer oder abgelaufen
        if (
            self._rules_cache is None
            or self._cache_timestamp is None
            or datetime.now() - self._cache_timestamp > timedelta(minutes=5)
        ):
            with SessionLocal() as session:
                rules = session.query(CategoryRules).all()
                self._rules_cache = [
                    {
                        "category": session.query(Category)
                        .filter_by(name=rule.category_name)
                        .first(),
                        "keywords": rule.keywords,
                        "min_amount": rule.amount_range_min,
                        "max_amount": rule.amount_range_max,
                        "priority": rule.priority,
                        "source": rule.source,
                        "created_at": rule.created_at,
                    }
                    for rule in rules
                ]
                self._cache_timestamp = datetime.now()

        return self._rules_cache

    def _prepare_search_text(self, transaction: Transaktion) -> str:
        """
        Bereitet den Suchtext für die Regelanwendung vor.
        Kombiniert relevante Felder der Transaktion zu einem einzigen Suchtext.

        Args:
            transaction: Transaktion-Objekt
        """
        fields = [
            transaction.beguenstigter or "",
            transaction.verwendungszweck or "",
            transaction.iban_kontonummer or "",
            transaction.beschreibung or "",
        ]
        return " ".join(fields).lower()

    def _matches_rule(
        self, transaction: Transaktion, rule: dict, search_text: str
    ) -> bool:
        """
        Prüft ob eine Transaktion zu einer Regel passt.

        Args:
            transaction: Transaktion-Objekt
            rule: Regel-Dict mit keywords und betrag_range
            search_text: Vorbereiteter Suchtext (lowercase)

        Returns:
            True wenn die Transaktion zur Regel passt, sonst False
        """
        # Prüfe Keywords
        keywords = [kw.strip().lower() for kw in rule["keyword"].split(",")]
        if not any(kw in search_text for kw in keywords):
            return False

        # Prüfe Betragsbereich
        if rule["min_amount"] is not None and transaction.betrag < rule["min_amount"]:
            return False
        if rule["max_amount"] is not None and transaction.betrag > rule["max_amount"]:
            return False

        return True

    def suggest_category(self, transaction: Transaktion) -> Category | None:
        """
        Schlägt eine Kategorie für die gegebene Transaktion vor.

        Args:
            transaction: Transaktion-Objekt

        Returns:
            Vorgeschlagene Kategorie oder None wenn keine Regel passt
        """
        rules = self._get_rules()
        search_text = self._prepare_search_text(transaction)

        sorted_rules = sorted(
            rules.items(), key=lambda item: item[1]["priority"], reverse=True
        )

        for rule in sorted_rules:
            if self._matches_rule(transaction, rule, search_text):
                return rule["category"]
        return None

    def categorize_transactions(
        self, transactions: list[Transaktion]
    ) -> list[tuple[Transaktion, Category]]:
        """
        Kategorisiert eine Liste von Transaktionen automatisch.

        Args:
            transactions: Liste von Transaktion-Objekten

        Returns:
            Liste von Tupeln (Transaktion, ermittelte Kategorie)
        """
        results = []
        for transaction in transactions:
            category = self.suggest_category(transaction)
            results.append((transaction, category))

        with SessionLocal() as session:
            for transaction, category in results:
                if category:
                    # Lade die Transaktion erneut in der Session
                    txn = session.query(Transaktion).get(transaction.id)
                    txn.kategorie = category
            session.commit()

        return results

    def categorize_all(
        self, overwrite: bool = False
    ) -> list[tuple[Transaktion, Category]]:
        """
        Kategorisiert alle Transaktionen in der Datenbank automatisch.
        Args:
            overwrite: Ob bereits kategorisierte Transaktionen überschrieben werden sollen
        Returns:
            Liste von Tupeln (Transaktion, ermittelte Kategorie)
        """
        with SessionLocal() as session:
            if overwrite:
                transactions = session.query(Transaktion).all()
            else:
                transactions = (
                    session.query(Transaktion)
                    .filter(Transaktion.kategorie_id == None)
                    .all()
                )

        return self.categorize_transactions(transactions)
