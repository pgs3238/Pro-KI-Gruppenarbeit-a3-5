# Zinsrechner API Routes für FastAPI

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import sqlite3
from pathlib import Path
import traceback

router = APIRouter(prefix="/zinsrechner", tags=["Zinsrechner"])

# Pfade
DATA_DIR = Path(__file__).parent.parent.parent / "data"
VERGLEICHE_DIR = DATA_DIR / "vergleiche"
VERGLEICHE_DIR.mkdir(parents=True, exist_ok=True)
EXPENSES_DB = DATA_DIR / "expenses.db"

# ==================== SCHEMAS ====================

class VergleichParameter(BaseModel):
    startkapital: float
    zinssatz: float
    intervall: str
    einzahlung: float
    laufzeit: int
    kontostandTyp: str

class VergleichPunkt(BaseModel):
    jahr: int
    periode: int
    kapital: float
    einzahlungGesamt: float
    zinsenGesamt: float

class VergleichSpeichern(BaseModel):
    db_nummer: int
    verlauf: List[VergleichPunkt]
    parameter: VergleichParameter

class KontoInfo(BaseModel):
    iban: str
    iban_kurz: str
    kontostand: float
    anzahl_transaktionen: int
    waehrung: str

# ==================== HILFSFUNKTIONEN ====================

def get_db_path(nummer: int) -> Path:
    return VERGLEICHE_DIR / f"vergleich_{nummer}.db"

def init_vergleich_db(db_path: Path):
    """Initialisiert eine Vergleichs-Datenbank"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parameter (
            kontostand REAL,
            zinssatz REAL,
            intervall TEXT,
            einzahlungen REAL,
            laufzeit INTEGER,
            kontostand_typ TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verlauf (
            Jahr INTEGER,
            Periode INTEGER,
            Kapital REAL,
            Einzahlungen_gesamt REAL,
            Zinsen_gesamt REAL
        )
    ''')
    
    conn.commit()
    conn.close()

# ==================== ROUTEN ====================

@router.post("/vergleich/speichern")
async def vergleich_speichern(data: VergleichSpeichern):
    """Speichert einen Vergleich in der Datenbank"""
    try:
        db_path = get_db_path(data.db_nummer)
        init_vergleich_db(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Parameter speichern
        cursor.execute('DELETE FROM parameter')
        cursor.execute('''
            INSERT INTO parameter (kontostand, zinssatz, intervall, einzahlungen, laufzeit, kontostand_typ)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.parameter.startkapital,
            data.parameter.zinssatz,
            data.parameter.intervall,
            data.parameter.einzahlung,
            data.parameter.laufzeit,
            data.parameter.kontostandTyp
        ))
        
        # Verlauf speichern
        cursor.execute('DELETE FROM verlauf')
        for punkt in data.verlauf:
            cursor.execute('''
                INSERT INTO verlauf (Jahr, Periode, Kapital, Einzahlungen_gesamt, Zinsen_gesamt)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                punkt.jahr,
                punkt.periode,
                punkt.kapital,
                punkt.einzahlungGesamt,
                punkt.zinsenGesamt
            ))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": f"Vergleich {data.db_nummer} gespeichert"}
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vergleich/alle")
async def vergleich_alle():
    """Lädt alle gespeicherten Vergleiche"""
    try:
        vergleiche = {}
        
        for i in range(1, 4):
            db_path = get_db_path(i)
            if not db_path.exists():
                continue
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Parameter laden
            cursor.execute('SELECT * FROM parameter')
            param_row = cursor.fetchone()
            
            if not param_row:
                conn.close()
                continue
            
            # Verlauf laden
            cursor.execute('SELECT * FROM verlauf ORDER BY Periode')
            verlauf_rows = cursor.fetchall()
            
            conn.close()
            
            vergleiche[f"vergleich_{i}"] = {
                "parameter": {
                    "startkapital": param_row[0],
                    "zinssatz": param_row[1],
                    "intervall": param_row[2],
                    "einzahlung": param_row[3],
                    "laufzeit": param_row[4],
                    "kontostandTyp": param_row[5] if len(param_row) > 5 else "fiktiv"
                },
                "verlauf": [
                    {
                        "jahr": row[0],
                        "periode": row[1],
                        "kapital": row[2],
                        "einzahlungGesamt": row[3],
                        "zinsenGesamt": row[4]
                    }
                    for row in verlauf_rows
                ]
            }
        
        return {"success": True, "vergleiche": vergleiche}
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/vergleich/loeschen/{nummer}")
async def vergleich_loeschen(nummer: int):
    """Löscht einen Vergleich"""
    try:
        db_path = get_db_path(nummer)
        
        if not db_path.exists():
            raise HTTPException(status_code=404, detail=f"Vergleich {nummer} nicht gefunden")
        
        db_path.unlink()
        return {"success": True, "message": f"Vergleich {nummer} gelöscht"}
    
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/kontostand")
async def get_kontostand():
    """Dummy-Endpoint für Rückwärtskompatibilität"""
    return {"success": True, "kontostand": 0}
