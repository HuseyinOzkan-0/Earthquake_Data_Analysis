import sqlite3
import os

db = 'earthquakes.db'
if not os.path.exists(db):
    print('DB file not found:', db)
    raise SystemExit(1)

conn = sqlite3.connect(db)
cur = conn.cursor()

try:
    cur.execute("SELECT count(*), max(date || ' ' || time) FROM Earthquake")
    row = cur.fetchone()
    print('count:', row[0])
    print('latest datetime:', row[1])

    print('\n-- 5 newest rows --')
    cur.execute("SELECT id, date, time, lat, lng, depth, mag, location FROM Earthquake ORDER BY date DESC, time DESC LIMIT 5")
    for r in cur.fetchall():
        print(r)

finally:
    conn.close()
