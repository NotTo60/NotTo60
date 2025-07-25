#!/usr/bin/env python3
"""
Management CLI for Daily Trivia System
"""
import argparse
import sys
from datetime import datetime
from src.core.config import DB_COMPRESSED_PATH, DB_CHANGED_FLAG, README_PATH
import logging
import os
import tempfile
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def atomic_create_flag(flag_path):
    """Atomically create the .db_changed flag file."""
    dir_name = os.path.dirname(flag_path)
    with tempfile.NamedTemporaryFile(delete=False, dir=dir_name) as tf:
        tf.write(b"1")
        tempname = tf.name
    os.replace(tempname, flag_path)

def print_db():
    from src.core.database import TriviaDatabase
    print("[PRINT-DB] Decrypting and loading database...")
    db = TriviaDatabase()
    trivia = db.get_trivia_questions()
    facts = db.get_daily_facts()
    leaderboard = db.get_leaderboard()
    print("[PRINT-DB] Trivia Questions:")
    print(trivia)
    print("[PRINT-DB] Daily Facts:")
    print(facts)
    print("[PRINT-DB] Leaderboard:")
    print(leaderboard)
    print("[PRINT-DB] Done.")

def update_db():
    try:
        flag_path = DB_CHANGED_FLAG
        marker = "[UPDATE-DB] DB_CHANGED"
        github_output = os.environ.get('GITHUB_OUTPUT')
        changed = os.path.exists(flag_path)
        if changed:
            logging.info("[manage.py] [update_db] Database has changed and will be exported.")
            print(marker)
            if github_output:
                with open(github_output, 'a') as f:
                    f.write("db_changed=true\n")
            os.remove(flag_path)
        else:
            logging.info("[manage.py] [update_db] No update needed: all changes are already written by job logic.")
            if github_output:
                with open(github_output, 'a') as f:
                    f.write("db_changed=false\n")
        logging.info("[manage.py] [update_db] Done.")
    except Exception as e:
        logging.error("[manage.py] [update_db] Error updating DB: %s", e)

def import_db():
    from src.core.database import TriviaDatabase
    print("[IMPORT-DB] Importing and decrypting database...")
    db = TriviaDatabase()
    db.import_compressed_data()
    print("[IMPORT-DB] Done.")

def export_db():
    try:
        from src.core.database import TriviaDatabase
        print("[EXPORT-DB] Exporting and encrypting database...")
        db = TriviaDatabase()
        db.export_compressed_data()
        print("[EXPORT-DB] Exported and encrypted DB.")
        print("[EXPORT-DB] Done.")
    except Exception as e:
        logging.error("[manage.py] [export_db] Error exporting DB: %s", e)

def new_trivia():
    try:
        from src.core.daily_trivia import generate_unique_trivia, load_trivia_data, save_trivia_data, get_utc_today
        from datetime import datetime
        trivia_data = load_trivia_data()
        today = get_utc_today()
        current_trivia = trivia_data.get("current")
        logging.info(f"[DEBUG] Checking for existing trivia for today: {today}")
        if current_trivia:
            logging.info(f"[DEBUG] Current trivia timestamp: {current_trivia.get('timestamp', 'None')}")
        else:
            logging.info("[DEBUG] No current trivia found in DB.")
        def iso_to_ddmmyyyy(iso_str):
            try:
                return datetime.fromisoformat(iso_str).strftime("%d.%m.%Y")
            except Exception:
                return ""
        # Check if today's trivia already exists
        if current_trivia and iso_to_ddmmyyyy(current_trivia.get("timestamp", "")) == today:
            logging.info(f"[NEW-TRIVIA] Trivia for today ({today}) already exists:")
            logging.info(f"    {current_trivia['question']}")
            logging.info(f"    (category: {current_trivia.get('category', 'unknown')})")
            logging.info(f"    (added at {current_trivia.get('timestamp', 'unknown')})")
            return
        logging.info("[DEBUG] No trivia for today found, will generate new.")
        logging.info("[NEW-TRIVIA] Generating new trivia (with retry if identical)...")
        new_trivia = None
        for attempt in range(3):
            new_trivia = generate_unique_trivia(current_trivia, max_tries=1)
            if not current_trivia or new_trivia['question'] != current_trivia.get('question'):
                break
            else:
                logging.info(f"[NEW-TRIVIA] Trivia is identical to previous. Retrying... (attempt {attempt+1})")
        if not current_trivia or new_trivia['question'] != current_trivia.get('question'):
            new_trivia["date"] = today
            trivia_data["current"] = new_trivia
            save_trivia_data(trivia_data)
            # Mark DB as changed
            atomic_create_flag(DB_CHANGED_FLAG)
            logging.info(f"[NEW-TRIVIA] Generated new trivia: {new_trivia['question']}")
        else:
            logging.info("[NEW-TRIVIA] Trivia is still identical to previous after 3 attempts. Not updating.")
    except Exception as e:
        logging.error("[manage.py] [new_trivia] Error generating new trivia: %s", e)

def new_fact():
    try:
        from src.core.daily_facts import get_todays_fact, load_daily_facts, save_daily_facts
        today = datetime.now().strftime("%Y-%m-%d")  # Use YYYY-MM-DD to match schema
        daily_facts_data = load_daily_facts()
        new_fact = get_todays_fact()
        prev_fact = daily_facts_data.get(today, {}).get('fact') if today in daily_facts_data else None
        if prev_fact and new_fact['fact'] == prev_fact:
            logging.info("[NEW-FACT] Fact is identical to previous. Not updating.")
        else:
            daily_facts_data[today] = {"fact": new_fact["fact"], "timestamp": today}
            save_daily_facts(daily_facts_data)
            # Mark DB as changed
            atomic_create_flag(DB_CHANGED_FLAG)
            logging.info(f"[NEW-FACT] Generated new fact: {new_fact['fact']}")
    except Exception as e:
        logging.error("[manage.py] [new_fact] Error generating new fact: %s", e)

def process_answers():
    try:
        from src.core.process_answers import process_answers as process
        process()
        # Mark DB as changed
        atomic_create_flag(DB_CHANGED_FLAG)
    except Exception as e:
        logging.error("[manage.py] [process_answers] Error processing answers: %s", e)

def update_readme():
    try:
        from src.core.daily_trivia import load_trivia_data, load_leaderboard, update_readme
        trivia_data = load_trivia_data()
        leaderboard = load_leaderboard()
        update_readme(trivia_data, leaderboard)
        # Do not print '[UPDATE-README] README updated.' here; the real function already prints the correct message.
    except Exception as e:
        logging.error("[manage.py] [update_readme] Error updating README: %s", e)

def encrypt_db():
    try:
        from src.core.database import TriviaDatabase
        db = TriviaDatabase()
        compressed_path = DB_COMPRESSED_PATH
        prev_content = None
        if os.path.exists(compressed_path):
            with open(compressed_path, "rb") as f:
                prev_content = f.read()
        for attempt in range(2):
            db.export_compressed_data()
            with open(compressed_path, "rb") as f:
                new_content = f.read()
            if prev_content is None or new_content != prev_content:
                print("[ENCRYPT-DB] Database exported and encrypted to src/data/trivia_database.db.gz.")
                return
            else:
                print(f"[ENCRYPT-DB] Compressed DB identical to previous. Retrying... (attempt {attempt+1})")
        print("⚠️ [ENCRYPT-DB] Compressed DB is still identical after 2 attempts.")
    except Exception as e:
        logging.error("[manage.py] [encrypt_db] Error encrypting DB: %s", e)

def prune_db(trivia_days=90, facts_days=90, leaderboard_days=180):
    from src.core.database import TriviaDatabase
    db = TriviaDatabase()
    db.prune_trivia_questions(days=trivia_days)
    db.prune_daily_facts(days=facts_days)
    db.prune_leaderboard(min_last_answered_days=leaderboard_days)
    logging.info(f"[manage.py] [prune_db] Pruned trivia (> {trivia_days}d), facts (> {facts_days}d), leaderboard (> {leaderboard_days}d)")

def main():
    parser = argparse.ArgumentParser(description="Daily Trivia System Management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("import-db", help="Import and decrypt DB")
    subparsers.add_parser("export-db", help="Export and encrypt DB to compressed file")
    subparsers.add_parser("new-trivia", help="Create new daily trivia and validate")
    subparsers.add_parser("new-fact", help="Create new daily fact and validate")
    subparsers.add_parser("process-answers", help="Process answers")
    subparsers.add_parser("update-readme", help="Update README")
    subparsers.add_parser("encrypt-db", help="Update and encrypt DB")
    subparsers.add_parser("print-db", help="Print trivia, fact, and leaderboard with logs")
    subparsers.add_parser("update-db", help="Import, update, and export DB with logs")
    prune_parser = subparsers.add_parser("prune-db", help="Prune old trivia, facts, and leaderboard entries from the database.")
    prune_parser.add_argument("--trivia-days", type=int, default=90, help="Days to keep trivia questions (default: 90)")
    prune_parser.add_argument("--facts-days", type=int, default=90, help="Days to keep daily facts (default: 90)")
    prune_parser.add_argument("--leaderboard-days", type=int, default=180, help="Days to keep leaderboard entries since last answered (default: 180)")

    args = parser.parse_args()
    if args.command == "import-db":
        import_db()
    elif args.command == "export-db":
        export_db()
    elif args.command == "new-trivia":
        new_trivia()
    elif args.command == "new-fact":
        new_fact()
    elif args.command == "process-answers":
        process_answers()
    elif args.command == "update-readme":
        update_readme()
    elif args.command == "encrypt-db":
        encrypt_db()
    elif args.command == "print-db":
        print_db()
    elif args.command == "update-db":
        update_db()
    elif args.command == "prune-db":
        prune_db(trivia_days=args.trivia_days, facts_days=args.facts_days, leaderboard_days=args.leaderboard_days)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 