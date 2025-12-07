from pathlib import Path
import sys
from sqlalchemy import Column, Integer, String


base_path = Path(__file__).parent.parent.parent
sys.path.append(str(base_path))  # Removed for proper package structure
from local_test.db_handler import SessionLocal, Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    category_type = Column(String, nullable=False)

    def __repr__(self):
        return f"<Category(name='{self.name}', category_type='{self.category_type}')>"


class CategoryManager:
    _instance = None

    def __init__(self):
        with SessionLocal() as session:
            Category.__table__.create(bind=session.bind, checkfirst=True)
        self._check_and_load_defaults()

    @classmethod
    def initialize(cls):
        if cls._instance is None:
            cls._instance = CategoryManager()
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise Exception(
                "CategoryManager ist nicht initialisiert. Rufe 'initialize' zuerst auf."
            )
        return cls._instance

    def _check_and_load_defaults(self):
        with SessionLocal() as session:
            category_count = session.query(Category).count()
            if category_count == 0:
                default_categories = [
                    Category(name="Lebensmittel", category_type="Ausgabe"),
                    Category(name="Miete", category_type="Ausgabe"),
                    Category(name="Gehalt", category_type="Einnahme"),
                    Category(name="Freizeit", category_type="Ausgabe"),
                ]
                session.add_all(default_categories)
                session.commit()

    def add_category(self, name: str, category_type: str):
        with SessionLocal() as session:
            existing = session.query(Category).filter_by(name=name).first()
            if existing:
                raise ValueError(f"Category with name '{name}' already exists")
            new_category = Category(name=name, category_type=category_type)
            session.add(new_category)
            session.commit()

    def remove_category(self, id: int = None, name: str = None):
        with SessionLocal() as session:
            query = session.query(Category)
            if id is not None:
                query = query.filter_by(id=id)
            elif name is not None:
                query = query.filter_by(name=name)
            else:
                raise ValueError("Either 'id' or 'name' must be provided")
            category = query.first()
            if category:
                session.delete(category)
                session.commit()
            else:
                raise ValueError("Category not found")

    def get_categories(self):
        with SessionLocal() as session:
            categories = session.query(Category).all()
            session.expunge_all()
            return categories
