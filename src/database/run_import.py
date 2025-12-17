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