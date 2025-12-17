from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
print(os.getcwd())          # current working directory
print(os.path.exists("transaktionen.csv"))

from models import Base
from csv_importer import CSVTransaktionImporter  # 👈 important

engine = create_engine("sqlite:///database.db")
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

importer = CSVTransaktionImporter(session)
importer.import_csv("transaktionen.csv")

print("Import finished")