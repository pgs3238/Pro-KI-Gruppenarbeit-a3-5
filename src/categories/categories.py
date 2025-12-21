from src.database import SessionLocal, Category


class CategoryManager:
    """
    Manager-Klasse für Kategorien.
    Implementiert das Singleton-Pattern, um sicherzustellen, dass nur eine Instanz existiert.
    Verwaltet Ausgabe- und Einnahmekategorien für Transaktionen.
    """

    # Singleton-Instanz
    _instance = None
    # Flag, ob die Initialisierung bereits durchgeführt wurde
    _initialized = False

    def __new__(cls):
        """Singleton-Pattern: Erstellt nur eine einzige Instanz der Klasse."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialisiert den CategoryManager und lädt Standard-Kategorien, falls die Datenbank leer ist."""
        if not self.__class__._initialized:
            # Prüfe und lade Standard-Kategorien beim ersten Initialisieren
            self._check_and_load_defaults()
            self.__class__._initialized = True

    @classmethod
    def initialize(cls):
        """
        Initialisiert den CategoryManager und gibt die Instanz zurück.
        """
        if cls._instance is None:
            cls._instance = CategoryManager()
        return cls._instance

    @classmethod
    def get_instance(cls):
        """
        Gibt die Singleton-Instanz zurück.
        Wirft eine Exception, wenn der Manager noch nicht initialisiert wurde.
        """
        if cls._instance is None:
            raise Exception(
                "CategoryManager ist nicht initialisiert. Rufe 'initialize' zuerst auf."
            )
        return cls._instance

    def _check_and_load_defaults(self):
        """
        Prüft, ob die Datenbank leer ist und lädt Standard-Kategorien.
        """
        with SessionLocal() as session:
            category_count = session.query(Category).count()
            if category_count == 0:
                # Erstelle Standard-Kategorien, wenn die Datenbank leer ist
                default_categories = [
                    Category(name="Lebensmittel", category_type="Ausgabe"),
                    Category(name="Miete", category_type="Ausgabe"),
                    Category(name="Gehalt", category_type="Einnahme"),
                    Category(name="Freizeit", category_type="Ausgabe"),
                ]
                session.add_all(default_categories)
                session.commit()

    def add_category(self, name: str, category_type: str):
        """
        Fügt eine neue Kategorie hinzu.

        Args:
            name: Name der Kategorie (darf nicht leer sein)
            category_type: Typ der Kategorie ("Ausgabe" oder "Einnahme")

        Raises:
            ValueError: Wenn der Name leer ist oder die Kategorie bereits existiert
        """
        # Validierung: Name darf nicht leer sein
        if name is None or not str(name).strip():
            raise ValueError("Name der Kategorie darf nicht leer sein")
        with SessionLocal() as session:
            # Prüfe, ob eine Kategorie mit diesem Namen bereits existiert
            existing = session.query(Category).filter_by(name=name).first()
            if existing:
                raise ValueError(f"Kategorie mit dem Namen '{name}' existiert bereits")
            # Erstelle und speichere die neue Kategorie
            new_category = Category(name=name, category_type=category_type)
            session.add(new_category)
            session.commit()

    def remove_category(self, id: int = None, name: str = None):
        """
        Entfernt eine Kategorie aus der Datenbank.

        Args:
            id: Optional - ID der zu löschenden Kategorie
            name: Optional - Name der zu löschenden Kategorie

        Raises:
            ValueError: Wenn weder ID noch Name angegeben wurde oder die Kategorie nicht gefunden wurde
        """
        with SessionLocal() as session:
            query = session.query(Category)
            # Suche entweder nach ID oder Name
            if id is not None:
                query = query.filter_by(id=id)
            elif name is not None:
                query = query.filter_by(name=name)
            else:
                raise ValueError("Entweder 'id' oder 'name' muss angegeben werden")
            category = query.first()
            if category:
                # Kategorie gefunden - lösche sie
                session.delete(category)
                session.commit()
            else:
                raise ValueError("Kategorie nicht gefunden")

    def get_categories(self):
        """
        Gibt alle Kategorien aus der Datenbank zurück.

        Returns:
            Liste aller Category-Objekte
        """
        with SessionLocal() as session:
            categories = session.query(Category).all()
            # Entferne die Objekte aus der Session, damit sie außerhalb verwendbar sind
            session.expunge_all()
            return categories

    def assign_category_to_transaction(
        self,
        transaction,
        category: Category = None,
        category_id: int = None,
        category_name: str = None,
    ):
        """
        Weist einer Transaktion eine Kategorie zu.

        Args:
            transaction: Das Transaktionsobjekt, dem die Kategorie zugewiesen werden soll
            category: Optional - Category-Objekt direkt
            category_id: Optional - ID der Kategorie
            category_name: Optional - Name der Kategorie

        Raises:
            ValueError: Wenn keine Kategorie angegeben wurde oder die Kategorie nicht gefunden wurde
        """
        with SessionLocal() as session:
            # Kategorie finden oder verwenden
            if category is not None:
                # Category-Objekt wurde direkt übergeben
                found_category = category
            elif category_id is not None:
                found_category = (
                    session.query(Category).filter_by(id=category_id).first()
                )
            elif category_name is not None:
                found_category = (
                    session.query(Category).filter_by(name=category_name).first()
                )
            else:
                raise ValueError(
                    "Entweder 'category', 'category_id' oder 'category_name' muss angegeben werden"
                )

            if not found_category:
                raise ValueError("Kategorie nicht gefunden")

            # Transaktion zur Session hinzufügen und Kategorie zuweisen
            session.add(transaction)
            transaction.kategorie_id = found_category.id
            session.commit()
