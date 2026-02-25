from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
from src.models.match_model import MatchPredictor
from src.utils.data_loader import get_team_stats
from src.models.transfer_model import TransferPredictor

app = FastAPI()

# Production-ready CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and data
predictor = MatchPredictor()
transfer_predictor = TransferPredictor()
clubs_df = pd.read_csv('data/dataset/clubs.csv', encoding='utf-8')
club_games_df = pd.read_csv('data/dataset/club_games.csv', encoding='utf-8')
games_df = pd.read_csv('data/dataset/games.csv', encoding='utf-8')
appearances_df = pd.read_csv('data/dataset/appearances.csv', encoding='utf-8')
players_df = pd.read_csv('data/dataset/players.csv', encoding='utf-8')
transfers_df = pd.read_csv('data/dataset/transfers.csv', encoding='utf-8')

# Parse dates
games_df['date'] = pd.to_datetime(games_df['date'])

# Parse contract expiry dates
players_df['contract_expiration_date'] = pd.to_datetime(players_df['contract_expiration_date'], errors='coerce')

club_map = dict(zip(clubs_df['club_id'], clubs_df['name']))
player_map = dict(zip(players_df['player_id'], players_df['name']))

if not predictor.load_model('models/match_model.pkl'):
    print("No trained model found. Run 'python train.py' first.")

class MatchRequest(BaseModel):
    home_team: str
    away_team: str

class TransferRequest(BaseModel):
    club_name: str

@app.get("/")
def read_root():
    return {"message": "Football Match Predictor API", "model_trained": predictor.is_trained}

@app.get("/clubs")
def get_clubs():
    """Get list of all clubs for autocomplete"""
    clubs_list = sorted(list(club_map.values()))
    return {"clubs": clubs_list}

@app.post("/predict-match")
async def predict_match(request: MatchRequest):
    home_team = request.home_team
    away_team = request.away_team
    
    # Validate teams are different
    if home_team.strip().lower() == away_team.strip().lower():
        return {"error": "Home and away teams must be different"}
    
    print(f"\n=== Prediction Request ===")
    print(f"Home: {home_team}")
    print(f"Away: {away_team}")
    
    # Get team stats with head-to-head
    home_stats = get_team_stats(home_team, club_map, club_games_df, games_df, clubs_df)
    away_stats = get_team_stats(away_team, club_map, club_games_df, games_df, clubs_df)
    
    print(f"Home stats found: {home_stats is not None}")
    print(f"Away stats found: {away_stats is not None}")
    
    # Check if teams were found
    if not home_stats:
        return {"error": f"Club not found: {home_team}"}
    if not away_stats:
        return {"error": f"Club not found: {away_team}"}
    
    # Get stadium names
    home_club_data = clubs_df[clubs_df['club_id'] == home_stats['team_id']].iloc[0]
    away_club_data = clubs_df[clubs_df['club_id'] == away_stats['team_id']].iloc[0]
    home_stadium = home_club_data.get('stadium_name', 'Unknown')
    away_stadium = away_club_data.get('stadium_name', 'Unknown')
    
    # Get head-to-head stats
    home_stats_h2h = get_team_stats(home_team, club_map, club_games_df, games_df, clubs_df, away_stats['team_id'])
    away_stats_h2h = get_team_stats(away_team, club_map, club_games_df, games_df, clubs_df, home_stats['team_id'])
    
    # Merge h2h stats
    if home_stats_h2h:
        home_stats.update({k: v for k, v in home_stats_h2h.items() if k.startswith('h2h')})
    if away_stats_h2h:
        away_stats.update({k: v for k, v in away_stats_h2h.items() if k.startswith('h2h')})
    
    # Get last 3 H2H matches
    h2h_matches = games_df[
        (((games_df['home_club_id'] == home_stats['team_id']) & (games_df['away_club_id'] == away_stats['team_id'])) |
         ((games_df['home_club_id'] == away_stats['team_id']) & (games_df['away_club_id'] == home_stats['team_id'])))
    ].sort_values('date', ascending=False).head(3)
    
    h2h_results = []
    for _, match in h2h_matches.iterrows():
        if match['home_club_id'] == home_stats['team_id']:
            result = f"{home_team} {int(match['home_club_goals'])}-{int(match['away_club_goals'])} {away_team}"
            winner = 'home' if match['home_club_goals'] > match['away_club_goals'] else ('away' if match['away_club_goals'] > match['home_club_goals'] else 'draw')
        else:
            result = f"{away_team} {int(match['home_club_goals'])}-{int(match['away_club_goals'])} {home_team}"
            winner = 'away' if match['home_club_goals'] > match['away_club_goals'] else ('home' if match['away_club_goals'] > match['home_club_goals'] else 'draw')
        
        h2h_results.append({
            'result': result,
            'winner': winner,
            'date': match['date'].strftime('%Y-%m-%d')
        })
    
    print(f"Home: {home_stats['goals_avg']:.2f} goals, {home_stats['win_rate']:.1f}% win rate")
    print(f"Away: {away_stats['goals_avg']:.2f} goals, {away_stats['win_rate']:.1f}% win rate")
    
    # Predict match
    prediction = predictor.predict(home_stats, away_stats)
    
    # Calculate xG (Expected Goals) - based on shots on target
    home_xg = round(home_stats.get('goals_avg', 0) * 1.1, 1)  # Slight boost for home
    away_xg = round(away_stats.get('goals_avg', 0) * 0.95, 1)  # Slight reduction for away
    
    # Match importance
    # Define historic rivalries
    rivalries = [
        {'Manchester United', 'Liverpool'},
        {'Manchester United', 'Manchester City'},
        {'Manchester United', 'Arsenal'},
        {'Liverpool', 'Everton'},
        {'Arsenal', 'Tottenham'},
        {'Chelsea', 'Tottenham'},
        {'Barcelona', 'Real Madrid'},
        {'AC Milan', 'Inter'},
        {'Bayern Munich', 'Borussia Dortmund'},
    ]
    
    # Check if it's a rivalry match
    is_rivalry = any(
        (home_team in rivalry and away_team in rivalry) or
        (any(home_team.startswith(r) for r in rivalry) and any(away_team.startswith(r) for r in rivalry))
        for rivalry in rivalries
    )
    
    # Check if teams are in the same domestic league
    home_league = home_club_data.get('domestic_competition_id')
    away_league = away_club_data.get('domestic_competition_id')
    same_league = home_league == away_league and pd.notna(home_league)
    
    home_pos = home_stats.get('league_position', 10)
    away_pos = away_stats.get('league_position', 10)
    
    if is_rivalry:
        importance = 'Rivalry Match'
    elif same_league and home_pos <= 4 and away_pos <= 4:
        importance = 'Title Race'
    elif same_league and (home_pos >= 17 or away_pos >= 17):
        importance = 'Relegation Battle'
    else:
        importance = 'Regular Match'
    
    # Get top scorers
    home_scorers = get_top_scorers(home_stats.get('team_id'), appearances_df, player_map)
    away_scorers = get_top_scorers(away_stats.get('team_id'), appearances_df, player_map)
    
    # Helper to convert NaN to None for JSON serialization
    def safe_value(val, default=0):
        if pd.isna(val) or val is None:
            return default
        return val
    
    return {
        "home_team": home_team,
        "away_team": away_team,
        "prediction": {
            "winner": prediction['winner'],
            "score": prediction['predicted_score'],
            "importance": importance,
            "probabilities": {
                "home_win": f"{prediction['home_win_prob']*100:.1f}%",
                "draw": f"{prediction['draw_prob']*100:.1f}%",
                "away_win": f"{prediction['away_win_prob']*100:.1f}%"
            },
            "stats": {
                "home_goals": prediction['home_goals'],
                "away_goals": prediction['away_goals'],
                "home_avg_goals": round(safe_value(home_stats.get('goals_avg', 0)), 2),
                "away_avg_goals": round(safe_value(away_stats.get('goals_avg', 0)), 2),
                "home_conceded_avg": round(safe_value(home_stats.get('conceded_avg', 0)), 2),
                "away_conceded_avg": round(safe_value(away_stats.get('conceded_avg', 0)), 2),
                "home_xg": home_xg,
                "away_xg": away_xg,
                "home_shots": round(safe_value(home_stats.get('goals_avg', 0)) * 8, 1),
                "away_shots": round(safe_value(away_stats.get('goals_avg', 0)) * 8, 1),
                "home_shots_on_target": round(safe_value(home_stats.get('goals_avg', 0)) * 4, 1),
                "away_shots_on_target": round(safe_value(away_stats.get('goals_avg', 0)) * 4, 1),
                "home_corners": round(safe_value(home_stats.get('goals_avg', 0)) * 3, 1),
                "away_corners": round(safe_value(away_stats.get('goals_avg', 0)) * 3, 1),
                "home_win_rate": round(safe_value(home_stats.get('win_rate', 0)), 1),
                "away_win_rate": round(safe_value(away_stats.get('win_rate', 0)), 1),
                "home_form": home_stats.get('form', []),
                "away_form": away_stats.get('form', []),
                "home_league_position": safe_value(home_stats.get('league_position'), None),
                "away_league_position": safe_value(away_stats.get('league_position'), None),
                "home_manager": home_stats.get('manager_name', 'Unknown'),
                "away_manager": away_stats.get('manager_name', 'Unknown'),
                "home_stadium": home_stadium if pd.notna(home_stadium) else 'Unknown',
                "away_stadium": away_stadium if pd.notna(away_stadium) else 'Unknown',
                "h2h_results": h2h_results
            },
            "likely_scorers": {
                "home": home_scorers[:3],
                "away": away_scorers[:3]
            }
        }
    }

@app.post("/predict-transfers")
async def predict_transfers(request: TransferRequest):
    club_name = request.club_name
    
    # Find club ID
    club_match = clubs_df[clubs_df['name'].str.contains(club_name.replace(' ', ''), case=False, na=False)]
    if len(club_match) == 0:
        club_match = clubs_df[clubs_df['name'].str.lower() == club_name.lower()]
    
    if len(club_match) == 0:
        return {"error": "Club not found"}
    
    club_id = club_match.iloc[0]['club_id']
    club_full_name = club_match.iloc[0]['name']
    
    # Predict transfers
    predictions = transfer_predictor.predict_transfers(club_id, club_full_name, players_df, transfers_df, clubs_df)
    
    return {
        "club_name": club_full_name,
        "transfers_out": predictions['transfers_out'],
        "transfers_in": predictions['transfers_in']
    }

def get_top_scorers(team_id, appearances_df, player_map):
    """Get top goal scorers for a specific team from recent seasons only"""
    if team_id is None:
        return ["Unknown Player"]
    
    # Get appearances for this team from last 2 seasons only (2024-2025)
    recent_appearances = appearances_df[
        (appearances_df['player_club_id'] == team_id) & 
        (appearances_df['date'] >= '2023-01-01')
    ]
    
    if len(recent_appearances) == 0:
        return ["Unknown Player"]
    
    # Group by player and sum goals
    player_goals = recent_appearances.groupby('player_id')['goals'].sum().sort_values(ascending=False)
    
    # Filter out players currently on loan
    top_scorers = []
    for player_id, goals in player_goals.head(10).items():
        if goals > 0 and not is_on_loan(player_id, team_id):
            player_name = player_map.get(player_id, f"Player {player_id}")
            top_scorers.append(player_name)
            if len(top_scorers) == 3:
                break
    
    return top_scorers if top_scorers else ["Unknown Player"]

def is_on_loan(player_id, team_id):
    """Check if player is currently on loan or has left the team"""
    player_transfers = transfers_df[transfers_df['player_id'] == player_id].sort_values('transfer_date', ascending=False)
    
    # Check contract expiry
    player_info = players_df[players_df['player_id'] == player_id]
    if len(player_info) > 0:
        contract_expiry = player_info.iloc[0]['contract_expiration_date']
        if pd.notna(contract_expiry) and contract_expiry < pd.Timestamp.now():
            return True
    
    if len(player_transfers) == 0:
        return False
    
    latest_transfer = player_transfers.iloc[0]
    now = pd.Timestamp.now()
    
    # If latest transfer is TO this team and date is in future, player is returning from loan (currently away)
    if latest_transfer['to_club_id'] == team_id and pd.to_datetime(latest_transfer['transfer_date']) > now:
        return True
    
    # If latest transfer is FROM this team (left the club)
    if latest_transfer['from_club_id'] == team_id:
        return True
    
    # Check if player retired or without club
    if latest_transfer['to_club_name'] in ['Retired', 'Without Club']:
        return True
    
    return False

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
