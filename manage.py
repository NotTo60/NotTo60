#!/usr/bin/env python3
"""
Management CLI for Daily Trivia System
"""
import argparse
import sys
from datetime import datetime

def import_db():
    from src.core.database import TriviaDatabase
    db = TriviaDatabase()
    db.import_compressed_data()
    print("[IMPORT-DB] Database import and decrypt complete.")

def new_trivia():
    from src.core.daily_trivia import generate_trivia_question, load_trivia_data, save_trivia_data, get_utc_today
    trivia_data = load_trivia_data()
    today = get_utc_today()
    new_trivia = generate_trivia_question()
    new_trivia["date"] = today
    if trivia_data.get("current") and new_trivia['question'] == trivia_data["current"].get('question'):
        print("[NEW-TRIVIA] Trivia is identical to previous. Not updating.")
    else:
        trivia_data["current"] = new_trivia
        save_trivia_data(trivia_data)
        print(f"[NEW-TRIVIA] Generated new trivia: {new_trivia['question']}")

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
    print("[ENCRYPT-DB] Update and encrypt DB (placeholder)")
    # TODO: Implement actual encrypt logic

def export_db():
    from src.core.database import TriviaDatabase
    db = TriviaDatabase()
    db.export_compressed_data()
    print("[EXPORT-DB] Database exported and encrypted to src/data/trivia_database.db.gz.")

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
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 