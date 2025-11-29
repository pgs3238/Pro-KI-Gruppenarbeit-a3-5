import sqlite3
import tkinter as tk
from tkinter import messagebox

# -----------------------
# Database insert function
# -----------------------
def insert_person(name, family_name, birthday, address):
    conn = sqlite3.connect("databaseTest01.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO Person (Name, FamilyName, Birthday, Address)
    VALUES (?, ?, ?, ?)
    """, (name, family_name, birthday, address))

    conn.commit()
    conn.close()


# -----------------------
# GUI callback function
# -----------------------
def save_data():
    name = entry_name.get()
    family = entry_family.get()
    birthday = entry_birthday.get()
    address = entry_address.get()

    if not name or not family:
        messagebox.showerror("Error", "Name and Family Name are required.")
        return

    insert_person(name, family, birthday, address)
    messagebox.showinfo("Success", "Data saved to database.")


# -----------------------
# Tkinter GUI
# -----------------------
root = tk.Tk()
root.title("Person Entry")

# Labels + entry fields
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

# Save button
save_button = tk.Button(root, text="Save", command=save_data)
save_button.grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()