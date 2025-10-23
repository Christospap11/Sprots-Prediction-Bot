# 🏈 Football Betting Prediction Bot

An AI-powered machine learning system for predicting football match outcomes and generating betting recommendations.

## 🎯 Project Overview

This project uses advanced machine learning algorithms to analyze historical football data, team statistics, player performance, and market sentiment to predict match outcomes and provide intelligent betting recommendations.

## 🏗️ Project Structure

```
Sports-Predict-Bot/
├── src/
│   ├── data/
│   │   ├── collectors/          # Data collection modules
│   │   ├── processors/          # Data processing and cleaning
│   │   └── storage/            # Database models and connections
│   ├── features/
│   │   ├── engineering/        # Feature engineering modules
│   │   └── selection/          # Feature selection algorithms
│   ├── models/
│   │   ├── training/           # Model training scripts
│   │   ├── prediction/         # Prediction engines
│   │   └── evaluation/         # Model evaluation metrics
│   ├── api/
│   │   ├── endpoints/          # FastAPI endpoints
│   │   └── middleware/         # API middleware
│   └── utils/                  # Utility functions
├── data/
│   ├── raw/                    # Raw collected data
│   ├── processed/              # Cleaned and processed data
│   └── models/                 # Trained model files
├── tests/                      # Unit and integration tests
├── notebooks/                  # Jupyter notebooks for analysis
├── config/                     # Configuration files
└── docs/                       # Documentation
```

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Sports-Predict-Bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Initialize database**
   ```bash
   python src/data/storage/init_db.py
   ```

## 📊 Features

- **Multi-source Data Collection**: Automated collection from various sports APIs and websites
- **Advanced Feature Engineering**: 50+ engineered features including team form, player stats, and market sentiment
- **Multiple ML Models**: Ensemble of Random Forest, XGBoost, and Neural Networks
- **Real-time Predictions**: Live match prediction with confidence scores
- **Betting Strategy**: Kelly Criterion-based bankroll management
- **Risk Management**: Built-in risk assessment and position sizing
- **Performance Tracking**: Comprehensive backtesting and live performance monitoring

## 🎯 Model Performance Targets

- **Match Outcome Accuracy**: >55%
- **ROI Target**: >10% annually
- **Sharpe Ratio**: >1.5
- **Maximum Drawdown**: <20%

## 📈 Data Sources

- Historical match results and statistics
- Team and player performance metrics
- Betting odds from multiple bookmakers
- Injury reports and team news
- Weather conditions
- Market sentiment indicators

## 🔧 Configuration

Key configuration options in `config/settings.py`:
- Data source APIs
- Model parameters
- Betting strategy settings
- Risk management rules

## 📝 Usage

### Basic Prediction
```python
from src.models.prediction import PredictionEngine

engine = PredictionEngine()
prediction = engine.predict_match("Team A", "Team B", match_date="2024-01-15")
print(f"Prediction: {prediction['outcome']} (Confidence: {prediction['confidence']:.2%})")
```

### Betting Recommendation
```python
from src.models.betting import BettingStrategy

strategy = BettingStrategy()
recommendation = strategy.get_betting_advice(prediction, current_odds)
print(f"Bet recommendation: {recommendation}")
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

## 📊 Performance Monitoring

Access the web dashboard at `http://localhost:8000` after starting the API server:
```bash
uvicorn src.api.main:app --reload
```

## ⚠️ Disclaimer

This software is for educational and research purposes only. Sports betting involves risk, and past performance does not guarantee future results. Always gamble responsibly and within your means.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For questions and support, please open an issue on GitHub. 