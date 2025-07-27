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
import json
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

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

def update_db(from_json=None):
    try:
        if from_json:
            from src.core.database import TriviaDatabase
            db = TriviaDatabase()
            for json_file in from_json:
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                        logging.info(f"[UPDATE-DB] Loaded data from {json_file}: {type(data)}")
                        # Detect and update trivia
                        if isinstance(data, dict) and "question" in data and "options" in data:
                            trivia_data = db.get_trivia_questions()
                            trivia_data[data["timestamp"]] = data
                            db.update_trivia_questions(trivia_data)
                            logging.info(f"[UPDATE-DB] Updated trivia in DB from {json_file}")
                        # Detect and update fact
                        elif isinstance(data, dict) and "fact" in data:
                            facts_data = db.get_daily_facts()
                            timestamp = data.get("timestamp") or data.get("date") or list(facts_data.keys())[0]
                            facts_data[timestamp] = data
                            db.update_daily_facts(facts_data)
                            logging.info(f"[UPDATE-DB] Updated fact in DB from {json_file}")
                        # Detect and update leaderboard/answers
                        elif isinstance(data, dict) and (
                            (data and any(isinstance(v, dict) and ("total_points" in v or "current_streak" in v or "total_answered" in v) for v in data.values()))
                            or ("total_points" in data or "current_streak" in data or "total_answered" in data)
                        ):
                            # If this is a single user, wrap in a dict
                            if "username" in data:
                                leaderboard = {data["username"]: data}
                            else:
                                leaderboard = data
                            db.update_leaderboard(leaderboard)
                            logging.info(f"[UPDATE-DB] Updated leaderboard in DB from {json_file}")
                        elif isinstance(data, dict) and not data:
                            logging.info(f"[UPDATE-DB] {json_file} is an empty dict, nothing to update.")
                        else:
                            logging.warning(f"[UPDATE-DB] Unknown data type in {json_file}, skipping.")
                except Exception as e:
                    logging.error(f"[UPDATE-DB] Failed to load {json_file}: {e}")
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

def new_trivia(json_out=None):
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
            if json_out:
                with open(json_out, 'w') as f:
                    json.dump(current_trivia, f)
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
            new_trivia["timestamp"] = new_trivia.get("timestamp") or datetime.now().isoformat()
            trivia_data["current"] = new_trivia
            save_trivia_data(trivia_data)
            if json_out:
                with open(json_out, 'w') as f:
                    json.dump(new_trivia, f)
            logging.info(f"[NEW-TRIVIA] Generated new trivia: {new_trivia['question']}")
        else:
            logging.info("[NEW-TRIVIA] Trivia is still identical to previous after 3 attempts. Not updating.")
            if json_out and current_trivia:
                with open(json_out, 'w') as f:
                    json.dump(current_trivia, f)
    except Exception as e:
        logging.error("[manage.py] [new_trivia] Error generating new trivia: %s", e)

def new_fact(json_out=None):
    try:
        from src.core.daily_facts import get_todays_fact, load_daily_facts, save_daily_facts
        today = datetime.now().strftime("%Y-%m-%d")
        daily_facts_data = load_daily_facts()
        new_fact = get_todays_fact()
        prev_fact = daily_facts_data.get(today, {}).get('fact') if today in daily_facts_data else None
        if prev_fact:
            logging.info(f"[NEW-FACT] Fact for today already exists. No update needed.")
            if json_out:
                with open(json_out, 'w') as f:
                    json.dump(new_fact, f)
        else:
            daily_facts_data[today] = {"fact": new_fact["fact"], "timestamp": today}
            save_daily_facts(daily_facts_data)
            if json_out:
                with open(json_out, 'w') as f:
                    json.dump(new_fact, f)
            logging.info(f"[NEW-FACT] Generated new fact: {new_fact['fact']}")
    except Exception as e:
        logging.error("[manage.py] [new_fact] Error generating new fact: %s", e)

def process_answers(json_out=None):
    try:
        from src.core.process_answers import process_answers as process, load_leaderboard
        process()
        if json_out:
            leaderboard = load_leaderboard()
            with open(json_out, 'w') as f:
                json.dump(leaderboard, f)
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
    new_trivia_parser = subparsers.add_parser("new-trivia", help="Create new daily trivia and validate")
    new_trivia_parser.add_argument('--json-out', type=str, help='Path to output JSON file')
    new_fact_parser = subparsers.add_parser("new-fact", help="Create new daily fact and validate")
    new_fact_parser.add_argument('--json-out', type=str, help='Path to output JSON file')
    process_answers_parser = subparsers.add_parser("process-answers", help="Process answers")
    process_answers_parser.add_argument('--json-out', type=str, help='Path to output JSON file')
    subparsers.add_parser("update-readme", help="Update README")
    subparsers.add_parser("encrypt-db", help="Update and encrypt DB")
    subparsers.add_parser("print-db", help="Print trivia, fact, and leaderboard with logs")
    update_db_parser = subparsers.add_parser("update-db", help="Import, update, and export DB with logs")
    update_db_parser.add_argument('--from-json', nargs='*', help='List of JSON files to update DB from')
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
        new_trivia(json_out=getattr(args, 'json_out', None))
    elif args.command == "new-fact":
        new_fact(json_out=getattr(args, 'json_out', None))
    elif args.command == "process-answers":
        process_answers(json_out=getattr(args, 'json_out', None))
    elif args.command == "update-readme":
        update_readme()
    elif args.command == "encrypt-db":
        encrypt_db()
    elif args.command == "print-db":
        print_db()
    elif args.command == "update-db":
        update_db(from_json=getattr(args, 'from_json', None))
    elif args.command == "prune-db":
        prune_db(trivia_days=args.trivia_days, facts_days=args.facts_days, leaderboard_days=args.leaderboard_days)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 