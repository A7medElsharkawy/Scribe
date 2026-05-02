import os
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.pool import SimpleConnectionPool
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

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


def get_embedding(text: str)->list[float]:
    output = client.embeddings.create(input=[text], model='text-embedding-3-small')
    return output.data[0].embedding

def get_batch_embedding(texts:list[str]):
    if not texts:
        return []
    output = client.embeddings.create(input=texts, model='text-embedding-3-small')

    return [item.embedding for item in output.data]



def upsert_papers(papers: list[dict]):

    if not papers:
        return
    
    texts = [f"{p['title']}. {p['abstract']}" for p in papers]
    embedding = get_batch_embedding(texts)

    rows=[
        (
            p["id"],
            p["title"],
            p["abstract"],
            p.get("authors", []),
            p.get("published"),
            p.get("categories", []),
            vector
        )
    for p, vector in zip(papers, embedding)]

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            execute_values(cur, """
                INSERT INTO papers (id, title, abstract, authors, published, categories, embedding)
                VALUES %s
                ON CONFLICT (id) DO NOTHING;
            """, rows)
        conn.commit()
    finally:
        return_connection(conn)


def vector_search(query: str, top_k: int = 15)-> list[dict]:
    query_vector = get_embedding(query)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                    SELECT id, title, abstract, authors, published, categories,
                        1 - (embedding <=> %s::vector) AS similarity
                    FROM papers
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s;
                """, (query_vector, query_vector, top_k))
            cols = ["id", "title", "abstract", "authors", "published", "categories", "similarity"]
            return [dict(zip(cols,row)) for row in cur.fetchall()]
    finally:
        return_connection(conn=conn)
    

