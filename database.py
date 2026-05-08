import os
import psycopg2
from pgvector.psycopg2 import register_vector # type: ignore

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_USER = os.getenv("DB_USER", "fyp_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "fyp_password")
DB_NAME = os.getenv("DB_NAME", "fyp_db")

def get_raw_connection():
    """Returns a raw PG connection without attempting to register pgvector schemas yet."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )

def get_connection():
    """Returns a PG connection with pgvector decoders loaded. Fails if extension doesn't exist."""
    conn = get_raw_connection()
    register_vector(conn)
    return conn

def init_db():
    conn = None
    try:
        conn = get_raw_connection()
        cur = conn.cursor()
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                openalex_id TEXT PRIMARY KEY,
                title TEXT,
                doi TEXT,
                abstract TEXT,
                publication_year INTEGER,
                authors TEXT[],
                author_names TEXT,
                embedding vector(384)
            );
        """)
        conn.commit()
        cur.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing DB: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()
