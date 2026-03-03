import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
# Remove the +psycopg part for direct psycopg connection if needed, 
# although psycopg3 supports the URI directly.
# However, the URI usually starts with postgresql:// or postgres://

print(f"Testing connection to: {db_url}")

try:
    # URL in .env has postgresql+psycopg://... 
    # Let's clean it for a direct psycopg test
    clean_url = db_url.replace("postgresql+psycopg://", "postgresql://")
    
    with psycopg.connect(clean_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            print("Successfully connected to the database!")
            
            cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            extension = cur.fetchone()
            if extension:
                print("PGVector extension is ALREADY ENABLED.")
            else:
                print("PGVector extension IS NOT ENABLED. Enabling now...")
                try:
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                    conn.commit()
                    print("PGVector extension ENABLED SUCCESSFULLY.")
                except Exception as e:
                    print(f"Failed to enable PGVector extension: {e}")
except Exception as e:
    print(f"Connection error: {e}")
