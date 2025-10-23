#!/usr/bin/env python3
"""
Debug environment loading
"""

import os
from dotenv import load_dotenv

print("Before loading .env:")
print(f"FOOTBALL_API_KEY: {os.getenv('FOOTBALL_API_KEY', 'NOT SET')}")
print(f"ODDS_API_KEY: {os.getenv('ODDS_API_KEY', 'NOT SET')}")

print("\nLoading .env...")
load_dotenv()

print("\nAfter loading .env:")
football_key = os.getenv('FOOTBALL_API_KEY')
odds_key = os.getenv('ODDS_API_KEY')

print(f"FOOTBALL_API_KEY: {football_key}")
print(f"ODDS_API_KEY: {odds_key}")

print(f"\nFootball key first 10 chars: {football_key[:10] if football_key else 'None'}")
print(f"Odds key first 10 chars: {odds_key[:10] if odds_key else 'None'}")

# Check .env file contents
print("\n.env file contents:")
try:
    with open('.env', 'r') as f:
        print(f.read())
except Exception as e:
    print(f"Error reading .env: {e}") 