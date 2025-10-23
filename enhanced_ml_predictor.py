"""
Enhanced ML Predictor with Advanced Statistics
Utilizes real-time team and player statistics for superior predictions
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import joblib
import warnings
warnings.filterwarnings('ignore')

from src.database.connection import get_db_connection
from src.database.models import (
    MatchStatistics, MatchEvents, PlayerStatistics, 
    TeamForm, MLFeatures, Matches, Teams
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMLPredictor:
    """Advanced ML predictor using comprehensive football statistics"""
    
    def __init__(self):
        self.db = get_db_connection()
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.is_trained = False
        
        # Model configurations
        self.model_configs = {
            'match_result': {
                'model': GradientBoostingClassifier(n_estimators=200, random_state=42),
                'target': 'result',  # 0: Away Win, 1: Draw, 2: Home Win
                'features': self._get_match_result_features()
            },
            'over_under': {
                'model': RandomForestClassifier(n_estimators=150, random_state=42),
                'target': 'over_2_5',  # 0: Under 2.5, 1: Over 2.5
                'features': self._get_over_under_features()
            },
            'btts': {
                'model': LogisticRegression(random_state=42),
                'target': 'btts',  # 0: No, 1: Yes
                'features': self._get_btts_features()
            },
            'correct_score': {
                'model': RandomForestClassifier(n_estimators=100, random_state=42),
                'target': 'score_category',  # Low/Medium/High scoring
                'features': self._get_score_features()
            }
        }
        
    def _get_match_result_features(self) -> List[str]:
        """Features for match result prediction"""
        return [
            # Team form and momentum
            'home_form_l5', 'away_form_l5', 'home_momentum', 'away_momentum',
            'home_confidence', 'away_confidence',
            
            # Head-to-head
            'h2h_home_wins', 'h2h_draws', 'h2h_away_wins', 'h2h_home_goals_avg',
            'h2h_away_goals_avg', 'h2h_home_advantage',
            
            # Attack vs Defense strength
            'home_attack_strength', 'away_attack_strength',
            'home_defense_strength', 'away_defense_strength',
            
            # Recent performance metrics
            'home_goals_per_game_l5', 'away_goals_per_game_l5',
            'home_goals_conceded_l5', 'away_goals_conceded_l5',
            'home_xg_l5', 'away_xg_l5', 'home_xga_l5', 'away_xga_l5',
            
            # Style and tactical metrics
            'home_possession_avg', 'away_possession_avg',
            'home_shots_per_game', 'away_shots_per_game',
            'home_corners_per_game', 'away_corners_per_game',
            'home_cards_per_game', 'away_cards_per_game',
            
            # Live match features (when available)
            'possession_ratio', 'shots_ratio', 'xg_ratio', 'corners_ratio',
            'attacks_ratio', 'pace_of_game', 'cards_intensity',
            
            # Context features
            'home_advantage_factor', 'referee_strictness', 'weather_impact',
            'crowd_factor', 'rest_days_diff', 'injury_impact'
        ]
        
    def _get_over_under_features(self) -> List[str]:
        """Features for over/under goals prediction"""
        return [
            # Goals scoring patterns
            'home_goals_per_game_l5', 'away_goals_per_game_l5',
            'home_goals_conceded_l5', 'away_goals_conceded_l5',
            'match_goals_avg_h2h', 'both_teams_scoring_tendency',
            
            # Expected goals
            'home_xg_l5', 'away_xg_l5', 'combined_xg_potential',
            
            # Playing style indicators
            'home_attack_intensity', 'away_attack_intensity',
            'home_defensive_stability', 'away_defensive_stability',
            'combined_pace_factor', 'match_importance_factor',
            
            # Live indicators
            'current_goals_trend', 'time_remaining_factor',
            'substitution_impact', 'momentum_shift_indicator'
        ]
        
    def _get_btts_features(self) -> List[str]:
        """Features for both teams to score prediction"""
        return [
            # Scoring consistency
            'home_btts_rate_l10', 'away_btts_rate_l10',
            'home_clean_sheet_rate', 'away_clean_sheet_rate',
            'home_fails_to_score_rate', 'away_fails_to_score_rate',
            
            # Attack vs defense matchups
            'home_attack_vs_away_defense', 'away_attack_vs_home_defense',
            'attack_defense_balance', 'defensive_vulnerability',
            
            # Match context
            'match_importance', 'tactical_setup_btts_friendly',
            'historical_btts_rate_h2h', 'recent_form_btts_indicator'
        ]
        
    def _get_score_features(self) -> List[str]:
        """Features for score category prediction"""
        return [
            # Combined attacking potential
            'total_xg_potential', 'total_shots_expected',
            'combined_attack_strength', 'combined_defense_weakness',
            
            # Match dynamics
            'expected_game_pace', 'tactical_openness',
            'set_piece_potential', 'counter_attack_potential',
            
            # Historical patterns
            'teams_high_scoring_rate', 'teams_low_scoring_rate',
            'venue_scoring_pattern', 'weather_scoring_impact'
        ]
        
    def prepare_training_data(self, start_date: str = None, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """Prepare training data with enhanced statistics"""
        logger.info("🔄 Preparing training data with enhanced statistics...")
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
        # Get completed matches with comprehensive data
        training_data = {}
        
        for prediction_type, config in self.model_configs.items():
            logger.info(f"📊 Preparing data for {prediction_type}...")
            
            # Get match data with all features
            df = self._build_feature_matrix(
                start_date=start_date,
                end_date=end_date,
                prediction_type=prediction_type
            )
            
            if not df.empty:
                training_data[prediction_type] = df
                logger.info(f"✅ Prepared {len(df)} samples for {prediction_type}")
            else:
                logger.warning(f"⚠️ No data found for {prediction_type}")
                
        return training_data
        
    def _build_feature_matrix(self, start_date: str, end_date: str, prediction_type: str) -> pd.DataFrame:
        """Build comprehensive feature matrix for training"""
        try:
            # Base query for completed matches
            query = """
            SELECT m.id, m.home_team_id, m.away_team_id, m.date_time,
                   m.home_score, m.away_score, m.result,
                   ht.name as home_team, at.name as away_team
            FROM matches m
            JOIN teams ht ON m.home_team_id = ht.id  
            JOIN teams at ON m.away_team_id = at.id
            WHERE m.status = 'finished'
            AND m.date_time BETWEEN ? AND ?
            AND m.home_score IS NOT NULL
            AND m.away_score IS NOT NULL
            ORDER BY m.date_time
            """
            
            matches_df = pd.read_sql_query(query, self.db, params=[start_date, end_date])
            
            if matches_df.empty:
                return pd.DataFrame()
                
            # Build features for each match
            features_list = []
            
            for _, match in matches_df.iterrows():
                match_features = self._calculate_match_features(
                    match_id=match['id'],
                    home_team_id=match['home_team_id'],
                    away_team_id=match['away_team_id'],
                    match_date=match['date_time'],
                    prediction_type=prediction_type
                )
                
                if match_features:
                    # Add target variables
                    match_features.update(self._calculate_targets(match))
                    features_list.append(match_features)
                    
            if not features_list:
                return pd.DataFrame()
                
            features_df = pd.DataFrame(features_list)
            
            # Fill missing values with appropriate defaults
            features_df = self._fill_missing_values(features_df)
            
            return features_df
            
        except Exception as e:
            logger.error(f"Error building feature matrix: {e}")
            return pd.DataFrame()
            
    def _calculate_match_features(self, match_id: int, home_team_id: int, 
                                away_team_id: int, match_date: str, 
                                prediction_type: str) -> Dict:
        """Calculate comprehensive features for a match"""
        features = {}
        
        try:
            # Team form features
            features.update(self._get_team_form_features(
                home_team_id, away_team_id, match_date
            ))
            
            # Head-to-head features
            features.update(self._get_h2h_features(
                home_team_id, away_team_id, match_date
            ))
            
            # Team strength features
            features.update(self._get_team_strength_features(
                home_team_id, away_team_id, match_date
            ))
            
            # Statistical features from recent matches
            features.update(self._get_statistical_features(
                home_team_id, away_team_id, match_date
            ))
            
            # Context features
            features.update(self._get_context_features(
                match_id, match_date
            ))
            
            # Add match identifiers
            features['match_id'] = match_id
            features['home_team_id'] = home_team_id
            features['away_team_id'] = away_team_id
            
            return features
            
        except Exception as e:
            logger.error(f"Error calculating match features: {e}")
            return {}
            
    def _get_team_form_features(self, home_team_id: int, away_team_id: int, 
                              match_date: str) -> Dict:
        """Get team form and momentum features"""
        features = {}
        
        try:
            # Get recent form for both teams (last 5 matches)
            for team_type, team_id in [('home', home_team_id), ('away', away_team_id)]:
                form_data = self._get_recent_form(team_id, match_date, num_matches=5)
                
                features[f'{team_type}_form_l5'] = form_data['points']
                features[f'{team_type}_momentum'] = form_data['momentum']
                features[f'{team_type}_confidence'] = form_data['confidence']
                features[f'{team_type}_goals_per_game_l5'] = form_data['goals_per_game']
                features[f'{team_type}_goals_conceded_l5'] = form_data['goals_conceded_per_game']
                features[f'{team_type}_xg_l5'] = form_data.get('xg_per_game', 0)
                features[f'{team_type}_xga_l5'] = form_data.get('xga_per_game', 0)
                
        except Exception as e:
            logger.error(f"Error getting team form features: {e}")
            
        return features
        
    def _get_recent_form(self, team_id: int, match_date: str, num_matches: int = 5) -> Dict:
        """Get recent form statistics for a team"""
        try:
            query = """
            SELECT home_score, away_score, result, date_time,
                   CASE WHEN home_team_id = ? THEN 1 ELSE 0 END as is_home
            FROM matches 
            WHERE (home_team_id = ? OR away_team_id = ?)
            AND status = 'finished'
            AND date_time < ?
            ORDER BY date_time DESC
            LIMIT ?
            """
            
            df = pd.read_sql_query(query, self.db, 
                                 params=[team_id, team_id, team_id, match_date, num_matches])
            
            if df.empty:
                return {'points': 0, 'momentum': 0, 'confidence': 0, 
                       'goals_per_game': 0, 'goals_conceded_per_game': 0}
                
            # Calculate form metrics
            points = 0
            goals_for = 0
            goals_against = 0
            
            for _, row in df.iterrows():
                if row['is_home']:
                    team_goals = row['home_score']
                    opponent_goals = row['away_score']
                else:
                    team_goals = row['away_score'] 
                    opponent_goals = row['home_score']
                    
                goals_for += team_goals
                goals_against += opponent_goals
                
                # Calculate points
                if team_goals > opponent_goals:
                    points += 3
                elif team_goals == opponent_goals:
                    points += 1
                    
            # Calculate momentum (weighted by recency)
            momentum = self._calculate_momentum(df, team_id)
            
            # Calculate confidence (based on performance vs expected)
            confidence = min(100, max(0, (points / (num_matches * 3)) * 100))
            
            return {
                'points': points,
                'momentum': momentum,
                'confidence': confidence,
                'goals_per_game': goals_for / max(len(df), 1),
                'goals_conceded_per_game': goals_against / max(len(df), 1)
            }
            
        except Exception as e:
            logger.error(f"Error getting recent form: {e}")
            return {'points': 0, 'momentum': 0, 'confidence': 0,
                   'goals_per_game': 0, 'goals_conceded_per_game': 0}
            
    def _calculate_momentum(self, df: pd.DataFrame, team_id: int) -> float:
        """Calculate team momentum based on recent results"""
        if df.empty:
            return 0.0
            
        momentum = 0.0
        
        for i, row in df.iterrows():
            # More weight for recent matches
            weight = 1.0 - (i * 0.15)
            
            # Determine result value
            if row['is_home']:
                team_goals = row['home_score']
                opponent_goals = row['away_score']
            else:
                team_goals = row['away_score']
                opponent_goals = row['home_score']
                
            if team_goals > opponent_goals:
                result_value = 3.0
            elif team_goals == opponent_goals:
                result_value = 1.0
            else:
                result_value = -1.0
                
            momentum += result_value * weight
            
        return momentum / len(df)
        
    def _get_h2h_features(self, home_team_id: int, away_team_id: int, 
                         match_date: str) -> Dict:
        """Get head-to-head features between teams"""
        features = {}
        
        try:
            # Get last 10 H2H matches
            query = """
            SELECT home_score, away_score, date_time,
                   CASE WHEN home_team_id = ? THEN 1 ELSE 0 END as home_is_target
            FROM matches
            WHERE ((home_team_id = ? AND away_team_id = ?) 
                   OR (home_team_id = ? AND away_team_id = ?))
            AND status = 'finished'
            AND date_time < ?
            ORDER BY date_time DESC
            LIMIT 10
            """
            
            df = pd.read_sql_query(query, self.db, params=[
                home_team_id, home_team_id, away_team_id, 
                away_team_id, home_team_id, match_date
            ])
            
            if df.empty:
                # Default values if no H2H history
                features.update({
                    'h2h_home_wins': 0, 'h2h_draws': 0, 'h2h_away_wins': 0,
                    'h2h_home_goals_avg': 1.5, 'h2h_away_goals_avg': 1.5,
                    'h2h_home_advantage': 0.5
                })
            else:
                home_wins = away_wins = draws = 0
                home_goals_total = away_goals_total = 0
                
                for _, row in df.iterrows():
                    if row['home_is_target']:
                        home_goals = row['home_score']
                        away_goals = row['away_score']
                    else:
                        home_goals = row['away_score']
                        away_goals = row['home_score']
                        
                    home_goals_total += home_goals
                    away_goals_total += away_goals
                    
                    if home_goals > away_goals:
                        home_wins += 1
                    elif away_goals > home_goals:
                        away_wins += 1
                    else:
                        draws += 1
                        
                total_matches = len(df)
                features.update({
                    'h2h_home_wins': home_wins / total_matches,
                    'h2h_draws': draws / total_matches,
                    'h2h_away_wins': away_wins / total_matches,
                    'h2h_home_goals_avg': home_goals_total / total_matches,
                    'h2h_away_goals_avg': away_goals_total / total_matches,
                    'h2h_home_advantage': (home_wins + 0.5 * draws) / total_matches
                })
                
        except Exception as e:
            logger.error(f"Error getting H2H features: {e}")
            features.update({
                'h2h_home_wins': 0.33, 'h2h_draws': 0.33, 'h2h_away_wins': 0.33,
                'h2h_home_goals_avg': 1.5, 'h2h_away_goals_avg': 1.5,
                'h2h_home_advantage': 0.5
            })
            
        return features
        
    def _get_team_strength_features(self, home_team_id: int, away_team_id: int,
                                  match_date: str) -> Dict:
        """Calculate team strength ratings"""
        features = {}
        
        try:
            # This would calculate ELO-style ratings or strength indices
            # For now, using simplified calculations
            
            for team_type, team_id in [('home', home_team_id), ('away', away_team_id)]:
                # Get recent performance metrics
                recent_stats = self._get_team_recent_stats(team_id, match_date)
                
                features[f'{team_type}_attack_strength'] = recent_stats['attack_rating']
                features[f'{team_type}_defense_strength'] = recent_stats['defense_rating']
                
        except Exception as e:
            logger.error(f"Error getting team strength features: {e}")
            
        return features
        
    def _get_team_recent_stats(self, team_id: int, match_date: str) -> Dict:
        """Get recent team statistics"""
        # Simplified implementation - would be expanded with actual statistics
        return {
            'attack_rating': 50.0,  # 0-100 scale
            'defense_rating': 50.0  # 0-100 scale
        }
        
    def _get_statistical_features(self, home_team_id: int, away_team_id: int,
                                match_date: str) -> Dict:
        """Get detailed statistical features from recent matches"""
        features = {}
        
        # This would pull from MatchStatistics table for detailed stats
        # Implementation would include possession, shots, corners, etc.
        
        return features
        
    def _get_context_features(self, match_id: int, match_date: str) -> Dict:
        """Get contextual features for the match"""
        features = {
            'home_advantage_factor': 1.3,  # Standard home advantage
            'referee_strictness': 0.5,     # Neutral referee
            'weather_impact': 0.0,         # No weather impact
            'crowd_factor': 1.0,           # Standard crowd
            'rest_days_diff': 0,           # No rest difference
            'injury_impact': 0.0           # No major injuries
        }
        
        return features
        
    def _calculate_targets(self, match: pd.Series) -> Dict:
        """Calculate target variables for training"""
        home_score = match['home_score']
        away_score = match['away_score']
        total_goals = home_score + away_score
        
        # Match result (0: Away win, 1: Draw, 2: Home win)
        if home_score > away_score:
            result = 2
        elif away_score > home_score:
            result = 0
        else:
            result = 1
            
        return {
            'result': result,
            'over_2_5': 1 if total_goals > 2.5 else 0,
            'btts': 1 if home_score > 0 and away_score > 0 else 0,
            'score_category': 2 if total_goals >= 4 else (1 if total_goals >= 2 else 0),
            'total_goals': total_goals
        }
        
    def _fill_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values with appropriate defaults"""
        # Numeric columns - fill with median or logical defaults
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if 'ratio' in col or 'factor' in col:
                df[col] = df[col].fillna(1.0)
            elif 'rate' in col or 'percentage' in col:
                df[col] = df[col].fillna(0.5)
            else:
                df[col] = df[col].fillna(df[col].median())
                
        return df
        
    def train_models(self, training_data: Dict[str, pd.DataFrame]):
        """Train all prediction models"""
        logger.info("🔥 Training enhanced ML models...")
        
        for prediction_type, df in training_data.items():
            if df.empty:
                logger.warning(f"⚠️ No data for {prediction_type}, skipping...")
                continue
                
            logger.info(f"🎯 Training {prediction_type} model...")
            
            config = self.model_configs[prediction_type]
            feature_cols = config['features']
            target_col = config['target']
            
            # Prepare features and target
            available_features = [col for col in feature_cols if col in df.columns]
            
            if not available_features:
                logger.warning(f"⚠️ No features available for {prediction_type}")
                continue
                
            X = df[available_features]
            y = df[target_col]
            
            # Handle missing values
            X = X.fillna(X.median())
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train model
            model = config['model']
            model.fit(X_scaled, y)
            
            # Store model and scaler
            self.models[prediction_type] = model
            self.scalers[prediction_type] = scaler
            self.feature_columns = available_features
            
            # Calculate accuracy
            predictions = model.predict(X_scaled)
            accuracy = accuracy_score(y, predictions)
            
            logger.info(f"✅ {prediction_type} model trained - Accuracy: {accuracy:.3f}")
            
        self.is_trained = True
        logger.info("🎉 All models trained successfully!")
        
    def predict_match(self, home_team_id: int, away_team_id: int, 
                     match_date: str = None) -> Dict:
        """Make comprehensive match predictions"""
        if not self.is_trained:
            logger.error("❌ Models not trained yet!")
            return {}
            
        if not match_date:
            match_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        logger.info(f"🔮 Making predictions for match {home_team_id} vs {away_team_id}")
        
        try:
            # Calculate features for the match
            features = self._calculate_match_features(
                match_id=0,  # Unknown for prediction
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                match_date=match_date,
                prediction_type='match_result'
            )
            
            predictions = {}
            
            # Make predictions with each model
            for prediction_type, model in self.models.items():
                if prediction_type not in self.scalers:
                    continue
                    
                try:
                    # Prepare features
                    available_features = [col for col in self.feature_columns if col in features]
                    X = np.array([[features.get(col, 0) for col in available_features]])
                    
                    # Scale features
                    X_scaled = self.scalers[prediction_type].transform(X)
                    
                    # Make prediction
                    prediction = model.predict(X_scaled)[0]
                    probabilities = model.predict_proba(X_scaled)[0] if hasattr(model, 'predict_proba') else None
                    
                    predictions[prediction_type] = {
                        'prediction': prediction,
                        'probabilities': probabilities.tolist() if probabilities is not None else None,
                        'confidence': float(np.max(probabilities)) if probabilities is not None else 0.5
                    }
                    
                except Exception as e:
                    logger.error(f"Error making {prediction_type} prediction: {e}")
                    
            return predictions
            
        except Exception as e:
            logger.error(f"Error making match predictions: {e}")
            return {}
            
    def save_models(self, model_dir: str = "models/enhanced"):
        """Save trained models and scalers"""
        import os
        os.makedirs(model_dir, exist_ok=True)
        
        for prediction_type in self.models:
            model_path = os.path.join(model_dir, f"{prediction_type}_model.pkl")
            scaler_path = os.path.join(model_dir, f"{prediction_type}_scaler.pkl")
            
            joblib.dump(self.models[prediction_type], model_path)
            joblib.dump(self.scalers[prediction_type], scaler_path)
            
        # Save feature columns
        features_path = os.path.join(model_dir, "feature_columns.pkl")
        joblib.dump(self.feature_columns, features_path)
        
        logger.info(f"✅ Models saved to {model_dir}")
        
    def load_models(self, model_dir: str = "models/enhanced"):
        """Load trained models and scalers"""
        import os
        
        try:
            # Load feature columns
            features_path = os.path.join(model_dir, "feature_columns.pkl")
            self.feature_columns = joblib.load(features_path)
            
            # Load models and scalers
            for prediction_type in self.model_configs:
                model_path = os.path.join(model_dir, f"{prediction_type}_model.pkl")
                scaler_path = os.path.join(model_dir, f"{prediction_type}_scaler.pkl")
                
                if os.path.exists(model_path) and os.path.exists(scaler_path):
                    self.models[prediction_type] = joblib.load(model_path)
                    self.scalers[prediction_type] = joblib.load(scaler_path)
                    
            self.is_trained = len(self.models) > 0
            logger.info(f"✅ Models loaded from {model_dir}")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")

# Usage example
if __name__ == "__main__":
    predictor = EnhancedMLPredictor()
    
    # Train models with historical data
    training_data = predictor.prepare_training_data()
    predictor.train_models(training_data)
    
    # Save models
    predictor.save_models()
    
    # Make a prediction
    predictions = predictor.predict_match(
        home_team_id=1,
        away_team_id=2
    )
    
    print("🔮 Enhanced Predictions:", predictions) 