import pg8000.dbapi as pg
import local_variables as LVar
from LocationNormalisation import NormaliseRawLocations
from create_tables import create_tables
from insert_db import insert_data
from postgis_insert import insert_postgis
from postgis_ready import postgis_ready


def create_database():
    # connect to default postgres database first
    conn = pg.connect(
        database="postgres",
        **LVar.DB_CONFIG
    )

    conn.autocommit = True
    cur = conn.cursor()

    # check if database already exists
    cur.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (LVar.DB_NAME,)
    )

    exists = cur.fetchone()

    if exists:
        print(f"Database '{LVar.DB_NAME}' already exists.")
    else:
        cur.execute(f'CREATE DATABASE "{LVar.DB_NAME}"')
        print(f"Database '{LVar.DB_NAME}' created.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    create_database()
    create_tables()
    insert_data()
    NormaliseRawLocations()
    insert_postgis()
    postgis_ready()