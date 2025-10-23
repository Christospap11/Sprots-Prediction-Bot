#!/usr/bin/env python3
"""
Quick API test with the user's keys
"""

import requests
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

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
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return False

if __name__ == "__main__":
    print("QUICK API TEST")
    print("=" * 30)
    
    football_ok = test_football_api()
    odds_ok = test_odds_api()
    
    print(f"\nResults:")
    print(f"Football API: {'✅' if football_ok else '❌'}")
    print(f"Odds API: {'✅' if odds_ok else '❌'}")
    
    if football_ok and odds_ok:
        print("\n🎉 READY TO START MONITORING!")
    elif football_ok or odds_ok:
        print("\n⚠️ Partial success - some features available")
    else:
        print("\n❌ Need to check API keys") 