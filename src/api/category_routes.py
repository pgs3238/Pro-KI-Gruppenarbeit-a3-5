"""
API-Endpoints für Kategorie-Verwaltung
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import SessionLocal, Category, CategoryRules
from ..categories.categories import add_category, remove_category, get_categories
from ..categories.categorizer_rules import Categorizer
from .dependencies import get_db
from .schemas import CategoryCreate, CategoryResponse, CategoryRulesResponse, KeywordRequest

router = APIRouter(prefix="/categories", tags=["categories"])


# ==================== ENDPOINTS ====================

@router.get("", response_model=List[CategoryResponse])
def get_categories_endpoint(db: Session = Depends(get_db)):
    """
    Gibt alle Kategorien aus der Datenbank zurück.
    Nutzt die get_categories() Funktion aus dem categories Modul.
    """
    try:
        categories = get_categories()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Kategorien: {str(e)}")


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """
    Erstellt eine neue Kategorie.
    Nutzt die add_category() Funktion aus dem categories Modul.
    """
    try:
        # Validiere category_type
        if category.category_type not in ["Ausgabe", "Einnahme"]:
            raise HTTPException(status_code=400, detail="category_type muss 'Ausgabe' oder 'Einnahme' sein")

        # Nutze die add_category Funktion mit icon und farbe
        add_category(
            name=category.name, 
            category_type=category.category_type,
            icon=category.icon,
            farbe=category.farbe
        )
        
        # Lade die neu erstellte Kategorie
        new_category = db.query(Category).filter(Category.name == category.name).first()
        return new_category

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen der Kategorie: {str(e)}")


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category_endpoint(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    """
    Aktualisiert eine bestehende Kategorie.
    """
    try:
        db_category = db.query(Category).filter(Category.id == category_id).first()
        if not db_category:
            raise HTTPException(status_code=404, detail="Kategorie nicht gefunden")

        # Prüfe ob neuer Name bereits existiert (und es nicht die gleiche Kategorie ist)
        if db_category.name != category.name:
            existing = db.query(Category).filter(Category.name == category.name).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"Kategorie '{category.name}' existiert bereits")

        # Wenn der Name sich ändert, muss auch der CategoryRules Name aktualisiert werden
        if db_category.name != category.name:
            db.query(CategoryRules).filter_by(category_name=db_category.name).update(
                {CategoryRules.category_name: category.name}
            )

        db_category.name = category.name
        db_category.category_type = category.category_type
        db_category.icon = category.icon
        db_category.farbe = category.farbe

        db.commit()
        db.refresh(db_category)
        return db_category

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren der Kategorie: {str(e)}")


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    Löscht eine Kategorie.
    Nutzt die remove_category() Funktion aus dem categories Modul.
    """
    try:
        # Prüfe ob Kategorie existiert
        db_category = db.query(Category).filter(Category.id == category_id).first()
        if not db_category:
            raise HTTPException(status_code=404, detail="Kategorie nicht gefunden")

        # Prüfe ob Kategorie von Transaktionen verwendet wird
        if db_category.transaktionen:
            raise HTTPException(
                status_code=400,
                detail="Diese Kategorie wird noch von Transaktionen verwendet und kann nicht gelöscht werden"
            )

        # Nutze die remove_category Funktion (löscht auch die CategoryRules)
        remove_category(id=category_id)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen der Kategorie: {str(e)}")


# ==================== KATEGORIE-REGELN ENDPOINTS ====================

@router.get("/{category_id}/rules", response_model=CategoryRulesResponse)
def get_category_rules_endpoint(category_id: int, db: Session = Depends(get_db)):
    """
    Gibt die Regeln (Keywords) einer Kategorie zurück.
    Nutzt die Categorizer Klasse um die Keywords zu laden.
    """
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Kategorie nicht gefunden")

        # Nutze Categorizer um die Rules zu laden
        categorizer = Categorizer()
        rules_dict = categorizer._get_rules()
        
        # Die Struktur ist: {category_name: {"keywords": "kw1, kw2", "category": ..., "created_at": ...}}
        rule_data = rules_dict.get(category.name, {})
        keywords_str = rule_data.get("keywords", "")
        keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]

        return {
            "id": category_id,
            "category_name": category.name,
            "keywords": keywords
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Regeln: {str(e)}")


@router.put("/{category_id}/rules")
def update_category_rules(category_id: int, keywords: List[str], db: Session = Depends(get_db)):
    """
    Aktualisiert die Regeln (Keywords) einer Kategorie komplett.
    Nutzt die Categorizer Klasse.
    """
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Kategorie nicht gefunden")

        # Normalisiere Keywords (lowercase, dedupliziere)
        keywords = list(set(k.strip().lower() for k in keywords if k.strip()))

        # Nutze Categorizer um die Rules zu aktualisieren
        categorizer = Categorizer()
        
        # Lösche alte Keywords und füge neue hinzu
        # Entferne zuerst alle alten Keywords
        rules = db.query(CategoryRules).filter_by(category_name=category.name).first()
        if rules:
            db.delete(rules)
            db.commit()
        
        # Füge neue Keywords hinzu
        if keywords:
            categorizer.add_keyword_to_rule(category.name, keywords)
        
        # Invalidiere Cache
        categorizer.invalidate_cache()

        return {
            "id": category_id,
            "category_name": category.name,
            "keywords": keywords
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren der Regeln: {str(e)}")


@router.post("/{category_id}/rules/keywords", status_code=201)
def add_keyword(category_id: int, request: KeywordRequest, db: Session = Depends(get_db)):
    """
    Fügt ein Schlüsselwort zu den Regeln einer Kategorie hinzu.
    Nutzt die Categorizer Klasse.
    """
    try:
        keyword = request.keyword.strip().lower()
        if not keyword:
            raise HTTPException(status_code=400, detail="Schlüsselwort darf nicht leer sein")
        
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Kategorie nicht gefunden")

        # Nutze Categorizer um das Keyword hinzuzufügen
        categorizer = Categorizer()
        
        # Prüfe ob Rule für diese Kategorie existiert
        rules_dict = categorizer._get_rules()
        rule_data = rules_dict.get(category.name, {})
        keywords_str = rule_data.get("keywords", "")
        existing_keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
        
        if keyword in existing_keywords:
            raise HTTPException(status_code=400, detail="Dieses Schlüsselwort existiert bereits")
        
        # Wenn noch keine Rule existiert, erstelle eine neue
        if not rule_data or not keywords_str:
            rule = db.query(CategoryRules).filter_by(category_name=category.name).first()
            if not rule:
                # Erstelle neue CategoryRules
                new_rule = CategoryRules(
                    category_name=category.name,
                    keywords=keyword
                )
                db.add(new_rule)
                db.commit()
            else:
                # Rule existiert, aber hat keine Keywords
                categorizer.add_keyword_to_rule(category.name, [keyword])
        else:
            # Rule existiert bereits mit Keywords
            categorizer.add_keyword_to_rule(category.name, [keyword])
        
        # Lade aktualisierte Keywords
        categorizer.invalidate_cache()
        rules_dict = categorizer._get_rules()
        rule_data = rules_dict.get(category.name, {})
        keywords_str = rule_data.get("keywords", "")
        keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]

        return {
            "id": category_id,
            "category_name": category.name,
            "keywords": keywords
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Hinzufügen des Schlüsselworts: {str(e)}")


@router.delete("/{category_id}/rules/keywords/{keyword}", status_code=204)
def remove_keyword(category_id: int, keyword: str, db: Session = Depends(get_db)):
    """
    Entfernt ein Schlüsselwort aus den Regeln einer Kategorie.
    Nutzt die Categorizer Klasse.
    """
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Kategorie nicht gefunden")

        keyword = keyword.strip().lower()

        # Nutze Categorizer um das Keyword zu entfernen
        categorizer = Categorizer()
        
        # Prüfe ob Keyword existiert
        rules_dict = categorizer._get_rules()
        rule_data = rules_dict.get(category.name, {})
        keywords_str = rule_data.get("keywords", "")
        existing_keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
        
        if keyword not in existing_keywords:
            raise HTTPException(status_code=404, detail="Schlüsselwort nicht gefunden")
        
        # Entferne Keyword
        categorizer.remove_keyword_from_rule(category.name, keyword)
        categorizer.invalidate_cache()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Entfernen des Schlüsselworts: {str(e)}")
