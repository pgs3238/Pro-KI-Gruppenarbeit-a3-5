from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import tempfile
import json
from pathlib import Path
from src.database.connection import SessionLocal
from src.database.csv_importer import CSVTransaktionImporter

router = APIRouter(prefix="/transactions", tags=["Import"])

@router.post("/import")
async def import_transactions(
    file: UploadFile = File(...),
    header_row: int = Form(...),
    mapping: str = Form(...),
    skip_footer: int = Form(0),
    konto_id: int | None = Form(None)
):
    if not file.filename.endswith((".csv", ".xlsx")):
        raise HTTPException(status_code=400, detail="Invalid file type")

    mapping = json.loads(mapping)

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    session = SessionLocal()

    try:
        importer = CSVTransaktionImporter(
            session=session,
            mapping=mapping,
            header_row=header_row,
            skip_footer=skip_footer,
            konto_id=konto_id
        )
        importer.import_csv(tmp_path)

        return {"status": "success"}

    finally:
        session.close()
        tmp_path.unlink(missing_ok=True)
