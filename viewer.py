import sqlite3

conn=sqlite3.connect("usage_log.db")
c=conn.cursor()

c.execute("SELECT * FROM usage_log")
rows=c.fetchall()

for row in rows:
    print(row)

conn.close()