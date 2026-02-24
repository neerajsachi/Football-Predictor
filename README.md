# ⚽ Football Match & Transfer Predictor

AI-powered web application that predicts football match outcomes and transfer movements using Machine Learning.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![React](https://img.shields.io/badge/React-18-61dafb)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange)

## 🎯 Features

### Match Predictor
- 🏆 **Winner Prediction** - Home/Draw/Away with probabilities
- 📊 **Score Prediction** - Predicted final score
- ⚽ **Goal Scorers** - Likely players to score
- 📈 **Team Statistics** - Goals, shots, win rates, form analysis
- 🎨 **Real-time Predictions** - Instant results with animated UI

### Transfer Predictor
- 📤 **Transfers Out** - Players likely to leave
- 📥 **Transfers In** - Potential signings
- 💰 **Market Values** - Player valuations
- 📊 **Probability Analysis** - Transfer likelihood percentages

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python web framework)
- scikit-learn (RandomForest, GradientBoosting)
- Pandas (Data processing)
- NumPy (Numerical computations)

**Frontend:**
- React 18
- Vite (Build tool)
- Tailwind CSS (Styling)
- Axios (HTTP client)

**Machine Learning:**
- Random Forest Classifier
- Gradient Boosting Classifier
- Gradient Boosting Regressor
- Ensemble model approach

## 📊 Dataset

- **12,000+** historical matches
- **356,000+** player appearances
- **1,000+** clubs from top European leagues
- Features: goals, xGoals, shots, win rates, team form

**Note:** Large CSV files (>100MB) are not included in the repository due to GitHub size limits.

### Dataset Files Included:
- ✅ `clubs.csv` - Club information
- ✅ `club_games.csv` - Match statistics
- ✅ `games.csv` - Match results
- ✅ `players.csv` - Player information
- ✅ `transfers.csv` - Transfer history
- ✅ `competitions.csv` - Competition data
- ✅ `player_valuations.csv` - Market values

### Large Files (Download Required):
- ❌ `appearances.csv` (129 MB)
- ❌ `game_events.csv` (129 MB)
- ❌ `game_lineups.csv` (283 MB)

**To get the full dataset:**
1. Download from [Transfermarkt Dataset](https://www.kaggle.com/datasets/davidcariboo/player-scores) or contact the repository owner
2. Place files in `backend/data/dataset/`
3. The application will work with the included files, but some features may be limited

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Train the ML model:
```bash
python train.py
```
This will:
- Load 12,000+ matches from dataset
- Train 4 ML models (RandomForest + GradientBoosting)
- Save trained model to `models/match_model.pkl`
- Display accuracy metrics

5. Start the API server:
```bash
python app.py
```
Backend runs on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```
Frontend runs on `http://localhost:5173`

## 📖 Usage

1. Open browser to `http://localhost:5173`
2. **Match Predictor Tab:**
   - Enter home team (e.g., "Barcelona")
   - Enter away team (e.g., "Real Madrid")
   - Click "Predict Match"
   - View predicted score, winner, probabilities, and stats
3. **Transfer Predictor Tab:**
   - Enter club name (e.g., "Manchester United")
   - Click "Predict Transfers"
   - View predicted incoming and outgoing transfers

## 🏗️ Project Structure

```
predictor/
├── backend/
│   ├── src/
│   │   ├── models/
│   │   │   ├── match_model.py      # Match prediction ML model
│   │   │   └── transfer_model.py   # Transfer prediction logic
│   │   └── utils/
│   │       └── data_loader.py      # Data loading & processing
│   ├── data/
│   │   └── dataset/                # CSV data files
│   ├── models/
│   │   └── match_model.pkl         # Trained model (generated)
│   ├── app.py                      # FastAPI application
│   ├── train.py                    # Model training script
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Main React component
│   │   ├── index.css               # Tailwind styles
│   │   └── main.jsx                # React entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🤖 How It Works

### Match Prediction

1. **Data Collection**: Analyzes last 10 games for each team
2. **Feature Engineering**: Creates 14 features including:
   - Goals average (home/away)
   - Conceded average
   - Win rates (overall/home/away)
   - Attack/defense ratios
   - Form differences
3. **ML Models**: Ensemble of 4 models:
   - RandomForest Classifier (winner)
   - GradientBoosting Classifier (winner)
   - GradientBoosting Regressor (home goals)
   - GradientBoosting Regressor (away goals)
4. **Quality Adjustment**: Boosts stronger team's probability when playing away
5. **Output**: Winner, score, probabilities, top scorers

### Transfer Prediction

1. **Transfers Out**: Analyzes current squad based on:
   - Age (>32 = higher chance)
   - Contract expiry (<1 year = 50% chance)
   - Market value (high value = more interest)
2. **Destination Prediction**: Matches player quality to club prestige
3. **Transfers In**: Searches for players by position and market value
4. **Rivalry Rules**: Prevents transfers between rival clubs

## 📈 Model Performance

- **Result Accuracy**: ~65-70% (Win/Draw/Loss)
- **Score Accuracy**: ~20-25% (Exact score)
- **Average Goal Error**: ~0.8 goals

## 🐛 Known Limitations

- Predictions based on recent form (last 10 games only)
- Doesn't account for injuries, suspensions, or tactics
- Transfer predictions include random elements
- Home advantage may still be overweighted in some cases
- Dataset limited to European leagues

## 📝 Future Enhancements

- [ ] Add player injury data
- [ ] Include head-to-head history
- [ ] Real-time odds comparison
- [ ] Historical prediction accuracy tracking
- [ ] More leagues and competitions
- [ ] Mobile app version
- [ ] User accounts and prediction history

## 📄 License

MIT License

## 🙏 Acknowledgments

- Dataset from Transfermarkt
- scikit-learn for ML algorithms
- FastAPI for backend framework
- React and Tailwind for UI

---

⭐ Star this repo if you found it helpful!
