# ⚽ Football Betting Prediction System - GUI User Guide

## 🎯 Overview

The Football Betting Prediction System now features a beautiful, modern GUI that provides an intuitive interface for viewing football matches, odds, predictions, and live data. The GUI integrates seamlessly with your database and real-time monitoring system.

## 🚀 Getting Started

### Quick Launch Options

#### Option 1: Use the Launcher (Recommended)
```bash
python launch_app.py
```
This opens a launcher window with options to:
- 🖥️ Launch GUI Interface only
- 📊 Start Data Monitoring only  
- 🚀 Launch Both (Recommended)
- ⏹️ Stop All processes

#### Option 2: Direct GUI Launch
```bash
python football_betting_gui.py
```

#### Option 3: Test GUI
```bash
python test_gui.py
```
Quick 10-second test to verify GUI functionality.

## 🖥️ GUI Features

### 🏆 Matches Tab
**Search and view football matches**
- **Search Bar**: Find matches by team name or competition
- **League Filter**: Filter by specific leagues (Premier League, La Liga, etc.)
- **Match List**: View match details including:
  - Date and time
  - Competition/League
  - Home vs Away teams
  - Match status (SCHEDULED, FINISHED, LIVE)
  - Final scores

### 🎯 Predictions Tab
**AI-powered betting predictions**
- **Generate Predictions**: Click to create AI predictions for upcoming matches
- **Prediction Display**: Shows for each match:
  - Home Win probability (%)
  - Draw probability (%)
  - Away Win probability (%)
  - Recommended bet type
  - Confidence level (High/Medium/Low)
- **Note**: Currently shows demo predictions; real ML model integration coming soon

### 💰 Odds Tab
**Live betting odds from multiple sources**
- **Real-time Odds**: Updated every 5 minutes from APIs
- **Multiple Bookmakers**: Compare odds across different sources
- **Odds Format**: Decimal odds for Home Win, Draw, Away Win
- **Last Updated**: Timestamp for each odds entry

### 📊 Standings Tab
**League standings and team statistics**
- **League Selector**: Choose from 5 major European leagues
- **Team Rankings**: Position, team name, games played
- **Statistics**: Wins, draws, losses, goals for/against, points
- **Live Updates**: Refreshed with latest match results

### 🔴 LIVE Tab
**Real-time match monitoring**
- **Live Matches**: Currently playing matches with live scores
- **Auto-Refresh**: Updates every 30 seconds (can be toggled)
- **Match Status**: IN_PLAY, HALFTIME, PAUSED indicators
- **Live Scores**: Real-time score updates

## 🎨 Design Features

### Modern Dark Theme
- **Color Scheme**: Professional dark theme with blue accents
- **Typography**: Clean, readable Arial fonts
- **Icons**: Emoji-based icons for intuitive navigation
- **Layout**: Responsive design that adapts to different window sizes

### User Experience
- **Tabbed Interface**: Easy navigation between different data views
- **Search & Filter**: Quick data discovery tools
- **Real-time Updates**: Live data refresh capabilities
- **Error Handling**: Graceful error messages and fallback options

## 🔧 Technical Requirements

### Dependencies
All dependencies are already installed from the main project setup:
- `tkinter` (built-in with Python)
- `sqlite3` (built-in with Python)
- `requests`
- `python-dotenv`

### Database Integration
- **Automatic Connection**: GUI connects to `data/football_betting.db`
- **Real-time Data**: Displays data collected by monitoring system
- **Safe Queries**: Proper SQL error handling and connection management

### API Integration
- **Environment Variables**: Uses existing API keys from `.env` file
- **Rate Limiting**: Respects API rate limits
- **Error Recovery**: Handles API failures gracefully

## 📊 Data Sources

The GUI displays data from:
- **Football-Data.org**: Match information, team data, standings
- **The Odds API**: Live betting odds from multiple bookmakers
- **Local Database**: Historical data and cached information

## 🛠️ Troubleshooting

### Common Issues

#### GUI Won't Start
```bash
# Check if database exists
ls data/football_betting.db

# Test database connection
python -c "import sqlite3; print('Database OK') if sqlite3.connect('data/football_betting.db') else print('Database Error')"
```

#### No Data Displayed
1. **Start Monitoring System**: The GUI shows data collected by the monitoring system
   ```bash
   python monitor_with_database.py
   ```
2. **Check API Keys**: Ensure `.env` file has valid API keys
3. **Refresh Data**: Click the "🔄 Refresh Data" button in the GUI

#### Styling Issues
- **Windows**: GUI uses native Windows theming
- **Dark Mode**: Automatically applies dark theme
- **Scaling**: GUI adapts to system DPI settings

### Error Messages

#### "Database not available"
- Ensure `data/football_betting.db` exists
- Run the monitoring system first to create the database

#### "Failed to refresh data"
- Check internet connection
- Verify API keys in `.env` file
- Ensure monitoring system has collected some data

## 🔄 Workflow Integration

### Recommended Usage Pattern

1. **Start Monitoring**: Begin data collection
   ```bash
   python monitor_with_database.py
   ```

2. **Launch GUI**: Open the interface
   ```bash
   python football_betting_gui.py
   ```

3. **Or Use Launcher**: One-click solution
   ```bash
   python launch_app.py
   ```

### Data Flow
```
APIs → Monitoring System → SQLite Database → GUI Display
```

## 🎯 Future Enhancements

### Planned Features
- **Real ML Predictions**: Integration with trained prediction models
- **Betting Simulator**: Test strategies with historical data
- **Advanced Analytics**: Team performance trends and statistics
- **Export Features**: Save data to CSV/Excel
- **User Settings**: Customizable themes and preferences
- **Push Notifications**: Alerts for important matches or odds changes

### Customization Options
- **Theme Colors**: Modify colors in `setup_window()` method
- **Data Refresh**: Adjust auto-refresh intervals
- **Display Columns**: Add/remove columns in tree views
- **API Sources**: Integrate additional data sources

## 📞 Support

If you encounter any issues:
1. Check this user guide
2. Verify all dependencies are installed
3. Ensure database and monitoring system are running
4. Check API keys and internet connection

The GUI provides a professional, user-friendly interface for your football betting prediction system, making data analysis and betting decisions easier and more intuitive! 🚀⚽ 