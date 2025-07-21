import os
from database import TriviaDatabase
from dotenv import load_dotenv

if __name__ == "__main__":
    # Load .env file
    load_dotenv()
    password = os.getenv("TRIVIA_DB_PASSWORD")
    if not password:
        raise RuntimeError("TRIVIA_DB_PASSWORD not set in .env file!")
    os.environ["TRIVIA_DB_PASSWORD"] = password

    db = TriviaDatabase()

    try:
        with open("src/data/trivia_database.db.gz", "rb") as f:
            encrypted = f.read()
        print(f"[TEST] Read {len(encrypted)} bytes from trivia_database.db.gz")
        decrypted = db.decrypt_data(encrypted)
        decompressed = db.decompress_data(decrypted)
        print("[TEST] SUCCESS: Decrypted and decompressed content (truncated):")
        print(str(decompressed)[:500])
    except Exception as e:
        print(f"[TEST] ERROR: {e}") 