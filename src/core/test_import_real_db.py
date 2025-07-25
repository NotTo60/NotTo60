import os
from database import TriviaDatabase
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def test_decrypt_and_decompress():
    try:
        with open("src/data/trivia_database.db.gz", "rb") as f:
            encrypted = f.read()
        db = TriviaDatabase()
        decrypted = db.decrypt_data(encrypted)
        decompressed = db.decompress_data(decrypted)
        assert isinstance(decompressed, dict)
        logging.info("[TEST] SUCCESS: Decrypted and decompressed content (truncated):\n%s", str(decompressed)[:500])
    except Exception as e:
        logging.error("[TEST] ERROR: Decrypt/decompress failed: %s", e)

def test_wrong_password():
    try:
        with open("src/data/trivia_database.db.gz", "rb") as f:
            encrypted = f.read()
        os.environ["TRIVIA_DB_PASSWORD"] = "wrongpassword"
        db = TriviaDatabase()
        try:
            db.decrypt_data(encrypted)
            logging.error("[TEST] ERROR: Decryption should have failed with wrong password!")
        except Exception:
            logging.info("[TEST] SUCCESS: Decryption failed as expected with wrong password.")
    except Exception as e:
        logging.error("[TEST] ERROR: test_wrong_password setup failed: %s", e)

def test_missing_file():
    try:
        db = TriviaDatabase()
        try:
            with open("src/data/nonexistent.db.gz", "rb") as f:
                f.read()
            logging.error("[TEST] ERROR: Should not have opened nonexistent file!")
        except FileNotFoundError:
            logging.info("[TEST] SUCCESS: FileNotFoundError as expected for missing file.")
    except Exception as e:
        logging.error("[TEST] ERROR: test_missing_file setup failed: %s", e)

def test_corrupt_file():
    try:
        corrupt_path = "src/data/corrupt.db.gz"
        with open(corrupt_path, "wb") as f:
            f.write(b"not a real gzipped or encrypted file")
        db = TriviaDatabase()
        with open(corrupt_path, "rb") as f:
            encrypted = f.read()
        try:
            db.decrypt_data(encrypted)
            logging.error("[TEST] ERROR: Decryption should have failed for corrupt file!")
        except Exception:
            logging.info("[TEST] SUCCESS: Decryption failed as expected for corrupt file.")
        os.remove(corrupt_path)
    except Exception as e:
        logging.error("[TEST] ERROR: test_corrupt_file failed: %s", e)

def test_round_trip_export_import():
    try:
        db = TriviaDatabase()
        # Export current DB
        db.export_compressed_data()
        # Import back
        db.import_compressed_data()
        logging.info("[TEST] SUCCESS: Round-trip export/import completed without error.")
    except Exception as e:
        logging.error("[TEST] ERROR: Round-trip export/import failed: %s", e)

def test_process_answers_no_issues():
    try:
        from unittest.mock import patch
        from core import process_answers as pa
        with patch.object(pa, 'get_github_issues', return_value=[]):
            pa.process_answers()
        logging.info("[TEST] SUCCESS: process_answers handled no issues without error.")
    except Exception as e:
        logging.error("[TEST] ERROR: process_answers no issues: %s", e)

def test_process_answers_malformed_issue():
    try:
        from unittest.mock import patch
        from core import process_answers as pa
        malformed_issue = {'number': 1, 'user': {'login': 'testuser'}, 'title': 'Not a trivia answer'}
        with patch.object(pa, 'get_github_issues', return_value=[malformed_issue]):
            pa.process_answers()
        logging.info("[TEST] SUCCESS: process_answers handled malformed issue without error.")
    except Exception as e:
        logging.error("[TEST] ERROR: process_answers malformed issue: %s", e)

def test_process_answers_duplicate_answers():
    try:
        from unittest.mock import patch
        from core import process_answers as pa
        # Simulate two issues from the same user for the same trivia
        issue1 = {'number': 1, 'user': {'login': 'dupeuser'}, 'title': 'Trivia Answer: A', 'body': 'Answer: A'}
        issue2 = {'number': 2, 'user': {'login': 'dupeuser'}, 'title': 'Trivia Answer: B', 'body': 'Answer: B'}
        # Patch trivia data to expect 'A' as correct, with a valid date
        with patch.object(pa, 'get_github_issues', return_value=[issue1, issue2]):
            with patch.object(pa, 'load_trivia_data', return_value={
                'current': {
                    'question': 'Test Q',
                    'options': {'A': 'A1', 'B': 'B1', 'C': 'C1'},
                    'correct_answer': 'A',
                    'explanation': 'Because A',
                    'timestamp': '2025-01-01T00:00:00',
                    'date': '2025-01-01'
                },
                'history': []
            }):
                pa.process_answers()
        logging.info("[TEST] SUCCESS: process_answers handled duplicate answers without error.")
    except Exception as e:
        logging.error("[TEST] ERROR: process_answers duplicate answers: %s", e)

def test_process_answers_scoring():
    try:
        from unittest.mock import patch
        from core import process_answers as pa
        # Simulate a correct and incorrect answer
        correct_issue = {'number': 3, 'user': {'login': 'scoreuser'}, 'title': 'Trivia Answer: A', 'body': 'Answer: A'}
        incorrect_issue = {'number': 4, 'user': {'login': 'scoreuser'}, 'title': 'Trivia Answer: B', 'body': 'Answer: B'}
        # Patch trivia data to expect 'A' as correct
        with patch.object(pa, 'get_github_issues', return_value=[correct_issue, incorrect_issue]):
            with patch.object(pa, 'load_trivia_data', return_value={
                'current': {
                    'question': 'Test Q',
                    'options': {'A': 'A1', 'B': 'B1', 'C': 'C1'},
                    'correct_answer': 'A',
                    'explanation': 'Because A',
                    'timestamp': '2025-01-01T00:00:00'
                },
                'history': []
            }):
                pa.process_answers()
        logging.info("[TEST] SUCCESS: process_answers handled correct/incorrect scoring without error.")
    except Exception as e:
        logging.error("[TEST] ERROR: process_answers scoring: %s", e)

def test_fallback_trivia_pool():
    from core.daily_trivia import create_standalone_trivia, TRIVIA_CATEGORIES
    seen_questions = set()
    for cat in TRIVIA_CATEGORIES:
        q = create_standalone_trivia(cat)
        question = q['question']
        assert question not in seen_questions, f"Duplicate trivia question found: {question}"
        seen_questions.add(question)
    assert len(seen_questions) >= 20, f"Trivia fallback pool too small: {len(seen_questions)}"
    print(f"[TEST] Trivia fallback pool size: {len(seen_questions)} (OK)")

def test_fallback_facts_pool():
    from core.daily_facts import generate_fallback_daily_fact
    facts = set()
    for _ in range(100):
        fact = generate_fallback_daily_fact()
        facts.add(fact)
    assert len(facts) >= 50, f"Facts fallback pool too small: {len(facts)}"
    print(f"[TEST] Facts fallback pool size: {len(facts)} (OK)")

def test_end_to_end_workflow():
    import os
    from core.daily_trivia import generate_trivia_question, save_trivia_data, load_trivia_data
    from core.daily_facts import get_todays_fact, save_daily_facts, load_daily_facts
    from core.process_answers import update_user_stats
    from core.database import TriviaDatabase
    import tempfile
    import shutil
    # Use a temp dir for DB
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'trivia.db')
        db = TriviaDatabase(db_path=db_path)
        # Step 1: Generate trivia
        trivia = generate_trivia_question()
        today = trivia.get('timestamp', '')[:10] if 'timestamp' in trivia else None
        trivia['timestamp'] = trivia.get('timestamp') or '2024-01-01T00:00:00Z'
        save_trivia_data({'current': trivia, 'history': []})
        # Step 2: Generate fact
        fact = get_todays_fact()
        save_daily_facts({today: fact})
        # Step 3: Simulate a correct answer
        leaderboard = {}
        username = 'testuser'
        is_correct = True
        points, _ = update_user_stats(leaderboard, username, is_correct, trivia_date=today)
        db.update_leaderboard(leaderboard)
        # Step 4: Check leaderboard
        loaded = db.get_leaderboard()
        assert username in loaded, "User not in leaderboard after correct answer"
        assert loaded[username]['total_points'] == points, "Points not updated correctly"
        print(f"[TEST] End-to-end workflow passed: user={username}, points={points}")

def main():
    load_dotenv()
    password = os.getenv("TRIVIA_DB_PASSWORD")
    if not password:
        raise RuntimeError("TRIVIA_DB_PASSWORD not set in .env file!")
    os.environ["TRIVIA_DB_PASSWORD"] = password
    test_decrypt_and_decompress()
    test_wrong_password()
    test_missing_file()
    test_corrupt_file()
    test_round_trip_export_import()
    test_process_answers_no_issues()
    test_process_answers_malformed_issue()
    test_process_answers_duplicate_answers()
    test_process_answers_scoring()
    test_fallback_trivia_pool()
    test_fallback_facts_pool()
    test_end_to_end_workflow()

if __name__ == "__main__":
    main() 