import local_functions as LF


def postgis_ready():
    try:
        # --------------------------------------------------
        # CONNECT
        # --------------------------------------------------

        conn = LF.connect_db()
        cur = conn.cursor()

        cur = conn.cursor()

        print("Connected to database.")

        # --------------------------------------------------
        # CHECK TABLE EXISTS
        # --------------------------------------------------

        cur.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = 'place_table'
            )
        """)

        table_exists = cur.fetchone()[0]

        if not table_exists:
            raise Exception("place_table does not exist.")

        print("place_table exists.")

        # --------------------------------------------------
        # ENABLE POSTGIS
        # --------------------------------------------------

        cur.execute("""
            CREATE EXTENSION IF NOT EXISTS postgis;
        """)

        print("PostGIS extension checked.")

        # --------------------------------------------------
        # CHECK EXISTING COLUMNS
        # --------------------------------------------------

        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'place_table'
        """)

        existing_columns = {
            row[0]
            for row in cur.fetchall()
        }

        print(f"Existing columns: {existing_columns}")

        # --------------------------------------------------
        # ADD latitude
        # --------------------------------------------------

        if "latitude" not in existing_columns:

            cur.execute("""
                ALTER TABLE place_table
                ADD COLUMN latitude DOUBLE PRECISION
            """)

            print("Added latitude column.")

        else:
            print("latitude column already exists.")

        # --------------------------------------------------
        # ADD longitude
        # --------------------------------------------------

        if "longitude" not in existing_columns:

            cur.execute("""
                ALTER TABLE place_table
                ADD COLUMN longitude DOUBLE PRECISION
            """)

            print("Added longitude column.")

        else:
            print("longitude column already exists.")

        # --------------------------------------------------
        # ADD coordinates
        # --------------------------------------------------

        if "coordinates" not in existing_columns:

            cur.execute("""
                ALTER TABLE place_table
                ADD COLUMN coordinates GEOGRAPHY(POINT, 4326)
            """)

            print("Added coordinates column.")

        else:
            print("coordinates column already exists.")

        # --------------------------------------------------
        # CREATE SPATIAL INDEX
        # --------------------------------------------------

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_place_coordinates
            ON place_table
            USING GIST (coordinates)
        """)

        print("Spatial index checked.")

        # --------------------------------------------------
        # VERIFY FINAL STRUCTURE
        # --------------------------------------------------

        cur.execute("""
            SELECT
                column_name,
                data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'place_table'
            ORDER BY ordinal_position
        """)

        print("\n=== FINAL place_table STRUCTURE ===")

        for column_name, data_type in cur.fetchall():
            print(f"{column_name} ({data_type})")

        # --------------------------------------------------
        # COMMIT
        # --------------------------------------------------

        conn.commit()

        print("\nMigration completed successfully.")

    except Exception as e:

        if conn:
            conn.rollback()

        print("\nMigration failed.")
        print(e)

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

        print("Connection closed.")