import os
from contextlib import contextmanager

import psycopg
from dotenv import load_dotenv


load_dotenv(dotenv_path=".env")


def get_conninfo() -> str:
    return (
        f"host={os.getenv('POSTGRES_HOST')} "
        f"port={os.getenv('POSTGRES_PORT')} "
        f"dbname={os.getenv('POSTGRES_DB')} "
        f"user={os.getenv('POSTGRES_USER')} "
        f"password={os.getenv('POSTGRES_PASSWORD')}"
    )


@contextmanager
def get_connection():
    conn = psycopg.connect(get_conninfo())
    try:
        yield conn
    finally:
        conn.close()
