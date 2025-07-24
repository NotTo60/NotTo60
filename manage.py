#!/usr/bin/env python3
"""
Management CLI for Daily Trivia System
"""
import argparse
import sys
from datetime import datetime

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
    from src.core.database import TriviaDatabase
    print("[UPDATE-DB] Importing, updating, and exporting database...")
    db = TriviaDatabase()
    db.import_compressed_data()
    print("[UPDATE-DB] Imported and decrypted DB.")
    db.export_compressed_data()
    print("[UPDATE-DB] Exported and encrypted DB.")
    print("[UPDATE-DB] Done.")

def import_db():
    from src.core.database import TriviaDatabase
    print("[IMPORT-DB] Importing and decrypting database...")
    db = TriviaDatabase()
    db.import_compressed_data()
    print("[IMPORT-DB] Done.")

def export_db():
    from src.core.database import TriviaDatabase
    print("[EXPORT-DB] Exporting and encrypting database...")
    db = TriviaDatabase()
    db.export_compressed_data()
    print("[EXPORT-DB] Done.")

def new_trivia():
    from src.core.daily_trivia import generate_unique_trivia, load_trivia_data, save_trivia_data, get_utc_today
    trivia_data = load_trivia_data()
    today = get_utc_today()
    current_trivia = trivia_data.get("current")
    print("[NEW-TRIVIA] Generating new trivia (with retry if identical)...")
    new_trivia = None
    for attempt in range(3):
        new_trivia = generate_unique_trivia(current_trivia, max_tries=1)
        if not current_trivia or new_trivia['question'] != current_trivia.get('question'):
            break
        else:
            print(f"[NEW-TRIVIA] Trivia is identical to previous. Retrying... (attempt {attempt+1})")
    if not current_trivia or new_trivia['question'] != current_trivia.get('question'):
        new_trivia["date"] = today
        trivia_data["current"] = new_trivia
        save_trivia_data(trivia_data)
        print(f"[NEW-TRIVIA] Generated new trivia: {new_trivia['question']}")
    else:
        print("[NEW-TRIVIA] Trivia is still identical to previous after 3 attempts. Not updating.")

def new_fact():
    from src.core.daily_facts import get_todays_fact, load_daily_facts, save_daily_facts
    today = datetime.now().strftime("%d.%m.%Y")
    daily_facts_data = load_daily_facts()
    new_fact = get_todays_fact()
    prev_fact = daily_facts_data.get(today, {}).get('fact') if today in daily_facts_data else None
    if prev_fact and new_fact['fact'] == prev_fact:
        print("[NEW-FACT] Fact is identical to previous. Not updating.")
    else:
        daily_facts_data[today] = {"fact": new_fact["fact"], "timestamp": datetime.now().isoformat()}
        save_daily_facts(daily_facts_data)
        print(f"[NEW-FACT] Generated new fact: {new_fact['fact']}")

def process_answers():
    from src.core.process_answers import process_answers as process
    process()

def update_readme():
    from src.core.daily_trivia import load_trivia_data, load_leaderboard, update_readme
    trivia_data = load_trivia_data()
    leaderboard = load_leaderboard()
    update_readme(trivia_data, leaderboard)
    print("[UPDATE-README] README updated.")

def encrypt_db():
    from src.core.database import TriviaDatabase
    import os
    db = TriviaDatabase()
    compressed_path = "src/data/trivia_database.db.gz"
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
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 