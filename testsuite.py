import sqlite3

conn = sqlite3.connect('dayrates.db')
c = conn.cursor()
c.execute('INSERT INTO planters(oid, fname, lname) VALUES (5, "Margot", "Thorseth")')
c.execute('SELECT oid, * FROM planters')
print(c.fetchall())
conn.commit()
conn.close()