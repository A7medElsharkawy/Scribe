import os
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.pool import SimpleConnectionPool
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


_pool: SimpleConnectionPool | None = None

def _get_pool() -> SimpleConnectionPool:
    global _pool
    if _pool is None:
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            raise RuntimeError("DATABASE_URL environment variable not set")
        _pool = SimpleConnectionPool(1, 10, db_url, connect_timeout=5)
    return _pool


def get_connection():
    return _get_pool().getconn()

def return_connection(conn):
    return _get_pool().putconn(conn=conn)


    
def init_db():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS papers (
                        id          TEXT PRIMARY KEY,
                        title       TEXT,
                        abstract    TEXT,
                        authors     TEXT[],
                        published   DATE,
                        categories  TEXT[],
                        embedding   vector(1536)
                    );
                """)
        conn.commit()
    finally:
        return_connection(conn=conn)




