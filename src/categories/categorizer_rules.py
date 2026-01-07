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

    Die Klasse verwendet regelbasierte Kategorisierung durch Keywords.
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
                self._rules_cache = {}
                for rule in rules:
                    self._rules_cache[rule.category_name] = {
                        "category": session.query(Category)
                        .filter_by(name=rule.category_name)
                        .first(),
                        "keywords": rule.keywords,
                        "created_at": rule.created_at,
                    }

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
        keywords = [self._clean_keyword(kw) for kw in rule["keywords"].split(",")]
        if not any(kw in search_text for kw in keywords):
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

        for rule in rules.values():
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
                    session.query(Transaktion).filter_by(kategorie_id=None).all()
                )

        return self.categorize_transactions(transactions)

    def add_keyword_to_rule(self, category_name: str, new_keywords: list[str]):
        """
        Fügt ein neues Schlüsselwort zu einer bestehenden Kategorisierungsregel hinzu.

        Args:
            category_name: Name der Kategorie, zu der die Regel gehört
            new_keywords: Liste von neuen Schlüsselwörtern, die hinzugefügt werden sollen
        """
        with SessionLocal() as session:
            rule = (
                session.query(CategoryRules)
                .filter_by(category_name=category_name)
                .first()
            )
            if rule:
                existing_keywords = [
                    kw.strip() for kw in rule.keywords.split(",") if kw.strip()
                ]
                for new_keyword in new_keywords:
                    new_keyword = self._clean_keyword(new_keyword)
                    if new_keyword not in existing_keywords:
                        existing_keywords.append(new_keyword)
                rule.keywords = ", ".join(existing_keywords)
                session.commit()
                self.invalidate_cache()

    def remove_keyword_from_rule(self, category_name: str, keyword_to_remove: str):
        """
        Entfernt ein Schlüsselwort aus einer bestehenden Kategorisierungsregel.

        Args:
            category_name: Name der Kategorie, zu der die Regel gehört
            keyword_to_remove: Das zu entfernende Schlüsselwort
        """
        with SessionLocal() as session:
            rule = (
                session.query(CategoryRules)
                .filter_by(category_name=category_name)
                .first()
            )
            if rule:
                existing_keywords = [
                    kw.strip() for kw in rule.keywords.split(",") if kw.strip()
                ]
                if keyword_to_remove in existing_keywords:
                    existing_keywords.remove(keyword_to_remove)
                    rule.keywords = ", ".join(existing_keywords)
                    session.commit()
                    self.invalidate_cache()

    def add_rule(
        self,
        category_name: str,
        keywords: str,
    ):
        """
        Fügt eine neue Kategorisierungsregel hinzu.

        Args:
            category_name: Name der Kategorie, zu der die Regel gehört
            keywords: Kommagetrennte Schlüsselwörter für die Regel
        """
        with SessionLocal() as session:
            new_rule = CategoryRules(
                category_name=category_name,
                keywords=keywords,
            )
            session.add(new_rule)
            session.commit()
            self.invalidate_cache()

    def remove_rule(self, category_name: str):
        """
        Entfernt eine Kategorisierungsregel basierend auf dem Kategorienamen.

        Args:
            category_name: Name der Kategorie, zu der die Regel gehört
        """
        with SessionLocal() as session:
            rule = (
                session.query(CategoryRules)
                .filter_by(category_name=category_name)
                .first()
            )
            if rule:
                session.delete(rule)
                session.commit()
                self.invalidate_cache()

    def invalidate_cache(self):
        self._rules_cache = None
        self._cache_timestamp = None

    def learn_from_categorized_transactions(self, min_occurrences: int = 3):
        """
        Lernt neue Kategorisierungsregeln basierend auf bereits kategorisierten Transaktionen.
        Berücksichtigt nur Keywords, die eindeutig einer Kategorie zugeordnet werden können.

        Args:
            min_occurrences: Minimale Anzahl von Vorkommen eines Schlüsselworts, um eine Regel zu erstellen
        """

        STOPWORDS = {
            "vielen",
            "dank",
            "mfg",
            "mit",
            "freundlichen",
            "grüßen",
            "der",
            "die",
            "das",
            "und",
            "für",
            "von",
            "zu",
            "den",
            "ich",
            "sie",
            "wir",
            "bei",
            "auf",
            "im",
            "am",
            "an",
            "bitte",
            "danke",
            "freundliche",
            "",
        }

        rules = self._get_rules()

        with SessionLocal() as session:
            categorized_transactions = (
                session.query(Transaktion)
                .filter(Transaktion.kategorie_id is not None)
                .all()
            )

            keyword_categories = {}

            for transaction in categorized_transactions:
                if transaction.kategorie is None:
                    continue

                search_text = self._prepare_search_text(transaction)
                keywords = set(search_text.split())
                category_name = transaction.kategorie.name
                existing_keywords = rules.get(category_name, {}).get("keywords", "")

                for kw in keywords:
                    kw = self._clean_keyword(kw)
                    if (
                        kw.lower() in STOPWORDS
                        or len(kw) < 3
                        or kw in existing_keywords
                    ):
                        continue

                    if kw not in keyword_categories:
                        keyword_categories[kw] = {}

                    keyword_categories[kw][category_name] = (
                        keyword_categories[kw].get(category_name, 0) + 1
                    )

            category_keywords = {}

            for kw, categories in keyword_categories.items():
                if len(categories) == 1:
                    category = list(categories.keys())[0]
                    count = categories[category]

                    if count >= min_occurrences:
                        if category not in category_keywords:
                            category_keywords[category] = []
                        category_keywords[category].append(kw)

            for category_name, keywords_to_add in category_keywords.items():
                if keywords_to_add:
                    self.add_keyword_to_rule(category_name, keywords_to_add)

    def _clean_keyword(self, keyword: str) -> str:
        """
        Bereinigt ein einzelnes Keyword von Leerzeichen und Satzzeichen.

        Args:
            keyword: Das zu bereinigende Keyword

        Returns:
            Bereinigtes Keyword in Kleinbuchstaben
        """
        import string

        # Entferne Leerzeichen und Satzzeichen am Anfang und Ende
        cleaned = keyword.strip()
        cleaned = cleaned.strip(string.punctuation + string.whitespace)

        # Ersetze mehrfache Leerzeichen durch ein einzelnes
        cleaned = " ".join(cleaned.split())

        # Konvertiere zu Kleinbuchstaben
        cleaned = cleaned.lower()

        return cleaned
