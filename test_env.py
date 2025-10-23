#!/usr/bin/env python3
"""
Create .env file with proper encoding
"""

# API keys from user
football_key = "ff054c8a6b04477c9034d3b0122f6054"
odds_key = "6d44ac6772abb3f38da85e37460c1dbe"

# Create .env file content
env_content = f"""# Football Betting Prediction Bot - Environment Configuration

# API Keys
FOOTBALL_API_KEY={football_key}
ODDS_API_KEY={odds_key}
WEATHER_API_KEY=placeholder

# Database
DATABASE_URL=sqlite:///data/football_betting.db

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
"""

# Write to .env file
with open('.env', 'w', encoding='utf-8') as f:
    f.write(env_content)

print("✅ .env file created successfully!")
print("Contents:")
print(env_content) 