"""
Modul zur Verwaltung von Ausgabe- und Einnahmekategorien für Transaktionen.
Bietet Funktionen zum Hinzufügen, Entfernen und Abrufen von Kategorien.
"""

from src.database import SessionLocal, Category


# Flag, ob die Standard-Kategorien bereits geladen wurden
_defaults_loaded = False


def _check_and_load_defaults_categories():
    """
    Prüft, ob die Datenbank leer ist und lädt Standard-Kategorien.
    Wird automatisch beim ersten Modulimport aufgerufen.
    """
    global _defaults_loaded

    if _defaults_loaded:
        return

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

    _defaults_loaded = True


def add_category(name: str, category_type: str):
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


def remove_category(id: int = None, name: str = None):
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


def get_categories():
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
            found_category = session.query(Category).filter_by(id=category_id).first()
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
