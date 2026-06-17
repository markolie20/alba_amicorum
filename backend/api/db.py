import psycopg2
import psycopg2.extras
from contextlib import contextmanager


@contextmanager
def get_conn():
    conn = psycopg2.connect(dbname="alba", user="postgres", password="admin", host="localhost")
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_cursor():
    with get_conn() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            yield cursor
        finally:
            cursor.close()
