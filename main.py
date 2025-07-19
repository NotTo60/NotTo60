#!/usr/bin/env python3
"""
Main entry point for the Interactive AI-Powered Trivia System
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point"""
    print("🎯 Interactive AI-Powered Trivia System")
    print("=" * 50)
    print()
    print("Available commands:")
    print("  1. python main.py trivia     - Generate daily trivia")
    print("  2. python main.py process    - Process answers")
    print("  3. python main.py demo       - Run demo")
    print("  4. python main.py test       - Test all modules")
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <command>")
        return
    
    command = sys.argv[1].lower()
    
    if command == "trivia":
        from src.core.daily_trivia import main as trivia_main
        trivia_main()
    elif command == "process":
        from src.core.process_answers import main as process_main
        process_main()
    elif command == "demo":
        from scripts.demo import demo_trivia_generation
        demo_trivia_generation()
    elif command == "test":
        from scripts.demo import test_wow_facts_module, test_daily_facts_module
        test_wow_facts_module()
        test_daily_facts_module()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: trivia, process, demo, test")

if __name__ == "__main__":
    main() 