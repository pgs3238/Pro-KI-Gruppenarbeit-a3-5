from sqlalchemy import create_engine, Column, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Integer, Column, String, Date
from sqlalchemy.orm import declarative_base
from datetime import date
#import os

# Define database URL (SQLite in this case)
DATABASE_URL = "sqlite:///databaseTest02.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=True)  # echo=True shows SQL commands

# Base class for models
Base = declarative_base()

# Define the Person table
class Person(Base):
    __tablename__ = "Person"

    id = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String)
    FamilyName = Column(String)
    Birthday = Column(Date)
    Address = Column(String)

# Create the table in the database
Base.metadata.create_all(engine)

#print("Current working directory:", os.getcwd())

#---------------------------------------------------------------------------

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Create a new person
dagobert = Person(
    Name="Dagobert",
    FamilyName="Duck",
    Birthday=date(1959, 12, 15),
    Address="Geldspeicherweig 1, Entenhausen"
)

# Add and commit to the database
session.add(dagobert)
session.commit()

print("Row inserted successfully!")

#---------------------------------------------------------------------------

# Query all rows
all_people = session.query(Person).all()
for person in all_people:
    print(person.Name, person.FamilyName, person.Birthday, person.Address)

#----