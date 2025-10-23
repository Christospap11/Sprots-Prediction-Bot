# 🚀 Quick Start Guide - European Football Real-Time Monitoring

## ⚡ Get Your Free API Keys (5 minutes each)

### 1. 🏆 Football-Data.org (ESSENTIAL for European leagues)
- **URL**: https://www.football-data.org/client/register
- **What you get**: Premier League, La Liga, Bundesliga, Serie A, Champions League data
- **Free tier**: 10 requests/minute (perfect for real-time updates)
- **Steps**:
  1. Fill out registration form
  2. Check your email for the API key
  3. Copy the key (format: `ff054c8a6b04477c9034d3b0122f6054`)

### 2. 💰 The Odds API (CRITICAL for betting)
- **URL**: https://the-odds-api.com/
- **What you get**: Live odds from 40+ European bookmakers
- **Free tier**: 500 requests/month
- **Steps**:
  1. Click "Get Free API Key"
  2. Sign up with email
  3. Go to dashboard and copy your API key

### 3. 🌤️ OpenWeatherMap (Weather impact analysis)
- **URL**: https://openweathermap.org/api
- **What you get**: Weather conditions affecting match performance
- **Free tier**: 1000 calls/day
- **Steps**:
  1. Click "Sign Up"
  2. After registration, go to "API Keys" tab
  3. Copy your default API key

---

## 🔧 Configure Your System

### Step 1: Update .env file
Open your `.env` file (in the project root) and replace these lines:

```env
FOOTBALL_API_KEY=your_actual_football_api_key_here
ODDS_API_KEY=your_actual_odds_api_key_here
WEATHER_API_KEY=your_actual_weather_api_key_here
```

**With your actual keys:**
```env
FOOTBALL_API_KEY=ff054c8a6b04477c9034d3b0122f6054
ODDS_API_KEY=6d44ac6772abb3f38da85e37460c1dbe
WEATHER_API_KEY=def456ghi789abc123
```

### Step 2: Test Your Setup
```bash
python simple_api_test.py
```

**Expected output when working:**
```
SUCCESS: Football-Data.org API working!
Premier League standings retrieved: 20 teams
Current leader: Liverpool

SUCCESS: The Odds API working!
Premier League odds retrieved: 5 matches

SUCCESS: OpenWeatherMap API working!
London weather: 15.2°C, cloudy

ALL SYSTEMS GO! Ready for real-time monitoring!
```

---

## 🎯 Start Real-Time Monitoring

### Option 1: Full 24/7 Monitoring
```bash
python run_realtime_monitor.py
```

**What this does:**
- ⚽ **Live matches**: Updates every 5 minutes
- 💰 **Betting odds**: Updates every 15 minutes  
- 📋 **Fixtures**: Updates every hour
- 📊 **Team stats**: Daily updates at 6 AM

### Option 2: Manual Data Collection
```bash
python src/data/collectors/football_api.py
```

---

## 📊 Monitored European Competitions

✅ **Premier League** (England)  
✅ **La Liga** (Spain)  
✅ **Bundesliga** (Germany)  
✅ **Serie A** (Italy)  
✅ **Ligue 1** (France)  
✅ **Champions League** (UEFA)  
✅ **Europa League** (UEFA)  
✅ **Championship** (England)  
✅ **Eredivisie** (Netherlands)  
✅ **Primeira Liga** (Portugal)  

---

## 🔄 How It Works

### Real-Time Updates:
1. **Live Match Monitoring**: System checks for live matches every minute
2. **Score Updates**: Instant notifications when goals are scored
3. **Odds Tracking**: Monitors betting odds changes from multiple bookmakers
4. **Database Storage**: All data is automatically stored in SQLite database
5. **Prediction Updates**: AI predictions are updated based on live match events

### API Usage Optimization:
- **Smart caching**: Reduces API calls by storing recent data
- **Rate limiting**: Respects API limits automatically
- **Error handling**: Continues working even if one API fails
- **Retry logic**: Automatically retries failed requests

---

## 🛑 Stop Monitoring

Press `Ctrl+C` in the terminal running the monitor to stop gracefully.

---

## 🆘 Troubleshooting

### Common Issues:

**"Invalid API key"**
- Double-check your API key in `.env` file
- Make sure there are no extra spaces
- Verify the key is active on the provider's website

**"Rate limit exceeded"**
- Wait a few minutes and try again
- Check your API usage on the provider's dashboard
- Consider upgrading to paid tier for higher limits

**"No data found"**
- Some competitions may be in off-season
- Try a different league or wait for active matches

### Getting Help:
- Check the logs in the `logs/` directory
- Run `python simple_api_test.py` to diagnose issues
- Verify your internet connection

---

## 🎉 Next Steps

Once monitoring is running:

1. **View Database**: Use SQLite browser to see collected data
2. **Jupyter Notebooks**: Explore data analysis notebooks
3. **Model Training**: Start building prediction models
4. **Betting Strategy**: Implement automated betting logic

**Happy betting! 🍀** 