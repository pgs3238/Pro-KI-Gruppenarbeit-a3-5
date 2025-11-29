from sqlalchemy import create_engine, Column, String, Date, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import tkinter as tk
from tkinter import messagebox


# -------------------------------
# SQLALCHEMY SETUP (ORM)
# -------------------------------
DATABASE_URL = "sqlite:///databaseTest02.db"

engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()


class Person(Base):
    __tablename__ = "Person"

    id = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String)
    FamilyName = Column(String)
    Birthday = Column(Date)
    Address = Column(String)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


# -------------------------------
# ORM INSERT FUNCTION
# -------------------------------
def insert_person(name, family_name, birthday_str, address):
    try:
        # Convert string to date
        birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Birthday must be in YYYY-MM-DD format")

    new_person = Person(
        Name=name,
        FamilyName=family_name,
        Birthday=birthday,
        Address=address,
    )

    session.add(new_person)
    session.commit()


# -------------------------------
# GUI SAVE CALLBACK
# -------------------------------
def save_data():
    name = entry_name.get()
    family = entry_family.get()
    birthday = entry_birthday.get()
    address = entry_address.get()

    if not name or not family:
        messagebox.showerror("Error", "Name and Family Name are required.")
        return

    try:
        insert_person(name, family, birthday, address)
        messagebox.showinfo("Success", "Data saved to database!")
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))


# -------------------------------
# TKINTER GUI
# -------------------------------
root = tk.Tk()
root.title("Person Entry (SQLAlchemy ORM)")

# Labels + fields
tk.Label(root, text="Name").grid(row=0, column=0)
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1)

tk.Label(root, text="Family Name").grid(row=1, column=0)
entry_family = tk.Entry(root)
entry_family.grid(row=1, column=1)

tk.Label(root, text="Birthday (YYYY-MM-DD)").grid(row=2, column=0)
entry_birthday = tk.Entry(root)
entry_birthday.grid(row=2, column=1)

tk.Label(root, text="Address").grid(row=3, column=0)
entry_address = tk.Entry(root)
entry_address.grid(row=3, column=1)

# Save Button
save_btn = tk.Button(root, text="Save", command=save_data)
save_btn.grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
