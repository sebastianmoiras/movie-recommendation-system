# import pyodbc
# import os
# from dotenv import load_dotenv

# # Load isi file .env
# load_dotenv()

# def get_connection():
#     return pyodbc.connect(
#         f"Driver={{ODBC Driver 18 for SQL Server}};"
#         f"Server=tcp:{os.getenv('DB_SERVER')};"
#         f"Database={os.getenv('DB_NAME')};"
#         f"Uid={os.getenv('DB_USER')};"
#         f"Pwd={os.getenv('DB_PASSWORD')};"
#         "Encrypt=yes;"
#         "TrustServerCertificate=no;"
#     )
import os
import psycopg2
from dotenv import load_dotenv

# Load isi file .env
load_dotenv()

def get_connection():
    try:
        conn = psycopg2.connect(
            os.getenv("DATABASE_URL"),
            sslmode="require"   # Supabase butuh SSL
        )
        return conn
    except Exception as e:
        print("❌ Gagal koneksi ke database:", e)
        raise