#!/usr/bin/env python3
"""
Simple API Keys Test Script
Test all API connections for European football data collection (Windows compatible)
"""

import requests
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_football_data_api():
    """Test Football-Data.org API connection."""
    
    print("Testing Football-Data.org API...")
    
    api_key = os.getenv('FOOTBALL_API_KEY')
    
    if not api_key or api_key == "your_actual_football_api_key_here":
        print("ERROR: FOOTBALL_API_KEY not configured in .env file")
        return False
    
    try:
        headers = {
            'X-Auth-Token': api_key
        }
        
        # Test with Premier League data
        url = "https://api.football-data.org/v4/competitions/PL/standings"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            table = data.get('standings', [{}])[0].get('table', [])
            
            if table:
                print(f"SUCCESS: Football-Data.org API working!")
                print(f"Premier League standings retrieved: {len(table)} teams")
                print(f"Current leader: {table[0]['team']['name']}")
                return True
            else:
                print("WARNING: API responded but no standings data found")
                return False
                
        elif response.status_code == 403:
            print("ERROR: Football-Data.org API - Invalid API key or quota exceeded")
            return False
        elif response.status_code == 429:
            print("ERROR: Football-Data.org API - Rate limit exceeded")
            return False
        else:
            print(f"ERROR: Football-Data.org API error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Football-Data.org API connection error: {e}")
        return False


def test_odds_api():
    """Test The Odds API connection."""
    
    print("Testing The Odds API...")
    
    api_key = os.getenv('ODDS_API_KEY')
    
    if not api_key or api_key == "your_actual_odds_api_key_here":
        print("ERROR: ODDS_API_KEY not configured in .env file")
        return False
    
    try:
        # Test with soccer odds
        url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
        params = {
            'api_key': api_key,
            'regions': 'uk',
            'markets': 'h2h',
            'oddsFormat': 'decimal'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data:
                print(f"SUCCESS: The Odds API working!")
                print(f"Premier League odds retrieved: {len(data)} matches")
                
                if data:
                    match = data[0]
                    home_team = match.get('home_team', 'Unknown')
                    away_team = match.get('away_team', 'Unknown')
                    print(f"Sample match: {home_team} vs {away_team}")
                
                return True
            else:
                print("WARNING: Odds API responded but no data found")
                return False
                
        elif response.status_code == 401:
            print("ERROR: The Odds API - Invalid API key")
            return False
        elif response.status_code == 429:
            print("ERROR: The Odds API - Rate limit exceeded")
            return False
        else:
            print(f"ERROR: The Odds API error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: The Odds API connection error: {e}")
        return False


def test_weather_api():
    """Test OpenWeatherMap API connection."""
    
    print("Testing OpenWeatherMap API...")
    
    api_key = os.getenv('WEATHER_API_KEY')
    
    if not api_key or api_key == "your_actual_weather_api_key_here":
        print("ERROR: WEATHER_API_KEY not configured in .env file")
        return False
    
    try:
        # Test with London weather (for Premier League matches)
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': 'London,UK',
            'appid': api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            temp = data['main']['temp']
            condition = data['weather'][0]['description']
            
            print(f"SUCCESS: OpenWeatherMap API working!")
            print(f"London weather: {temp}°C, {condition}")
            return True
            
        elif response.status_code == 401:
            print("ERROR: OpenWeatherMap API - Invalid API key")
            return False
        elif response.status_code == 429:
            print("ERROR: OpenWeatherMap API - Rate limit exceeded")
            return False
        else:
            print(f"ERROR: OpenWeatherMap API error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: OpenWeatherMap API connection error: {e}")
        return False


def main():
    """Run all API tests."""
    
    print("EUROPEAN FOOTBALL API TESTING SYSTEM")
    print("=" * 60)
    print("Testing all API connections...")
    print("")
    
    # Track test results
    test_results = {
        'football_data': False,
        'odds_api': False,
        'weather_api': False
    }
    
    # Test each API
    test_results['football_data'] = test_football_data_api()
    print("")
    
    test_results['odds_api'] = test_odds_api()
    print("")
    
    test_results['weather_api'] = test_weather_api()
    print("")
    
    # Display results summary
    print("TEST RESULTS SUMMARY:")
    print("=" * 30)
    
    for api_name, result in test_results.items():
        status = "WORKING" if result else "FAILED"
        api_display = {
            'football_data': 'Football-Data.org',
            'odds_api': 'The Odds API',
            'weather_api': 'OpenWeatherMap'
        }
        print(f"{api_display[api_name]}: {status}")
    
    # Overall status
    total_working = sum(test_results.values())
    total_apis = len(test_results)
    
    print("")
    print(f"OVERALL STATUS: {total_working}/{total_apis} APIs working")
    
    if total_working == total_apis:
        print("ALL SYSTEMS GO! Ready for real-time monitoring!")
        print("Run: python run_realtime_monitor.py")
    elif total_working >= 1:
        print("Partial functionality available")
        print("Fix failing APIs for full functionality")
    else:
        print("No APIs working - check your .env file")
    
    print("")
    print("API USAGE LIMITS:")
    print("Football-Data.org: 10 requests per minute")
    print("The Odds API: 500 requests per month")
    print("OpenWeatherMap: 1,000 requests per day")
    
    return total_working == total_apis


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test error: {e}")
        sys.exit(1) 