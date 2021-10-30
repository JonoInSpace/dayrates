import sqlite3

conn = sqlite3.connect('dayrates.db')
c = conn.cursor()
c.execute('UPDATE daily SET pid = pid-1')
print(c.fetchall())
conn.commit()
conn.close()


