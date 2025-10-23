#!/usr/bin/env python3
"""
Final API test with forced .env loading
"""

import requests
import os
from dotenv import load_dotenv

# Force load from .env file, overriding system environment
load_dotenv(override=True)

def test_football_api():
    """Test Football-Data.org API"""
    print("Testing Football-Data.org API...")
    
    api_key = os.getenv('FOOTBALL_API_KEY')
    print(f"Using key: {api_key[:10]}...")
    
    headers = {'X-Auth-Token': api_key}
    url = "https://api.football-data.org/v4/competitions/PL/standings"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            table = data.get('standings', [{}])[0].get('table', [])
            if table:
                print(f"SUCCESS! Got {len(table)} teams")
                print(f"Top team: {table[0]['team']['name']}")
                return True
        elif response.status_code == 403:
            print("ERROR: API key quota exceeded (daily limit reached)")
        elif response.status_code == 400:
            print("ERROR: Invalid API key format")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return False

def test_odds_api():
    """Test The Odds API"""
    print("\nTesting The Odds API...")
    
    api_key = os.getenv('ODDS_API_KEY')
    print(f"Using key: {api_key[:10]}...")
    
    url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
    params = {
        'api_key': api_key,
        'regions': 'uk',
        'markets': 'h2h',
        'oddsFormat': 'decimal'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS! Got odds for {len(data)} matches")
            if data:
                match = data[0]
                print(f"Sample: {match.get('home_team')} vs {match.get('away_team')}")
            return True
        elif response.status_code == 401:
            print("ERROR: Invalid API key")
        elif response.status_code == 429:
            print("ERROR: Rate limit exceeded")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 FINAL API TEST")
    print("=" * 40)
    
    # Show what keys we're using
    football_key = os.getenv('FOOTBALL_API_KEY')
    odds_key = os.getenv('ODDS_API_KEY')
    
    print(f"Football API Key: {football_key}")
    print(f"Odds API Key: {odds_key}")
    print("")
    
    football_ok = test_football_api()
    odds_ok = test_odds_api()
    
    print(f"\n🎯 RESULTS:")
    print(f"Football API: {'✅ WORKING' if football_ok else '❌ FAILED'}")
    print(f"Odds API: {'✅ WORKING' if odds_ok else '❌ FAILED'}")
    
    if football_ok and odds_ok:
        print("\n🎉 BOTH APIs WORKING! READY TO START MONITORING!")
    elif football_ok or odds_ok:
        print("\n⚠️ PARTIAL SUCCESS - Some features available")
        if football_ok:
            print("✅ Can collect match data, standings, fixtures")
        if odds_ok:
            print("✅ Can collect betting odds")
    else:
        print("\n❌ API ISSUES DETECTED")
        print("🔍 POSSIBLE CAUSES:")
        print("- Keys might be invalid or expired")
        print("- Daily quota might be exceeded")
        print("- Internet connection issues") 