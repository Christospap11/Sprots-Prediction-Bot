"""
Configuration settings for the Football Betting Prediction Bot.
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = "sqlite:///data/football_predictions.db"
    
    # API Keys
    football_api_key: str = ""
    odds_api_key: str = ""
    weather_api_key: str = ""
    
    # Enhanced Statistics API Keys
    api_football_key: str = ""
    sportmonks_api_key: str = ""
    sportdevs_api_key: str = ""
    soccersapi_key: str = ""
    
    # API URLs
    football_api_base_url: str = "https://api.football-data.org/v4"
    odds_api_base_url: str = "https://api.the-odds-api.com/v4"
    weather_api_base_url: str = "https://api.openweathermap.org/data/2.5"
    
    # Model Configuration
    model_retrain_interval_days: int = 7
    min_confidence_threshold: float = 0.6
    max_daily_bets: int = 5
    
    # Betting Configuration
    initial_bankroll: float = 1000.0
    max_bet_percentage: float = 0.05
    kelly_criterion_fraction: float = 0.25
    min_odds: float = 1.5
    max_odds: float = 5.0
    
    # Risk Management
    max_daily_loss_percentage: float = 0.10
    max_drawdown_percentage: float = 0.20
    
    # Application Settings
    debug: bool = True
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Data Collection Settings
    collect_data_interval_hours: int = 6
    leagues: str = "Premier League,La Liga,Bundesliga,Serie A,Ligue 1"
    
    @property
    def leagues_list(self) -> List[str]:
        """Get leagues as a list."""
        return [league.strip() for league in self.leagues.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


# Model parameters
MODEL_PARAMS = {
    "random_forest": {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "random_state": 42
    },
    "xgboost": {
        "n_estimators": 100,
        "max_depth": 6,
        "learning_rate": 0.1,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42
    },
    "neural_network": {
        "hidden_layers": [128, 64, 32],
        "dropout_rate": 0.3,
        "learning_rate": 0.001,
        "epochs": 100,
        "batch_size": 32
    }
}

# Feature engineering parameters
FEATURE_PARAMS = {
    "form_window": 5,  # Number of recent matches for form calculation
    "head_to_head_window": 10,  # Number of recent H2H matches
    "season_weight_decay": 0.9,  # Weight decay for older seasons
    "home_advantage_factor": 1.1,  # Home advantage multiplier
}

# Betting strategy parameters
BETTING_PARAMS = {
    "min_edge": 0.05,  # Minimum edge required to place bet
    "max_stake": 0.05,  # Maximum stake as fraction of bankroll
    "kelly_multiplier": 0.25,  # Conservative Kelly criterion multiplier
    "compound_growth": True,  # Whether to compound winnings
}

# Data validation parameters
DATA_VALIDATION = {
    "min_matches_for_prediction": 10,  # Minimum matches needed for team
    "max_missing_data_percentage": 0.1,  # Maximum missing data allowed
    "outlier_detection_threshold": 3.0,  # Standard deviations for outlier detection
}

# Statistics APIs Configuration
STATISTICS_APIS = {
    "api_football": {
        "base_url": "https://api-football-v1.p.rapidapi.com/v3",
        "api_key": os.getenv("API_FOOTBALL_KEY", "20f6ba49aa1c97a9d3d868caebcabe34"),
        "headers": {
            "X-RapidAPI-Key": os.getenv("API_FOOTBALL_KEY", "20f6ba49aa1c97a9d3d868caebcabe34"),
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        },
        "endpoints": {
            "statistics": "/fixtures/statistics",
            "live_statistics": "/fixtures/statistics",
            "events": "/fixtures/events",
            "lineups": "/fixtures/lineups",
            "player_stats": "/fixtures/players"
        },
        "rate_limit": "15_seconds",  # Updates every 15 seconds
        "features": ["live_stats", "detailed_stats", "player_stats", "events"]
    },
    "sportmonks": {
        "base_url": "https://api.sportmonks.com/v3/football",
        "api_key": os.getenv("SPORTMONKS_API_KEY", ""),
        "endpoints": {
            "match_stats": "/fixtures/{fixture_id}/statistics",
            "live_stats": "/livescores/inplay",
            "player_stats": "/fixtures/{fixture_id}/players",
            "team_stats": "/teams/{team_id}/statistics"
        },
        "rate_limit": "3000_per_hour",
        "features": ["extensive_stats", "xG_data", "historical_data"]
    },
    "sportdevs": {
        "base_url": "https://sportdevs.com/api/v1",
        "api_key": os.getenv("SPORTDEVS_API_KEY", ""),
        "websocket_url": "wss://sportdevs.com/ws",
        "endpoints": {
            "live_stats": "/football/matches/{match_id}/statistics",
            "incidents": "/football/matches/{match_id}/incidents",
            "lineups": "/football/matches/{match_id}/lineups"
        },
        "rate_limit": "200ms_response",
        "features": ["websockets", "ultra_fast", "multi_language"]
    },
    "soccersapi": {
        "base_url": "https://api.soccersapi.com/v2.2",
        "api_key": os.getenv("SOCCERSAPI_KEY", ""),
        "endpoints": {
            "live_scores": "/livescores",
            "statistics": "/matches/{match_id}/statistics",
            "events": "/matches/{match_id}/events"
        },
        "rate_limit": "1_second",
        "features": ["affordable", "800_leagues", "real_time"]
    }
}

# Statistics Collection Configuration
STATISTICS_CONFIG = {
    "collection_interval": 30,  # Collect every 30 seconds for live matches
    "historical_interval": 3600,  # Collect historical data every hour
    "match_events": [
        "goals", "cards", "corners", "shots", "possession", 
        "passes", "fouls", "offsides", "substitutions", "saves"
    ],
    "team_stats": [
        "ball_possession", "shots_total", "shots_on_target", "shots_off_target",
        "shots_blocked", "corner_kicks", "offsides", "fouls", "yellow_cards",
        "red_cards", "passes_total", "passes_accurate", "attacks", 
        "dangerous_attacks", "free_kicks", "goal_kicks", "throw_ins"
    ],
    "player_stats": [
        "goals", "assists", "shots", "passes", "tackles", "interceptions",
        "fouls_committed", "fouls_drawn", "yellow_cards", "red_cards",
        "minutes_played", "rating", "dribbles", "crosses"
    ],
    "advanced_stats": [
        "xG", "xGA", "xGOT", "xGC", "pressure_index", "sprint_distance",
        "top_speed", "heat_maps", "pass_networks", "defensive_actions"
    ]
}

# ML Model Enhancement Configuration
ML_FEATURES_CONFIG = {
    "real_time_features": [
        "current_possession_ratio", "shots_ratio", "corners_ratio",
        "fouls_ratio", "cards_momentum", "attack_pressure",
        "defensive_stability", "pace_of_game", "territorial_advantage"
    ],
    "match_context_features": [
        "home_advantage_factor", "crowd_impact", "weather_influence",
        "referee_strictness", "tactical_formation", "player_fatigue"
    ],
    "statistical_windows": {
        "short_term": 5,    # Last 5 minutes
        "medium_term": 15,  # Last 15 minutes  
        "long_term": 45     # Half or full match
    }
} 