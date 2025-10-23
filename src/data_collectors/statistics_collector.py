"""
Advanced Statistics Collector for Enhanced Football Prediction
Collects detailed team statistics, player stats, and live match events
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass

from config.settings import STATISTICS_APIS, STATISTICS_CONFIG, ML_FEATURES_CONFIG
from src.database.connection import get_db_connection
from src.database.models import (
    MatchStatistics, MatchEvents, PlayerStatistics, 
    TeamForm, MLFeatures, Matches, Teams
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MatchData:
    """Data structure for match statistics"""
    match_id: int
    fixture_id: str
    home_team_id: int
    away_team_id: int
    status: str
    minute: int = 0
    home_score: int = 0
    away_score: int = 0

class EnhancedStatisticsCollector:
    """Advanced statistics collector with multiple API support"""
    
    def __init__(self):
        self.db = get_db_connection()
        self.apis = STATISTICS_APIS
        self.config = STATISTICS_CONFIG
        self.session = None
        self.collection_active = False
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def start_collection(self):
        """Start continuous statistics collection"""
        logger.info("🔥 Starting Enhanced Statistics Collection System")
        self.collection_active = True
        
        while self.collection_active:
            try:
                # Get live matches
                live_matches = await self.get_live_matches()
                
                if live_matches:
                    logger.info(f"📊 Collecting stats for {len(live_matches)} live matches")
                    
                    # Collect statistics from multiple APIs in parallel
                    await asyncio.gather(
                        self.collect_api_football_stats(live_matches),
                        self.collect_sportmonks_stats(live_matches),
                        self.collect_live_events(live_matches),
                        return_exceptions=True
                    )
                    
                    # Update ML features
                    await self.update_ml_features(live_matches)
                    
                else:
                    logger.info("⏰ No live matches found")
                    
                # Collect historical data periodically
                await self.collect_historical_stats()
                
                # Wait before next collection cycle
                await asyncio.sleep(self.config["collection_interval"])
                
            except Exception as e:
                logger.error(f"Error in collection cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
                
    async def get_live_matches(self) -> List[MatchData]:
        """Get currently live matches from database"""
        try:
            query = """
            SELECT id, external_id, home_team_id, away_team_id, status,
                   home_score, away_score, match_time
            FROM matches 
            WHERE status IN ('live', 'in_progress', '1st_half', '2nd_half', 'halftime')
            AND date_time > datetime('now', '-3 hours')
            """
            
            rows = self.db.execute(query).fetchall()
            
            matches = []
            for row in rows:
                matches.append(MatchData(
                    match_id=row[0],
                    fixture_id=str(row[1]) if row[1] else str(row[0]),
                    home_team_id=row[2],
                    away_team_id=row[3],
                    status=row[4],
                    home_score=row[5] or 0,
                    away_score=row[6] or 0,
                    minute=self.parse_match_time(row[7])
                ))
                
            return matches
            
        except Exception as e:
            logger.error(f"Error getting live matches: {e}")
            return []
            
    def parse_match_time(self, match_time: str) -> int:
        """Parse match time string to minutes"""
        if not match_time:
            return 0
        try:
            if ":" in match_time:
                return int(match_time.split(":")[0])
            return int(match_time)
        except:
            return 0
            
    async def collect_api_football_stats(self, matches: List[MatchData]):
        """Collect statistics from API-Football"""
        api_config = self.apis["api_football"]
        headers = api_config["headers"]
        
        for match in matches:
            try:
                # Get match statistics
                stats_url = f"{api_config['base_url']}/fixtures/statistics"
                params = {"fixture": match.fixture_id}
                
                async with self.session.get(stats_url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.process_api_football_stats(match, data)
                        
                # Get live events
                events_url = f"{api_config['base_url']}/fixtures/events" 
                async with self.session.get(events_url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.process_match_events(match, data)
                        
                # Get player statistics
                players_url = f"{api_config['base_url']}/fixtures/players"
                async with self.session.get(players_url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.process_player_stats(match, data)
                        
                # Rate limiting
                await asyncio.sleep(4)  # API-Football rate limit
                
            except Exception as e:
                logger.error(f"Error collecting API-Football stats for match {match.match_id}: {e}")
                
    async def process_api_football_stats(self, match: MatchData, data: dict):
        """Process API-Football statistics data"""
        try:
            if not data.get("response"):
                return
                
            for team_stats in data["response"]:
                team_data = team_stats["team"]
                stats = team_stats["statistics"]
                
                # Determine if this is home or away team
                is_home = team_data["id"] == match.home_team_id
                team_id = match.home_team_id if is_home else match.away_team_id
                
                # Create statistics record
                match_stats = MatchStatistics()
                match_stats.match_id = match.match_id
                match_stats.team_id = team_id
                match_stats.minute = match.minute
                
                # Map API-Football stats to our model
                for stat in stats:
                    stat_type = stat["type"]
                    value = stat["value"]
                    
                    if value is None:
                        continue
                        
                    # Convert percentage strings to floats
                    if isinstance(value, str) and "%" in value:
                        value = float(value.replace("%", ""))
                    
                    # Map statistics
                    mapping = {
                        "Ball Possession": "ball_possession",
                        "Total Shots": "shots_total", 
                        "Shots on Goal": "shots_on_target",
                        "Shots off Goal": "shots_off_target",
                        "Blocked Shots": "shots_blocked",
                        "Shots insidebox": "shots_inside_box",
                        "Shots outsidebox": "shots_outside_box",
                        "Corner Kicks": "corner_kicks",
                        "Offsides": "offsides",
                        "Fouls": "fouls_committed",
                        "Yellow Cards": "yellow_cards",
                        "Red Cards": "red_cards",
                        "Goalkeeper Saves": "saves",
                        "Total passes": "passes_total",
                        "Passes accurate": "passes_accurate",
                        "Passes %": "passes_percentage"
                    }
                    
                    if stat_type in mapping:
                        setattr(match_stats, mapping[stat_type], value)
                        
                # Save to database
                self.db.merge(match_stats)
                self.db.commit()
                
        except Exception as e:
            logger.error(f"Error processing API-Football stats: {e}")
            
    async def process_match_events(self, match: MatchData, data: dict):
        """Process match events for real-time analysis"""
        try:
            if not data.get("response"):
                return
                
            for event in data["response"]:
                # Check if event already exists
                existing = self.db.query(MatchEvents).filter_by(
                    match_id=match.match_id,
                    minute=event["time"]["elapsed"] or 0,
                    event_type=event["type"],
                    team_id=event["team"]["id"]
                ).first()
                
                if existing:
                    continue
                    
                match_event = MatchEvents()
                match_event.match_id = match.match_id
                match_event.team_id = event["team"]["id"]
                match_event.event_type = event["type"]
                match_event.event_detail = event["detail"]
                match_event.minute = event["time"]["elapsed"] or 0
                match_event.stoppage_time = event["time"]["extra"] or 0
                match_event.is_home_team = event["team"]["id"] == match.home_team_id
                match_event.description = f"{event['type']}: {event['detail']}"
                
                # Add player info if available
                if event.get("player"):
                    match_event.player_id = event["player"]["id"]
                    
                # Calculate momentum change for key events
                match_event.momentum_change = self.calculate_momentum_change(
                    event["type"], event["detail"], match_event.is_home_team
                )
                
                self.db.add(match_event)
                
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error processing match events: {e}")
            
    def calculate_momentum_change(self, event_type: str, detail: str, is_home: bool) -> float:
        """Calculate momentum change based on event"""
        momentum_values = {
            "Goal": 3.0,
            "Red Card": -2.5,
            "Yellow Card": -0.5,
            "Penalty": 2.0,
            "Substitution": 0.2,
            "Corner": 0.3,
            "Free Kick": 0.4
        }
        
        base_value = momentum_values.get(event_type, 0.0)
        
        # Adjust for home/away
        if is_home:
            return base_value
        else:
            return -base_value if base_value > 0 else base_value
            
    async def process_player_stats(self, match: MatchData, data: dict):
        """Process player statistics"""
        try:
            if not data.get("response"):
                return
                
            for team_data in data["response"]:
                team_id = team_data["team"]["id"]
                
                for player_data in team_data["players"]:
                    player = player_data["player"]
                    stats = player_data["statistics"][0] if player_data["statistics"] else {}
                    
                    player_stats = PlayerStatistics()
                    player_stats.match_id = match.match_id
                    player_stats.team_id = team_id
                    player_stats.player_id = player["id"]
                    player_stats.player_name = player["name"]
                    player_stats.position = stats.get("games", {}).get("position")
                    player_stats.minutes_played = stats.get("games", {}).get("minutes", 0)
                    player_stats.is_starter = stats.get("games", {}).get("substitute", False) == False
                    player_stats.rating = float(stats.get("games", {}).get("rating", 0) or 0)
                    
                    # Goals and assists
                    goals_data = stats.get("goals", {})
                    player_stats.goals = goals_data.get("total", 0) or 0
                    player_stats.assists = goals_data.get("assists", 0) or 0
                    
                    # Shots
                    shots_data = stats.get("shots", {})
                    player_stats.shots_total = shots_data.get("total", 0) or 0
                    player_stats.shots_on_target = shots_data.get("on", 0) or 0
                    
                    # Passes
                    passes_data = stats.get("passes", {})
                    player_stats.passes_total = passes_data.get("total", 0) or 0
                    player_stats.passes_accurate = passes_data.get("accuracy", 0) or 0
                    player_stats.key_passes = passes_data.get("key", 0) or 0
                    
                    # Tackles and defending
                    tackles_data = stats.get("tackles", {})
                    player_stats.tackles = tackles_data.get("total", 0) or 0
                    player_stats.blocks = tackles_data.get("blocks", 0) or 0
                    player_stats.interceptions = tackles_data.get("interceptions", 0) or 0
                    
                    # Dribbles
                    dribbles_data = stats.get("dribbles", {})
                    player_stats.dribbles_attempted = dribbles_data.get("attempts", 0) or 0
                    player_stats.dribbles_successful = dribbles_data.get("success", 0) or 0
                    
                    # Duels
                    duels_data = stats.get("duels", {})
                    player_stats.duels_total = duels_data.get("total", 0) or 0
                    player_stats.duels_won = duels_data.get("won", 0) or 0
                    
                    # Fouls and cards
                    fouls_data = stats.get("fouls", {})
                    player_stats.fouls_committed = fouls_data.get("committed", 0) or 0
                    player_stats.fouls_drawn = fouls_data.get("drawn", 0) or 0
                    
                    cards_data = stats.get("cards", {})
                    player_stats.yellow_cards = cards_data.get("yellow", 0) or 0
                    player_stats.red_cards = cards_data.get("red", 0) or 0
                    
                    self.db.merge(player_stats)
                    
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error processing player stats: {e}")
            
    async def collect_sportmonks_stats(self, matches: List[MatchData]):
        """Collect advanced statistics from Sportmonks API"""
        # Implementation for Sportmonks API
        logger.info("📈 Collecting Sportmonks advanced statistics")
        # This would include xG, xGA, heat maps, etc.
        pass
        
    async def collect_live_events(self, matches: List[MatchData]):
        """Collect live events for momentum tracking"""
        logger.info("⚡ Collecting live events for momentum analysis")
        # Real-time event collection for momentum calculation
        pass
        
    async def update_ml_features(self, matches: List[MatchData]):
        """Update ML features for live prediction"""
        for match in matches:
            try:
                # Calculate current match ratios and features
                features = await self.calculate_live_features(match)
                
                ml_features = MLFeatures()
                ml_features.match_id = match.match_id
                ml_features.calculation_minute = match.minute
                
                # Set calculated features
                for key, value in features.items():
                    if hasattr(ml_features, key):
                        setattr(ml_features, key, value)
                        
                self.db.merge(ml_features)
                
            except Exception as e:
                logger.error(f"Error updating ML features for match {match.match_id}: {e}")
                
        self.db.commit()
        
    async def calculate_live_features(self, match: MatchData) -> Dict[str, float]:
        """Calculate live ML features for a match"""
        features = {}
        
        try:
            # Get latest statistics for both teams
            home_stats = self.get_latest_match_stats(match.match_id, match.home_team_id)
            away_stats = self.get_latest_match_stats(match.match_id, match.away_team_id)
            
            if home_stats and away_stats:
                # Calculate ratios
                features["possession_ratio"] = self.safe_divide(
                    home_stats.ball_possession, away_stats.ball_possession
                )
                features["shots_ratio"] = self.safe_divide(
                    home_stats.shots_total, away_stats.shots_total
                )
                features["corners_ratio"] = self.safe_divide(
                    home_stats.corner_kicks, away_stats.corner_kicks  
                )
                features["attacks_ratio"] = self.safe_divide(
                    home_stats.attacks, away_stats.attacks
                )
                
                # Calculate momentum
                home_momentum = self.calculate_team_momentum(match.match_id, match.home_team_id, match.minute)
                away_momentum = self.calculate_team_momentum(match.match_id, match.away_team_id, match.minute)
                
                features["home_momentum"] = home_momentum
                features["away_momentum"] = away_momentum
                features["pace_of_game"] = self.calculate_pace_of_game(match)
                
        except Exception as e:
            logger.error(f"Error calculating live features: {e}")
            
        return features
        
    def get_latest_match_stats(self, match_id: int, team_id: int) -> Optional[MatchStatistics]:
        """Get latest statistics for a team in a match"""
        try:
            return self.db.query(MatchStatistics).filter_by(
                match_id=match_id,
                team_id=team_id
            ).order_by(MatchStatistics.timestamp.desc()).first()
        except:
            return None
            
    def safe_divide(self, a: float, b: float) -> float:
        """Safe division to avoid division by zero"""
        if b == 0:
            return 1.0 if a == 0 else 10.0
        return a / b
        
    def calculate_team_momentum(self, match_id: int, team_id: int, current_minute: int) -> float:
        """Calculate team momentum based on recent events"""
        try:
            # Get recent events (last 10 minutes)
            recent_events = self.db.query(MatchEvents).filter(
                MatchEvents.match_id == match_id,
                MatchEvents.team_id == team_id,
                MatchEvents.minute >= current_minute - 10
            ).all()
            
            momentum = 0.0
            for event in recent_events:
                # Weight recent events more heavily
                time_weight = 1.0 - (current_minute - event.minute) / 10.0
                momentum += event.momentum_change * time_weight
                
            return max(-5.0, min(5.0, momentum))  # Clamp between -5 and 5
            
        except:
            return 0.0
            
    def calculate_pace_of_game(self, match: MatchData) -> float:
        """Calculate pace of game based on events frequency"""
        try:
            total_events = self.db.query(MatchEvents).filter_by(
                match_id=match.match_id
            ).count()
            
            if match.minute > 0:
                return total_events / match.minute
            return 0.0
            
        except:
            return 0.0
            
    async def collect_historical_stats(self):
        """Collect historical statistics for model training"""
        # Run every hour for completed matches
        current_time = datetime.utcnow()
        last_collection = current_time - timedelta(hours=1)
        
        # This would collect and process historical match data
        logger.info("📚 Collecting historical statistics for model training")
        
    def stop_collection(self):
        """Stop the collection process"""
        logger.info("🛑 Stopping statistics collection")
        self.collection_active = False

# Standalone function to run the collector
async def run_statistics_collector():
    """Run the enhanced statistics collector"""
    async with EnhancedStatisticsCollector() as collector:
        await collector.start_collection()

if __name__ == "__main__":
    asyncio.run(run_statistics_collector()) 