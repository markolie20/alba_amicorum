"""
Run this to check your local database matches the expected schema.
Usage: python verify_db.py [--user <user>] [--password <pw>] [--db <db>] [--host <host>] [--port <port>]
"""

import argparse
import sys
import pg8000.dbapi as pg

EXPECTED_EXTENSIONS = ["uuid-ossp", "postgis"]

EXPECTED_TABLES = {
    "album_table": {
        "albumid": "uuid",
        "url": "text",
        "name": "text",
        "datecreated": "date",
        "width": "integer",
        "height": "integer",
        "funder": "text",
        "identifier1": "text",
        "identifier2": "text",
        "identifier3": "text",
        "numberofpages": "integer",
    },
    "bijdrage_table": {
        "bijdrageid": "uuid",
        "albumid": "uuid",
        "url": "text",
        "datecreated": "date",
        "name": "text",
        "page": "integer",
        "position": "integer",
    },
    "place_table": {
        "placeid": "uuid",
        "location": "text",
        "latitude": "double precision",
        "longitude": "double precision",
        "coordinates": "geography",
    },
    "location_album_table": {
        "locationid": "uuid",
        "albumid": "uuid",
        "raw_location": "text",
        "placeid": "uuid",
    },
    "location_bijdrage_table": {
        "locationid": "uuid",
        "bijdrageid": "uuid",
        "raw_location": "text",
        "placeid": "uuid",
    },
    "album_author_table": {
        "authorid": "uuid",
        "albumid": "uuid",
        "name": "text",
    },
    "bijdrage_author_table": {
        "authorid": "uuid",
        "bijdrageid": "uuid",
        "name": "text",
    },
    "description_album_table": {
        "descriptionid": "uuid",
        "albumid": "uuid",
        "description": "text",
    },
    "description_bijdrage_table": {
        "descriptionid": "uuid",
        "bijdrageid": "uuid",
        "description": "text",
    },
    "album_language_table": {
        "languageid": "uuid",
        "albumid": "uuid",
        "language": "text",
    },
    "album_material_table": {
        "materialid": "uuid",
        "albumid": "uuid",
        "material": "text",
    },
    "location_normalization": {
        "raw_location": "text",
        "normalized_location": "text",
    },
}

# (table, column) -> (references_table, references_column)
EXPECTED_FKS = {
    ("bijdrage_table", "albumid"): ("album_table", "albumid"),
    ("location_album_table", "albumid"): ("album_table", "albumid"),
    ("location_album_table", "placeid"): ("place_table", "placeid"),
    ("location_bijdrage_table", "bijdrageid"): ("bijdrage_table", "bijdrageid"),
    ("location_bijdrage_table", "placeid"): ("place_table", "placeid"),
    ("album_author_table", "albumid"): ("album_table", "albumid"),
    ("bijdrage_author_table", "bijdrageid"): ("bijdrage_table", "bijdrageid"),
    ("description_album_table", "albumid"): ("album_table", "albumid"),
    ("description_bijdrage_table", "bijdrageid"): ("bijdrage_table", "bijdrageid"),
    ("album_language_table", "albumid"): ("album_table", "albumid"),
    ("album_material_table", "albumid"): ("album_table", "albumid"),
}


def ok(msg):
    print(f"  [OK]   {msg}")

def fail(msg):
    print(f"  [FAIL] {msg}")

def warn(msg):
    print(f"  [WARN] {msg}")

def section(title):
    print(f"\n--- {title} ---")


def check_extensions(cur):
    section("Extensions")
    cur.execute("SELECT extname FROM pg_extension;")
    installed = {row[0] for row in cur.fetchall()}
    all_ok = True
    for ext in EXPECTED_EXTENSIONS:
        if ext in installed:
            ok(ext)
        else:
            fail(f"{ext} is NOT installed")
            all_ok = False
    return all_ok


def check_tables_and_columns(cur):
    section("Tables & Columns")
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    """)
    existing_tables = {row[0] for row in cur.fetchall()}

    cur.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public';
    """)
    existing_cols = {}
    for table, col, dtype in cur.fetchall():
        existing_cols.setdefault(table, {})[col] = dtype

    all_ok = True
    for table, expected_cols in EXPECTED_TABLES.items():
        if table not in existing_tables:
            fail(f"Table '{table}' is MISSING")
            all_ok = False
            continue

        actual_cols = existing_cols.get(table, {})
        col_issues = []
        for col, expected_type in expected_cols.items():
            if col not in actual_cols:
                col_issues.append(f"column '{col}' missing")
            elif not actual_cols[col].startswith(expected_type.split()[0]):
                col_issues.append(f"column '{col}' type is '{actual_cols[col]}', expected '{expected_type}'")

        if col_issues:
            fail(f"Table '{table}': " + ", ".join(col_issues))
            all_ok = False
        else:
            ok(f"Table '{table}'")
    return all_ok


def check_foreign_keys(cur):
    section("Foreign Keys")
    cur.execute("""
        SELECT
            tc.table_name, kcu.column_name,
            ccu.table_name AS foreign_table,
            ccu.column_name AS foreign_column
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public';
    """)
    actual_fks = {}
    for row in cur.fetchall():
        actual_fks[(row[0], row[1])] = (row[2], row[3])

    all_ok = True
    for (table, col), (ref_table, ref_col) in EXPECTED_FKS.items():
        key = (table, col)
        if key not in actual_fks:
            fail(f"{table}.{col} -> {ref_table}.{ref_col} is MISSING")
            all_ok = False
        elif actual_fks[key] != (ref_table, ref_col):
            fail(f"{table}.{col} points to {actual_fks[key]}, expected {ref_table}.{ref_col}")
            all_ok = False
        else:
            ok(f"{table}.{col} -> {ref_table}.{ref_col}")
    return all_ok


def check_row_counts(cur):
    section("Row Counts")
    for table in EXPECTED_TABLES:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        count = cur.fetchone()[0]
        print(f"  {table}: {count} rows")


def main():
    parser = argparse.ArgumentParser(description="Verify the alba database schema.")
    parser.add_argument("--user", default="postgres")
    parser.add_argument("--password", default="wachtwoord")
    parser.add_argument("--db", default="alba")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5432)
    args = parser.parse_args()

    print(f"Connecting to {args.db} on {args.host}:{args.port} as {args.user}...")
    try:
        conn = pg.connect(
            user=args.user,
            password=args.password,
            database=args.db,
            host=args.host,
            port=args.port,
        )
    except Exception as e:
        print(f"[ERROR] Could not connect: {e}")
        sys.exit(1)

    cur = conn.cursor()
    results = []
    results.append(check_extensions(cur))
    results.append(check_tables_and_columns(cur))
    results.append(check_foreign_keys(cur))
    check_row_counts(cur)

    cur.close()
    conn.close()

    section("Summary")
    if all(results):
        print("  All checks passed.")
    else:
        print("  Some checks FAILED. Fix the issues above before running the project.")
        sys.exit(1)


if __name__ == "__main__":
    main()
