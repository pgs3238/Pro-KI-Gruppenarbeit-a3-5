# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# import os
# print(os.getcwd())          # current working directory
# print(os.path.exists("transaktionen.csv"))

# from models import Base
# from csv_importer import CSVTransaktionImporter 

# engine = create_engine("sqlite:///database.db")
# Session = sessionmaker(bind=engine)
# session = Session()

# Base.metadata.create_all(engine)

# importer = CSVTransaktionImporter(session)
# importer.import_csv("transaktionen.csv")

# print("Import finished")


# run_import.py
from pathlib import Path
from src.database.csv_importer import CSVTransaktionImporter 
from src.database.connection import SessionLocal, init_db

# Make sure DB is initialized
init_db()

# Create a session
session = SessionLocal()

# Path to the CSV file in the examples folder
csv_file = Path(__file__).parent.parent.parent / "examples" / "transaktionen.csv"

# Import CSV
importer = CSVTransaktionImporter (session)
importer.import_csv(csv_file)

print("Import finished")

session.close()