#!/usr/bin/env python3
"""
Real-Time European Football Monitoring System
Run this script to start 24/7 live data collection for European football leagues
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data.collectors.realtime_european_collector import RealTimeEuropeanCollector
from src.utils.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


def check_api_keys():
    """Check if all required API keys are configured."""
    
    missing_keys = []
    
    # Check Football-Data.org API key
    if not settings.FOOTBALL_API_KEY or settings.FOOTBALL_API_KEY == "your_actual_football_api_key_here":
        missing_keys.append("FOOTBALL_API_KEY (Football-Data.org)")
    
    # Check The Odds API key
    if not settings.ODDS_API_KEY or settings.ODDS_API_KEY == "your_actual_odds_api_key_here":
        missing_keys.append("ODDS_API_KEY (The Odds API)")
    
    # Check Weather API key
    if not settings.WEATHER_API_KEY or settings.WEATHER_API_KEY == "your_actual_weather_api_key_here":
        missing_keys.append("WEATHER_API_KEY (OpenWeatherMap)")
    
    if missing_keys:
        logger.error("❌ Missing API keys:")
        for key in missing_keys:
            logger.error(f"   - {key}")
        logger.error("\n📋 Please update your .env file with actual API keys")
        logger.error("💡 Get free API keys from:")
        logger.error("   🏆 Football-Data.org: https://www.football-data.org/client/register")
        logger.error("   💰 The Odds API: https://the-odds-api.com/")
        logger.error("   🌤️ OpenWeatherMap: https://openweathermap.org/api")
        return False
    
    logger.info("✅ All API keys configured!")
    return True


def display_startup_info():
    """Display startup information and monitoring details."""
    
    logger.info("🏈⚽ EUROPEAN FOOTBALL REAL-TIME MONITORING SYSTEM")
    logger.info("=" * 60)
    logger.info("📊 MONITORING COMPETITIONS:")
    logger.info("   🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (England)")
    logger.info("   🇪🇸 La Liga (Spain)")
    logger.info("   🇩🇪 Bundesliga (Germany)")
    logger.info("   🇮🇹 Serie A (Italy)")
    logger.info("   🇫🇷 Ligue 1 (France)")
    logger.info("   🏆 UEFA Champions League")
    logger.info("   🏆 UEFA Europa League")
    logger.info("   🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Championship")
    logger.info("   🇳🇱 Eredivisie (Netherlands)")
    logger.info("   🇵🇹 Primeira Liga (Portugal)")
    logger.info("")
    logger.info("🔄 UPDATE FREQUENCIES:")
    logger.info("   🔥 Live matches: Every 5 minutes")
    logger.info("   💰 Betting odds: Every 15 minutes")
    logger.info("   📋 Fixtures: Every hour")
    logger.info("   📊 Team stats: Daily at 6:00 AM")
    logger.info("")
    logger.info("📈 FEATURES:")
    logger.info("   ⚽ Real-time score updates")
    logger.info("   💰 Live odds tracking")
    logger.info("   🎯 Automatic prediction updates")
    logger.info("   📊 Comprehensive statistics")
    logger.info("   💾 Database storage")
    logger.info("=" * 60)


async def main():
    """Main function to run the real-time monitoring system."""
    
    try:
        logger.info("🚀 Initializing European Football Real-Time Monitor...")
        
        # Check API keys
        if not check_api_keys():
            logger.error("❌ Cannot start without proper API keys configured")
            logger.info("\n💡 To configure API keys:")
            logger.info("1. Edit the .env file in your project directory")
            logger.info("2. Replace the placeholder values with your actual API keys")
            logger.info("3. Save the file and run this script again")
            return
        
        # Display startup information
        display_startup_info()
        
        # Initialize the collector
        collector = RealTimeEuropeanCollector()
        
        logger.info("🎯 Starting 24/7 monitoring...")
        logger.info("💡 Press Ctrl+C to stop monitoring")
        logger.info("")
        
        # Start the monitoring system
        await collector.start_24_7_monitoring()
        
    except KeyboardInterrupt:
        logger.info("\n👋 Monitoring stopped by user")
        if 'collector' in locals():
            collector.stop_monitoring()
        logger.info("✅ System shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error("💡 Check your .env file and API keys")
        sys.exit(1)


if __name__ == "__main__":
    try:
        # Run the monitoring system
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting system: {e}")
        sys.exit(1) 