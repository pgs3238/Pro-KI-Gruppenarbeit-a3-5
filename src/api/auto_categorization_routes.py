from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..categories.auto_categorizer_service import get_auto_categorizer_service
from .dependencies import get_db

router = APIRouter(prefix="/categories", tags=["Auto-Categorization"])

# Globale Service-Instanz (Singleton kommt aus get_auto_categorizer_service)
auto_categorizer = get_auto_categorizer_service()


@router.post("/auto-categorize")
def trigger_auto_categorization(
    max_iterations: Optional[int] = None,
    min_occurrences: int = 3,
    db: Session = Depends(get_db),
):
    """
    Manueller Trigger für Auto-Kategorisierung.
    Nützlich für Tests und Debugging.

    Args:
        max_iterations: Maximale Anzahl von Iterationen (None = unbegrenzt)
        min_occurrences: Minimale Häufigkeit für neue Keywords beim Lernen
    """

    stats = auto_categorizer.run_full_categorization_cycle(
        max_iterations=max_iterations, min_occurrences=min_occurrences
    )

    return {"message": "Auto-Kategorisierung abgeschlossen", "statistics": stats}


@router.get("/auto-categorize/status")
def get_auto_categorization_status(db: Session = Depends(get_db)):
    """
    Gibt den Status der Auto-Kategorisierung zurück.
    """

    state = auto_categorizer.get_categorization_state()

    return {
        "new_transactions_count": state["has_new_transactions"],
        "last_categorization": state["last_categorization"],
        "will_trigger_at": 5,  # Schwelle
        "needs_categorization": state["has_new_transactions"] >= 5,
    }

