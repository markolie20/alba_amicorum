from loc_nm_mapping import mapping
import local_functions as LF
import local_queries as LQ

conn = LF.connect_db()
cur = conn.cursor()



def NormaliseRawLocations():
    for raw, normalized in mapping.items():
        cur.execute(LQ.insert_normalization_table, (raw, normalized))
    try:
        # Preview album replacements
        cur.execute("""
            SELECT
                la.raw_location,
                ln.normalized_location,
                COUNT(*)
            FROM location_album_table la
            JOIN location_normalization ln
                ON ln.raw_location = la.raw_location
            GROUP BY la.raw_location, ln.normalized_location
            ORDER BY la.raw_location
        """)

        print("\n=== ALBUM LOCATIONS TO REPLACE ===")
        for raw, normalized, count in cur.fetchall():
            print(f"{raw!r} -> {normalized!r} ({count} rows)")

        # Preview bijdrage replacements
        cur.execute("""
            SELECT
                lb.raw_location,
                ln.normalized_location,
                COUNT(*)
            FROM location_bijdrage_table lb
            JOIN location_normalization ln
                ON ln.raw_location = lb.raw_location
            GROUP BY lb.raw_location, ln.normalized_location
            ORDER BY lb.raw_location
        """)

        print("\n=== BIJDRAGE LOCATIONS TO REPLACE ===")
        for raw, normalized, count in cur.fetchall():
            print(f"{raw!r} -> {normalized!r} ({count} rows)")

        # Update album raw_location
        cur.execute("""
            UPDATE location_album_table la
            SET raw_location = ln.normalized_location
            FROM location_normalization ln
            WHERE la.raw_location = ln.raw_location
        """)

        print("\nUpdated album rows:", cur.rowcount)

        # Update bijdrage raw_location
        cur.execute("""
            UPDATE location_bijdrage_table lb
            SET raw_location = ln.normalized_location
            FROM location_normalization ln
            WHERE lb.raw_location = ln.raw_location
        """)

        print("Updated bijdrage rows:", cur.rowcount)

        conn.commit()
        print("\nNormalization replacement complete.")

    except Exception as e:
        conn.rollback()
        print("Failed:", e)

    finally:
        cur.close()
        conn.close()