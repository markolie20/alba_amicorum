import local_queries as LQuery
import local_functions as LFunc

def create_tables():
    conn = LFunc.connect_db()
    cur = conn.cursor()

    cur.execute(LQuery.tables_creation)

    conn.commit()
    cur.close()
    conn.close()

    print("Tables created.")
