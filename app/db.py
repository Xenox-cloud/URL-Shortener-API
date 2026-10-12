import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
conn.autocommit = True
cursor = conn.cursor()

# Create the table and index on startup if they don't exist yet
SCHEMA = Path(__file__).resolve().parent.parent / "schema.sql"
cursor.execute(SCHEMA.read_text())
