#!/usr/bin/env python3
"""
Enhanced Real-Time European Football Monitor with Database Storage
Collects data every 5 minutes and stores in SQLite database
"""

import asyncio
import time
import requests
import os
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

# Force load environment variables
load_dotenv(override=True)

class DatabaseEuropeanMonitor:
    """Real-time collector with database storage."""
    
    def __init__(self):
        self.football_api_key = os.getenv('FOOTBALL_API_KEY')
        self.odds_api_key = os.getenv('ODDS_API_KEY')
        self.is_running = False
        self.db_path = "data/football_betting.db"
        
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
        
        # Initialize database
        self.init_database()
        
        print("Enhanced European Football Monitor with Database initialized")
        print(f"Database: {self.db_path}")
        print(f"Monitoring {len(self.competitions)} competitions")
    
    def init_database(self):
        """Initialize SQLite database with tables."""
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY,
                name TEXT,
                competition TEXT,
                position INTEGER,
                points INTEGER,
                games_played INTEGER,
                wins INTEGER,
                draws INTEGER,
                losses INTEGER,
                goals_for INTEGER,
                goals_against INTEGER,
                last_updated TIMESTAMP,
                UNIQUE(name, competition)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY,
                api_id TEXT UNIQUE,
                competition TEXT,
                home_team TEXT,
                away_team TEXT,
                match_date TEXT,
                status TEXT,
                home_score INTEGER,
                away_score INTEGER,
                last_updated TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS odds (
                id INTEGER PRIMARY KEY,
                home_team TEXT,
                away_team TEXT,
                home_odds REAL,
                draw_odds REAL,
                away_odds REAL,
                bookmaker TEXT,
                last_updated TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_log (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP,
                collection_type TEXT,
                items_collected INTEGER,
                success BOOLEAN,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("Database initialized successfully")
    
    def log_collection(self, collection_type, items_collected, success, notes=""):
        """Log data collection activity."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO collection_log (timestamp, collection_type, items_collected, success, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now(), collection_type, items_collected, success, notes))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging collection: {e}")
    
    def save_standings(self, competition, standings):
        """Save standings data to database."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            teams_saved = 0
            
            for team_data in standings:
                team = team_data.get('team', {})
                
                cursor.execute('''
                    INSERT OR REPLACE INTO teams 
                    (name, competition, position, points, games_played, wins, draws, losses, 
                     goals_for, goals_against, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    team.get('name'),
                    competition,
                    team_data.get('position'),
                    team_data.get('points'),
                    team_data.get('playedGames'),
                    team_data.get('won'),
                    team_data.get('draw'),
                    team_data.get('lost'),
                    team_data.get('goalsFor'),
                    team_data.get('goalsAgainst'),
                    datetime.now()
                ))
                teams_saved += 1
            
            conn.commit()
            conn.close()
            
            print(f"  - Saved {teams_saved} teams to database")
            self.log_collection(f"standings_{competition}", teams_saved, True)
            
        except Exception as e:
            print(f"Error saving standings: {e}")
            self.log_collection(f"standings_{competition}", 0, False, str(e))
    
    def save_matches(self, competition, matches):
        """Save matches data to database."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            matches_saved = 0
            
            for match in matches:
                home_team = match.get('homeTeam', {}).get('name')
                away_team = match.get('awayTeam', {}).get('name')
                score = match.get('score', {}).get('fullTime', {})
                
                cursor.execute('''
                    INSERT OR REPLACE INTO matches 
                    (api_id, competition, home_team, away_team, match_date, status, 
                     home_score, away_score, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(match.get('id')),
                    competition,
                    home_team,
                    away_team,
                    match.get('utcDate'),
                    match.get('status'),
                    score.get('home'),
                    score.get('away'),
                    datetime.now()
                ))
                matches_saved += 1
            
            conn.commit()
            conn.close()
            
            print(f"  - Saved {matches_saved} matches to database")
            self.log_collection(f"matches_{competition}", matches_saved, True)
            
        except Exception as e:
            print(f"Error saving matches: {e}")
            self.log_collection(f"matches_{competition}", 0, False, str(e))
    
    def save_odds(self, odds_data):
        """Save odds data to database."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            odds_saved = 0
            
            for match in odds_data:
                home_team = match.get('home_team')
                away_team = match.get('away_team')
                
                # Save odds from each bookmaker
                for bookmaker in match.get('bookmakers', []):
                    markets = bookmaker.get('markets', [])
                    for market in markets:
                        if market.get('key') == 'h2h':
                            outcomes = market.get('outcomes', [])
                            home_odds = None
                            draw_odds = None
                            away_odds = None
                            
                            for outcome in outcomes:
                                if outcome.get('name') == home_team:
                                    home_odds = outcome.get('price')
                                elif outcome.get('name') == away_team:
                                    away_odds = outcome.get('price')
                                elif outcome.get('name') == 'Draw':
                                    draw_odds = outcome.get('price')
                            
                            cursor.execute('''
                                INSERT INTO odds 
                                (home_team, away_team, home_odds, draw_odds, away_odds, 
                                 bookmaker, last_updated)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                home_team,
                                away_team,
                                home_odds,
                                draw_odds,
                                away_odds,
                                bookmaker.get('title'),
                                datetime.now()
                            ))
                            odds_saved += 1
            
            conn.commit()
            conn.close()
            
            print(f"  - Saved {odds_saved} odds records to database")
            self.log_collection("odds", odds_saved, True)
            
        except Exception as e:
            print(f"Error saving odds: {e}")
            self.log_collection("odds", 0, False, str(e))
    
    def get_database_stats(self):
        """Get current database statistics."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM teams")
            teams_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM matches")
            matches_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM odds")
            odds_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM collection_log WHERE success = 1")
            successful_collections = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'teams': teams_count,
                'matches': matches_count,
                'odds': odds_count,
                'collections': successful_collections
            }
            
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {'teams': 0, 'matches': 0, 'odds': 0, 'collections': 0}
    
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
                if response.status_code != 429:  # Don't log rate limit errors
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
                if response.status_code != 429:  # Don't log rate limit errors
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
                if response.status_code != 429:  # Don't log rate limit errors
                    print(f"Error getting odds: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting odds: {e}")
            return []
    
    def update_all_data(self):
        """Update all football data and save to database."""
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting data update...")
        
        total_standings = 0
        total_matches = 0
        
        # Update standings and matches for each competition
        for comp_name, comp_code in self.competitions.items():
            try:
                print(f"Updating {comp_name}...")
                
                # Get and save standings
                standings = self.get_competition_standings(comp_code)
                if standings:
                    total_standings += len(standings)
                    print(f"  - {len(standings)} teams in standings")
                    self.save_standings(comp_name, standings)
                
                # Get and save matches
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
                    self.save_matches(comp_name, matches)
                
                # Small delay to respect API limits
                time.sleep(2)
                
            except Exception as e:
                print(f"Error updating {comp_name}: {e}")
                continue
        
        # Update and save odds
        try:
            print("Updating betting odds...")
            odds_data = self.get_odds_data()
            if odds_data:
                print(f"  - Got odds for {len(odds_data)} matches")
                self.save_odds(odds_data)
                
                # Show sample odds
                if odds_data:
                    sample = odds_data[0]
                    home_team = sample.get('home_team', 'Unknown')
                    away_team = sample.get('away_team', 'Unknown') 
                    print(f"  - Sample: {home_team} vs {away_team}")
        
        except Exception as e:
            print(f"Error updating odds: {e}")
        
        # Show database statistics
        stats = self.get_database_stats()
        print(f"DATABASE: {stats['teams']} teams, {stats['matches']} matches, {stats['odds']} odds, {stats['collections']} collections")
        
        print(f"Update complete: {total_standings} teams, {total_matches} matches")
        return total_standings > 0 or total_matches > 0
    
    async def start_monitoring(self):
        """Start the monitoring loop."""
        
        print("\nStarting 24/7 European Football Monitoring with Database Storage...")
        print("Data updates every 5 minutes and saves to database")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        self.is_running = True
        update_count = 0
        
        while self.is_running:
            try:
                update_count += 1
                print(f"\nUpdate #{update_count}")
                
                # Update all data
                success = self.update_all_data()
                
                if success:
                    print("SUCCESS: Data updated and saved to database")
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
        print("EUROPEAN FOOTBALL REAL-TIME MONITORING WITH DATABASE")
        print("=" * 70)
        
        # Initialize monitor
        monitor = DatabaseEuropeanMonitor()
        
        # Check API keys
        if not monitor.check_api_keys():
            print("ERROR: Cannot start without valid API keys")
            return
        
        # Show initial database stats
        stats = monitor.get_database_stats()
        print(f"Current Database: {stats['teams']} teams, {stats['matches']} matches, {stats['odds']} odds")
        
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