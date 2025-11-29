import sqlite3

# Connect to database (creates file if not exists)
conn = sqlite3.connect("databaseTest01.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Person (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT,
    FamilyName TEXT,
    Birthday DATE,
    Address TEXT
)
""")

conn.commit()
conn.close()

print("Table 'Person' created successfully.")

#---------------------------------------------------------------------------
#import sqlite3

# Connect to database
conn = sqlite3.connect("databaseTest01.db")
cursor = conn.cursor()

# Insert data
cursor.execute("""
INSERT INTO Person (Name, FamilyName, Birthday, Address)
VALUES (?, ?, ?, ?)
""", ('Dagobert', 'Duck', '1959-12-15', 'Geldspeicherweig 1, Entenhausen'))

conn.commit()
conn.close()

print("Row inserted successfully.")

#---------------------------------------------------------------------------
#import sqlite3

conn = sqlite3.connect("databaseTest01.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM Person")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()