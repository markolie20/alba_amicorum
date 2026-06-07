import pg8000.dbapi as pg


def connect_db():
    return pg.connect(
        user="mark",
        password="wachtwoord",
        database="alba",
        host="localhost",
        port=5432,
    )