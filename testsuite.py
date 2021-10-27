import sqlite3

conn = sqlite3.connect('dayrates.db')
c = conn.cursor()
c.execute('DELETE FROM seedlots WHERE code ="FR001"')
conn.commit()
conn.close()