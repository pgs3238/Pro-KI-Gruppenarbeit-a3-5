"""
Author: Paul-Gerhard Siegel
Course: Programmieren für KI
Description:
    Example script to import transactions from a CSV file into the database.
    It initializes the database, creates a session, and runs the CSVTransaktionImporter
    on a CSV file located in the 'examples' folder. Designed for manual testing or
    demonstration purposes before a frontend is implemented.
"""
from pathlib import Path
from src.database.csv_importer import CSVTransaktionImporter 
from src.database.connection import SessionLocal, init_db

# Sicherstellen, dass die DB initialisiert ist. 
init_db() 

# Session erstellen
session = SessionLocal()

# Pfad zur CSV-Datei im „examples“-Ordner. Sobald ein Frontend vorliegt 
# kann dieser pfad durch das auswählen einer Datei im Frontend ersetzt werden. 
# bzw. durch @app.post("/import-csv/")
csv_file = Path(__file__).parent.parent.parent / "examples" / "transaktionen.csv"

# CSV-Datei importieren
importer = CSVTransaktionImporter (session)
importer.import_csv(csv_file)

print("Import finished")

session.close()