#!/usr/bin/env python3
"""
API Keys Test Script
Test all API connections for European football data collection
"""

import requests
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.settings import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def test_football_data_api():
    """Test Football-Data.org API connection."""
    
    logger.info("🏆 Testing Football-Data.org API...")
    
    try:
        headers = {
            'X-Auth-Token': settings.FOOTBALL_API_KEY
        }
        
        # Test with Premier League data
        url = "https://api.football-data.org/v4/competitions/PL/standings"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            table = data.get('standings', [{}])[0].get('table', [])
            
            if table:
                logger.info(f"✅ Football-Data.org API working!")
                logger.info(f"📊 Premier League standings retrieved: {len(table)} teams")
                logger.info(f"🏆 Current leader: {table[0]['team']['name']}")
                return True
            else:
                logger.warning("⚠️ API responded but no standings data found")
                return False
                
        elif response.status_code == 403:
            logger.error("❌ Football-Data.org API: Invalid API key or quota exceeded")
            return False
        elif response.status_code == 429:
            logger.error("❌ Football-Data.org API: Rate limit exceeded")
            return False
        else:
            logger.error(f"❌ Football-Data.org API error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Football-Data.org API connection error: {e}")
        return False


def test_odds_api():
    """Test The Odds API connection."""
    
    logger.info("💰 Testing The Odds API...")
    
    try:
        # Test with soccer odds
        url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
        params = {
            'api_key': settings.ODDS_API_KEY,
            'regions': 'uk',
            'markets': 'h2h',
            'oddsFormat': 'decimal'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data:
                logger.info(f"✅ The Odds API working!")
                logger.info(f"💰 Premier League odds retrieved: {len(data)} matches")
                
                if data:
                    match = data[0]
                    home_team = match.get('home_team', 'Unknown')
                    away_team = match.get('away_team', 'Unknown')
                    logger.info(f"📋 Sample match: {home_team} vs {away_team}")
                
                return True
            else:
                logger.warning("⚠️ Odds API responded but no data found")
                return False
                
        elif response.status_code == 401:
            logger.error("❌ The Odds API: Invalid API key")
            return False
        elif response.status_code == 429:
            logger.error("❌ The Odds API: Rate limit exceeded")
            return False
        else:
            logger.error(f"❌ The Odds API error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ The Odds API connection error: {e}")
        return False


def test_weather_api():
    """Test OpenWeatherMap API connection."""
    
    logger.info("🌤️ Testing OpenWeatherMap API...")
    
    try:
        # Test with London weather (for Premier League matches)
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': 'London,UK',
            'appid': settings.WEATHER_API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            temp = data['main']['temp']
            condition = data['weather'][0]['description']
            
            logger.info(f"✅ OpenWeatherMap API working!")
            logger.info(f"🌤️ London weather: {temp}°C, {condition}")
            return True
            
        elif response.status_code == 401:
            logger.error("❌ OpenWeatherMap API: Invalid API key")
            return False
        elif response.status_code == 429:
            logger.error("❌ OpenWeatherMap API: Rate limit exceeded")
            return False
        else:
            logger.error(f"❌ OpenWeatherMap API error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ OpenWeatherMap API connection error: {e}")
        return False


def display_api_usage_info():
    """Display API usage limits and recommendations."""
    
    logger.info("\n📊 API USAGE LIMITS & RECOMMENDATIONS:")
    logger.info("=" * 50)
    logger.info("🏆 Football-Data.org (Free Tier):")
    logger.info("   ⏱️  10 requests per minute")
    logger.info("   📅 Good for: Real-time match data, standings")
    logger.info("   🎯 Recommendation: Use for live matches & fixtures")
    logger.info("")
    logger.info("💰 The Odds API (Free Tier):")
    logger.info("   ⏱️  500 requests per month")
    logger.info("   📅 Good for: Betting odds, bookmaker data")
    logger.info("   🎯 Recommendation: Cache odds, update every 15 minutes")
    logger.info("")
    logger.info("🌤️ OpenWeatherMap (Free Tier):")
    logger.info("   ⏱️  1,000 requests per day")
    logger.info("   📅 Good for: Weather impact analysis")
    logger.info("   🎯 Recommendation: Get weather before matches")
    logger.info("=" * 50)


def main():
    """Run all API tests."""
    
    logger.info("🔑 EUROPEAN FOOTBALL API TESTING SYSTEM")
    logger.info("=" * 60)
    logger.info("🚀 Testing all API connections...")
    logger.info("")
    
    # Track test results
    test_results = {
        'football_data': False,
        'odds_api': False,
        'weather_api': False
    }
    
    # Test each API
    test_results['football_data'] = test_football_data_api()
    logger.info("")
    
    test_results['odds_api'] = test_odds_api()
    logger.info("")
    
    test_results['weather_api'] = test_weather_api()
    logger.info("")
    
    # Display results summary
    logger.info("📋 TEST RESULTS SUMMARY:")
    logger.info("=" * 30)
    
    for api_name, result in test_results.items():
        status = "✅ WORKING" if result else "❌ FAILED"
        api_display = {
            'football_data': 'Football-Data.org',
            'odds_api': 'The Odds API',
            'weather_api': 'OpenWeatherMap'
        }
        logger.info(f"{api_display[api_name]}: {status}")
    
    # Overall status
    total_working = sum(test_results.values())
    total_apis = len(test_results)
    
    logger.info("")
    logger.info(f"🎯 OVERALL STATUS: {total_working}/{total_apis} APIs working")
    
    if total_working == total_apis:
        logger.info("🎉 ALL SYSTEMS GO! Ready for real-time monitoring!")
        logger.info("💡 Run: python run_realtime_monitor.py")
    elif total_working >= 1:
        logger.info("⚠️  Partial functionality available")
        logger.info("💡 Fix failing APIs for full functionality")
    else:
        logger.info("❌ No APIs working - check your .env file")
    
    # Display usage info
    display_api_usage_info()
    
    return total_working == total_apis


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test error: {e}")
        sys.exit(1) 