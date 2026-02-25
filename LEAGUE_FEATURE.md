# League Table Predictor Feature

## Overview
New feature that predicts the final league table for the current season based on team performance and form.

## Files Created/Modified

### Backend
1. **`src/models/league_model.py`** (NEW)
   - `LeaguePredictor` class
   - `predict_league_table()` - Main prediction method
   - `_get_team_season_stats()` - Extracts current season stats
   - `_simulate_season()` - Projects remaining matches

2. **`app.py`** (MODIFIED)
   - Added `LeaguePredictor` import
   - Added `competitions_df` loading
   - Added `/leagues` GET endpoint - Returns list of available leagues
   - Added `/predict-league` POST endpoint - Returns predicted table
   - Added `LeagueRequest` model

### Frontend
3. **`frontend/src/App.jsx`** (MODIFIED)
   - Added league predictor state variables
   - Added `handleLeaguePredict()` function
   - Added "League Table" tab button
   - Added league table display with:
     - League selector dropdown
     - Full table with Position, Team, P, W, D, L, GF, GA, GD, Pts
     - Color coding for Champions League (top 4), Europa League (5-6), Relegation (bottom 3)
     - Zone indicators

## How It Works

### Prediction Algorithm
1. **Get Current Stats**: Analyzes last 10 games for each team in the league
2. **Calculate Metrics**:
   - Win rate, goals per game, conceded per game
   - Home/away performance splits
   - Recent form (last 5 games)
3. **Project Season**: 
   - Assumes 38 games total per season
   - Projects wins/draws/losses based on current rates
   - Projects goals for/against based on averages
4. **Calculate Points**: Wins × 3 + Draws
5. **Sort**: By points, then goal difference

### Features Included
- **25+ statistics** per team analyzed
- **Form-based projection** using recent performance
- **Home/away splits** for accuracy
- **Goal difference** calculation
- **Visual indicators** for European spots and relegation

## API Endpoints

### GET /leagues
Returns list of available leagues
```json
{
  "leagues": [
    {
      "id": "GB1",
      "name": "Premier League",
      "country": "England"
    },
    ...
  ]
}
```

### POST /predict-league
Request:
```json
{
  "league_id": "GB1"
}
```

Response:
```json
{
  "league_name": "Premier League",
  "table": [
    {
      "position": 1,
      "team_name": "Manchester City",
      "played": 38,
      "won": 28,
      "drawn": 6,
      "lost": 4,
      "goals_for": 89,
      "goals_against": 32,
      "goal_diff": 57,
      "points": 90
    },
    ...
  ]
}
```

## Available Leagues
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (England)
- 🇪🇸 LaLiga (Spain)
- 🇩🇪 Bundesliga (Germany)
- 🇮🇹 Serie A (Italy)
- 🇫🇷 Ligue 1 (France)
- 🇳🇱 Eredivisie (Netherlands)
- 🇵🇹 Liga Portugal (Portugal)
- 🇧🇪 Jupiler Pro League (Belgium)
- And more...

## Testing

Run the test script:
```bash
cd backend
source venv/bin/activate
python test_league.py
```

## Usage

1. Start backend: `cd backend && python app.py`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to "League Table" tab
4. Select a league from dropdown
5. Click "Predict League Table"
6. View predicted final standings

## Future Enhancements
- [ ] Add remaining fixtures display
- [ ] Show probability ranges for each position
- [ ] Include head-to-head tiebreakers
- [ ] Add historical accuracy tracking
- [ ] Support for different league formats (20 teams vs 18 teams)
- [ ] Monte Carlo simulation for multiple scenarios
