"""
Author: Paul-Gerhard Siegel
Course: Programmieren für KI
Description:
    FastAPI endpoint for importing CSV transactions into the database.
"""
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
    """
    Imports transactions from an uploaded CSV file into the database.

    The endpoint accepts a CSV file via multipart form data, stores it temporarily
    on the server, and uses the CSVTransaktionImporter to insert the data into
    the database. The column mapping and CSV structure information are provided
    by the client (e.g. frontend).

    Args:
        file: Uploaded CSV file containing transaction data.
        header_row: Line number (1-based) where the CSV header is located.
        mapping: JSON string defining the mapping between CSV headers and model fields.
        skip_footer: Number of lines at the end of the file to ignore.
        konto_id: Optional account ID assigned to all imported transactions.

    Returns:
        JSON response indicating whether the import was successful.

    Raises:
        HTTPException: If the uploaded file is not a supported file type.
    """
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
