import pg8000.dbapi as pg
import local_functions as LFunc


conn = LFunc.connect_db()
cur = conn.cursor()
cur.execute("""
    SELECT DISTINCT raw_location
    FROM (
        SELECT raw_location FROM location_album_table
        UNION
        SELECT raw_location FROM location_bijdrage_table
    ) AS all_locations
    WHERE raw_location IS NOT NULL
    ORDER BY raw_location
""")

for row in cur.fetchall():
    print(row[0])

for location, count in cur.fetchall():
    print(f"{location}: {count}")

rows = cur.fetchall()

for row in rows:
    print(row)

cur.close()
conn.close()