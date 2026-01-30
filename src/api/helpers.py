from fastapi import HTTPException
from sqlalchemy.orm import Session


def get_or_404(db: Session, model, obj_id: int, *, detail: str):
    """
    Lädt ein ORM-Objekt per ID oder wirft 404.

    Hinweis: bewusst simpel gehalten (nur .id), um Risiko gering zu halten.
    """
    obj = db.query(model).filter(model.id == obj_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=detail)
    return obj

