#!/usr/bin/env python3
"""
Simple Real-Time European Football Monitor
Works with current settings and avoids unicode issues
"""

import asyncio
import time
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Force load environment variables
load_dotenv(override=True)

class SimpleEuropeanMonitor:
    """Simple 24/7 real-time collector for European football data."""
    
    def __init__(self):
        self.football_api_key = os.getenv('FOOTBALL_API_KEY')
        self.odds_api_key = os.getenv('ODDS_API_KEY')
        self.is_running = False
        
        # European competitions mapping
        self.competitions = {
            'Premier League': 'PL',
            'La Liga': 'PD', 
            'Bundesliga': 'BL1',
            'Serie A': 'SA',
            'Ligue 1': 'FL1',
            'Champions League': 'CL',
            'Europa League': 'EL'
        }
        
        print("European Football Real-Time Monitor initialized")
        print(f"Monitoring {len(self.competitions)} competitions")
    
    def check_api_keys(self):
        """Check if API keys are configured."""
        
        if not self.football_api_key or self.football_api_key == "your_actual_football_api_key_here":
            print("ERROR: FOOTBALL_API_KEY not configured")
            return False
        
        if not self.odds_api_key or self.odds_api_key == "your_actual_odds_api_key_here":
            print("ERROR: ODDS_API_KEY not configured") 
            return False
        
        print("API keys configured successfully!")
        return True
    
    def get_competition_standings(self, comp_code):
        """Get standings for a competition."""
        
        try:
            headers = {'X-Auth-Token': self.football_api_key}
            url = f"https://api.football-data.org/v4/competitions/{comp_code}/standings"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('standings', [{}])[0].get('table', [])
            else:
                print(f"Error getting standings for {comp_code}: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting standings for {comp_code}: {e}")
            return []
    
    def get_competition_matches(self, comp_code):
        """Get matches for a competition."""
        
        try:
            headers = {'X-Auth-Token': self.football_api_key}
            
            # Get matches from yesterday to next week
            date_from = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            date_to = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            
            url = f"https://api.football-data.org/v4/competitions/{comp_code}/matches"
            params = {
                'dateFrom': date_from,
                'dateTo': date_to
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('matches', [])
            else:
                print(f"Error getting matches for {comp_code}: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting matches for {comp_code}: {e}")
            return []
    
    def get_odds_data(self):
        """Get odds data from The Odds API."""
        
        try:
            url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
            params = {
                'api_key': self.odds_api_key,
                'regions': 'uk',
                'markets': 'h2h',
                'oddsFormat': 'decimal'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting odds: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting odds: {e}")
            return []
    
    def update_all_data(self):
        """Update all football data."""
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting data update...")
        
        total_standings = 0
        total_matches = 0
        
        # Update standings and matches for each competition
        for comp_name, comp_code in self.competitions.items():
            try:
                print(f"Updating {comp_name}...")
                
                # Get standings
                standings = self.get_competition_standings(comp_code)
                if standings:
                    total_standings += len(standings)
                    print(f"  - {len(standings)} teams in standings")
                
                # Get matches
                matches = self.get_competition_matches(comp_code)
                if matches:
                    total_matches += len(matches)
                    
                    # Count live matches
                    live_matches = [m for m in matches if m.get('status') in ['IN_PLAY', 'PAUSED', 'HALFTIME']]
                    if live_matches:
                        print(f"  - {len(live_matches)} LIVE matches!")
                        for match in live_matches:
                            home = match.get('homeTeam', {}).get('name', 'Unknown')
                            away = match.get('awayTeam', {}).get('name', 'Unknown')
                            score = match.get('score', {})
                            home_score = score.get('fullTime', {}).get('home', 0)
                            away_score = score.get('fullTime', {}).get('away', 0)
                            print(f"    LIVE: {home} {home_score}-{away_score} {away}")
                    
                    print(f"  - {len(matches)} total matches")
                
                # Small delay to respect API limits
                time.sleep(2)
                
            except Exception as e:
                print(f"Error updating {comp_name}: {e}")
                continue
        
        # Update odds
        try:
            print("Updating betting odds...")
            odds_data = self.get_odds_data()
            if odds_data:
                print(f"  - Got odds for {len(odds_data)} matches")
                
                # Show sample odds
                if odds_data:
                    sample = odds_data[0]
                    home_team = sample.get('home_team', 'Unknown')
                    away_team = sample.get('away_team', 'Unknown') 
                    print(f"  - Sample: {home_team} vs {away_team}")
        
        except Exception as e:
            print(f"Error updating odds: {e}")
        
        print(f"Update complete: {total_standings} teams, {total_matches} matches")
        return total_standings > 0 or total_matches > 0
    
    async def start_monitoring(self):
        """Start the monitoring loop."""
        
        print("\nStarting 24/7 European Football Monitoring...")
        print("Press Ctrl+C to stop")
        print("=" * 50)
        
        self.is_running = True
        update_count = 0
        
        while self.is_running:
            try:
                update_count += 1
                print(f"\nUpdate #{update_count}")
                
                # Update all data
                success = self.update_all_data()
                
                if success:
                    print("SUCCESS: Data updated successfully")
                else:
                    print("WARNING: No data retrieved")
                
                # Show next update time
                next_update = datetime.now() + timedelta(minutes=5)
                print(f"Next update at: {next_update.strftime('%H:%M:%S')}")
                print("Waiting 5 minutes...")
                
                # Wait 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                print("Waiting 1 minute before retry...")
                await asyncio.sleep(60)
    
    def stop_monitoring(self):
        """Stop the monitoring."""
        print("\nStopping monitoring...")
        self.is_running = False


async def main():
    """Main function."""
    
    try:
        print("EUROPEAN FOOTBALL REAL-TIME MONITORING SYSTEM")
        print("=" * 60)
        
        # Initialize monitor
        monitor = SimpleEuropeanMonitor()
        
        # Check API keys
        if not monitor.check_api_keys():
            print("ERROR: Cannot start without valid API keys")
            return
        
        # Test initial connection
        print("\nTesting API connections...")
        test_standings = monitor.get_competition_standings('PL')
        test_odds = monitor.get_odds_data()
        
        if test_standings:
            print(f"SUCCESS: Football API working ({len(test_standings)} teams)")
        else:
            print("WARNING: Football API not responding")
        
        if test_odds:
            print(f"SUCCESS: Odds API working ({len(test_odds)} matches)")
        else:
            print("WARNING: Odds API not responding")
        
        if not test_standings and not test_odds:
            print("ERROR: No APIs working")
            return
        
        # Start monitoring
        await monitor.start_monitoring()
        
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
        if 'monitor' in locals():
            monitor.stop_monitoring()
    except Exception as e:
        print(f"Fatal error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}") 