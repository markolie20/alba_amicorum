import pg8000.dbapi as pg

conn = None
cur = None

try:
    conn = pg.connect(
        user="postgres",
        password="Watiseenwachtwoord",
        database="alba",
        host="localhost",
        port=5432,
    )

    cur = conn.cursor()

    # --------------------------------------------------
    # HELPER
    # --------------------------------------------------

    def constraint_exists(name):
        cur.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.table_constraints
                WHERE table_schema = 'public'
                  AND constraint_name = %s
            )
        """, (name,))

        return cur.fetchone()[0]

    # --------------------------------------------------
    # CHECK UNMATCHED ALBUM LOCATIONS
    # --------------------------------------------------

    cur.execute("""
        SELECT DISTINCT la.location
        FROM location_album_table la
        LEFT JOIN place_table p
            ON p.place_name = la.location
        WHERE la.location IS NOT NULL
          AND p.place_name IS NULL
        ORDER BY la.location
    """)

    unmatched_album = cur.fetchall()

    # --------------------------------------------------
    # CHECK UNMATCHED BIJDRAGE LOCATIONS
    # --------------------------------------------------

    cur.execute("""
        SELECT DISTINCT lb.location
        FROM location_bijdrage_table lb
        LEFT JOIN place_table p
            ON p.place_name = lb.location
        WHERE lb.location IS NOT NULL
          AND p.place_name IS NULL
        ORDER BY lb.location
    """)

    unmatched_bijdrage = cur.fetchall()

    # --------------------------------------------------
    # ABORT IF UNMATCHED VALUES EXIST
    # --------------------------------------------------

    if unmatched_album or unmatched_bijdrage:

        print("Cannot add foreign keys.")
        print("These locations do not exist in place_table:\n")

        for row in unmatched_album:
            print("[ALBUM]", row[0])

        for row in unmatched_bijdrage:
            print("[BIJDRAGE]", row[0])

        conn.rollback()

    else:

        # --------------------------------------------------
        # UNIQUE CONSTRAINT
        # --------------------------------------------------

        if not constraint_exists("unique_place_name"):

            cur.execute("""
                ALTER TABLE place_table
                ADD CONSTRAINT unique_place_name
                UNIQUE (place_name)
            """)

            print("Added unique_place_name.")

        else:
            print("unique_place_name already exists.")

        # --------------------------------------------------
        # FK: location_album_table.location
        # --------------------------------------------------

        if not constraint_exists("fk_location_album_place_name"):

            cur.execute("""
                ALTER TABLE location_album_table
                ADD CONSTRAINT fk_location_album_place_name
                FOREIGN KEY (location)
                REFERENCES place_table(place_name)
                ON UPDATE CASCADE
                ON DELETE SET NULL
            """)

            print("Added fk_location_album_place_name.")

        else:
            print("fk_location_album_place_name already exists.")

        # --------------------------------------------------
        # FK: location_bijdrage_table.location
        # --------------------------------------------------

        if not constraint_exists("fk_location_bijdrage_place_name"):

            cur.execute("""
                ALTER TABLE location_bijdrage_table
                ADD CONSTRAINT fk_location_bijdrage_place_name
                FOREIGN KEY (location)
                REFERENCES place_table(place_name)
                ON UPDATE CASCADE
                ON DELETE SET NULL
            """)

            print("Added fk_location_bijdrage_place_name.")

        else:
            print("fk_location_bijdrage_place_name already exists.")

        # --------------------------------------------------
        # COMMIT
        # --------------------------------------------------

        conn.commit()

        print("\nForeign key setup completed successfully.")

except Exception as e:

    if conn:
        conn.rollback()

    print("\nFailed:")
    print(e)

finally:

    if cur:
        cur.close()

    if conn:
        conn.close()

    print("\nConnection closed.")