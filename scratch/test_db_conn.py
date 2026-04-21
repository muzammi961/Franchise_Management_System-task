import sqlalchemy
from sqlalchemy import create_engine

DB_URL = "postgresql+psycopg2://postgres:muzammil1513@127.0.0.1:5432/franchise_db"

def test_conn():
    print(f"Testing connection to {DB_URL}...")
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            print("Successfully connected to the database!")
            conn.execute(sqlalchemy.text("SELECT 1"))
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_conn()
