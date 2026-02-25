#!/usr/bin/env python3
"""Train the league prediction model"""

import pandas as pd
from src.models.league_model import LeaguePredictor

print("Loading data...")
clubs_df = pd.read_csv('data/dataset/clubs.csv', encoding='utf-8')
club_games_df = pd.read_csv('data/dataset/club_games.csv', encoding='utf-8')
games_df = pd.read_csv('data/dataset/games.csv', encoding='utf-8')

# Parse dates
games_df['date'] = pd.to_datetime(games_df['date'])

print(f"Loaded {len(clubs_df)} clubs, {len(games_df)} games")

# Train model
predictor = LeaguePredictor()
success = predictor.train(clubs_df, club_games_df, games_df)

if success:
    # Save model
    predictor.save_model('models/league_model.pkl')
    print("\n✅ League model training complete!")
    print("Model saved to: models/league_model.pkl")
else:
    print("\n⚠️ Training failed. Will use statistical fallback method.")
