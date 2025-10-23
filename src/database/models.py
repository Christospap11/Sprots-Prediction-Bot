class MatchStatistics(db.Model):
    """Enhanced match statistics for ML prediction"""
    __tablename__ = 'match_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    minute = db.Column(db.Integer)  # Match minute when stats were recorded
    
    # Possession and Control
    ball_possession = db.Column(db.Float)  # Percentage
    territorial_control = db.Column(db.Float)  # Percentage of time in opponent half
    
    # Shooting Statistics  
    shots_total = db.Column(db.Integer, default=0)
    shots_on_target = db.Column(db.Integer, default=0)
    shots_off_target = db.Column(db.Integer, default=0)
    shots_blocked = db.Column(db.Integer, default=0)
    shots_inside_box = db.Column(db.Integer, default=0)
    shots_outside_box = db.Column(db.Integer, default=0)
    
    # Attacking Statistics
    attacks = db.Column(db.Integer, default=0)
    dangerous_attacks = db.Column(db.Integer, default=0)
    corner_kicks = db.Column(db.Integer, default=0)
    free_kicks = db.Column(db.Integer, default=0)
    offsides = db.Column(db.Integer, default=0)
    
    # Passing Statistics
    passes_total = db.Column(db.Integer, default=0)
    passes_accurate = db.Column(db.Integer, default=0)
    passes_percentage = db.Column(db.Float)
    key_passes = db.Column(db.Integer, default=0)
    crosses_total = db.Column(db.Integer, default=0)
    crosses_accurate = db.Column(db.Integer, default=0)
    
    # Defensive Statistics
    tackles_total = db.Column(db.Integer, default=0)
    tackles_successful = db.Column(db.Integer, default=0)
    interceptions = db.Column(db.Integer, default=0)
    clearances = db.Column(db.Integer, default=0)
    blocks = db.Column(db.Integer, default=0)
    
    # Disciplinary
    fouls_committed = db.Column(db.Integer, default=0)
    fouls_suffered = db.Column(db.Integer, default=0)
    yellow_cards = db.Column(db.Integer, default=0)
    red_cards = db.Column(db.Integer, default=0)
    
    # Goalkeeping (when applicable)
    saves = db.Column(db.Integer, default=0)
    goals_conceded = db.Column(db.Integer, default=0)
    
    # Advanced Metrics
    xg = db.Column(db.Float)  # Expected Goals
    xga = db.Column(db.Float)  # Expected Goals Against
    xgot = db.Column(db.Float)  # Expected Goals on Target
    
    def __repr__(self):
        return f'<MatchStatistics {self.match_id}-{self.team_id} at {self.minute}min>'

class MatchEvents(db.Model):
    """Live match events for real-time analysis"""
    __tablename__ = 'match_events'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    player_id = db.Column(db.Integer, nullable=True)  # Can be null for team events
    
    event_type = db.Column(db.String(50), nullable=False)  # goal, card, substitution, etc.
    event_detail = db.Column(db.String(100))  # e.g., yellow_card, corner_kick, penalty
    minute = db.Column(db.Integer, nullable=False)
    stoppage_time = db.Column(db.Integer, default=0)
    
    # Event coordinates (when available)
    x_coordinate = db.Column(db.Float)  # Field position X (0-100)
    y_coordinate = db.Column(db.Float)  # Field position Y (0-100)
    
    # Event context
    is_home_team = db.Column(db.Boolean, nullable=False)
    match_clock = db.Column(db.String(10))  # e.g., "45:30"
    description = db.Column(db.Text)
    
    # Event impact (for ML)
    momentum_change = db.Column(db.Float)  # Calculated momentum impact
    xg_value = db.Column(db.Float)  # Expected goals value for shots
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<MatchEvent {self.event_type} at {self.minute}min>'

class PlayerStatistics(db.Model):
    """Enhanced player statistics for matches"""
    __tablename__ = 'player_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    player_id = db.Column(db.Integer, nullable=False)
    player_name = db.Column(db.String(100), nullable=False)
    
    # Basic info
    position = db.Column(db.String(20))
    shirt_number = db.Column(db.Integer)
    is_starter = db.Column(db.Boolean, default=False)
    minutes_played = db.Column(db.Integer, default=0)
    
    # Performance
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    shots_total = db.Column(db.Integer, default=0)
    shots_on_target = db.Column(db.Integer, default=0)
    
    # Passing
    passes_total = db.Column(db.Integer, default=0)
    passes_accurate = db.Column(db.Integer, default=0)
    key_passes = db.Column(db.Integer, default=0)
    crosses_total = db.Column(db.Integer, default=0)
    crosses_accurate = db.Column(db.Integer, default=0)
    
    # Defending
    tackles = db.Column(db.Integer, default=0)
    interceptions = db.Column(db.Integer, default=0)
    clearances = db.Column(db.Integer, default=0)
    blocks = db.Column(db.Integer, default=0)
    
    # Attacking
    dribbles_attempted = db.Column(db.Integer, default=0)
    dribbles_successful = db.Column(db.Integer, default=0)
    duels_won = db.Column(db.Integer, default=0)
    duels_total = db.Column(db.Integer, default=0)
    
    # Disciplinary
    fouls_committed = db.Column(db.Integer, default=0)
    fouls_drawn = db.Column(db.Integer, default=0)
    yellow_cards = db.Column(db.Integer, default=0)
    red_cards = db.Column(db.Integer, default=0)
    
    # Performance rating
    rating = db.Column(db.Float)  # Match rating (1-10)
    
    # Substitution info
    substituted_in = db.Column(db.Integer)  # Minute substituted in
    substituted_out = db.Column(db.Integer)  # Minute substituted out
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<PlayerStats {self.player_name} in match {self.match_id}>'

class TeamForm(db.Model):
    """Team form and momentum tracking"""
    __tablename__ = 'team_form'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    
    # Form metrics (calculated after each match)
    current_form_points = db.Column(db.Integer)  # Points from last 5 matches
    momentum_score = db.Column(db.Float)  # Weighted momentum calculation
    confidence_index = db.Column(db.Float)  # Based on recent performance
    
    # Attack metrics
    goals_per_game_l5 = db.Column(db.Float)  # Last 5 games
    xg_per_game_l5 = db.Column(db.Float)
    shots_per_game_l5 = db.Column(db.Float)
    big_chances_created_l5 = db.Column(db.Float)
    
    # Defense metrics  
    goals_conceded_per_game_l5 = db.Column(db.Float)
    xga_per_game_l5 = db.Column(db.Float)
    clean_sheets_l5 = db.Column(db.Integer)
    tackles_per_game_l5 = db.Column(db.Float)
    
    # Style metrics
    possession_avg_l5 = db.Column(db.Float)
    pass_accuracy_l5 = db.Column(db.Float)
    crosses_per_game_l5 = db.Column(db.Float)
    corners_per_game_l5 = db.Column(db.Float)
    
    # Discipline
    cards_per_game_l5 = db.Column(db.Float)
    fouls_per_game_l5 = db.Column(db.Float)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<TeamForm {self.team_id} - {self.momentum_score}>'

class MLFeatures(db.Model):
    """Pre-calculated ML features for faster prediction"""
    __tablename__ = 'ml_features'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    calculation_minute = db.Column(db.Integer)  # Live match minute, or -1 for pre-match
    
    # Team comparison features
    home_attack_strength = db.Column(db.Float)
    away_attack_strength = db.Column(db.Float)
    home_defense_strength = db.Column(db.Float)
    away_defense_strength = db.Column(db.Float)
    
    # Current match features (live)
    possession_ratio = db.Column(db.Float)  # Home possession / Away possession
    shots_ratio = db.Column(db.Float)
    xg_ratio = db.Column(db.Float)
    corners_ratio = db.Column(db.Float)
    attacks_ratio = db.Column(db.Float)
    
    # Momentum features
    home_momentum = db.Column(db.Float)
    away_momentum = db.Column(db.Float)
    pace_of_game = db.Column(db.Float)
    cards_intensity = db.Column(db.Float)
    
    # Context features
    home_advantage_factor = db.Column(db.Float)
    referee_strictness = db.Column(db.Float)
    weather_impact = db.Column(db.Float)
    crowd_factor = db.Column(db.Float)
    
    # Predicted probabilities
    home_win_prob = db.Column(db.Float)
    draw_prob = db.Column(db.Float)
    away_win_prob = db.Column(db.Float)
    over_2_5_prob = db.Column(db.Float)
    btts_prob = db.Column(db.Float)
    
    # Model confidence
    prediction_confidence = db.Column(db.Float)
    feature_importance_score = db.Column(db.Float)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<MLFeatures match {self.match_id} at {self.calculation_minute}min>' 