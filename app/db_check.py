import os
import psycopg
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

conninfo = (
    f"host={os.getenv('POSTGRES_HOST')} "
    f"port={os.getenv('POSTGRES_PORT')} "
    f"dbname={os.getenv('POSTGRES_DB')} "
    f"user={os.getenv('POSTGRES_USER')} "
    f"password={os.getenv('POSTGRES_PASSWORD')}"
)

with psycopg.connect(conninfo) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT current_database(), current_user;")
        database_name, user_name = cur.fetchone()
        print(f"Conexión correcta: base={database_name}, usuario={user_name}")
