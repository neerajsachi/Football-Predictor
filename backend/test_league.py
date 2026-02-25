#!/usr/bin/env python3
"""Test script for league predictor"""

import sys
sys.path.append('.')

from src.models.league_model import LeaguePredictor
import pandas as pd

# Load data
clubs_df = pd.read_csv('data/dataset/clubs.csv', encoding='utf-8')
club_games_df = pd.read_csv('data/dataset/club_games.csv', encoding='utf-8')
games_df = pd.read_csv('data/dataset/games.csv', encoding='utf-8')
games_df['date'] = pd.to_datetime(games_df['date'])

# Test with Premier League (GB1)
predictor = LeaguePredictor()
table = predictor.predict_league_table('GB1', clubs_df, club_games_df, games_df)

if table:
    print("✅ League prediction successful!")
    print(f"\\nPredicted {len(table)} teams")
    print("\\nTop 5:")
    for team in table[:5]:
        print(f"{team['position']}. {team['team_name']} - {team['points']} pts")
else:
    print("❌ League prediction failed")
