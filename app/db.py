import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
conn.autocommit = True
cursor = conn.cursor()