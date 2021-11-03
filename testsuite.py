import sqlite3

conn = sqlite3.connect('dayrates.db')
c = conn.cursor()
c.execute('DELETE FROM daily WHERE jour="2021-11-04"')
print(c.fetchall())
conn.commit()
conn.close()


