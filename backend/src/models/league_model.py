import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
import pickle
import os

class LeaguePredictor:
    def __init__(self):
        self.points_model = None
        self.goals_for_model = None
        self.goals_against_model = None
        self.is_trained = False
    
    def train(self, clubs_df, club_games_df, games_df):
        """Train ML models on historical data"""
        print("Training league prediction models...")
        
        X_list = []
        y_points_list = []
        y_gf_list = []
        y_ga_list = []
        
        # Get all teams
        for _, club in clubs_df.iterrows():
            team_games = club_games_df[club_games_df['club_id'] == club['club_id']].copy()
            if len(team_games) < 20:
                continue
            
            # Merge with games
            team_games = team_games.merge(games_df[['game_id', 'date']], on='game_id', how='left')
            team_games = team_games.sort_values('date')
            
            # Create training samples (use first 10 games to predict season totals)
            if len(team_games) >= 30:
                first_10 = team_games.head(10)
                full_season = team_games.head(38) if len(team_games) >= 38 else team_games
                
                features = self._extract_features(first_10)
                
                # Calculate actual season stats
                actual_points = (full_season['is_win'] == 1).sum() * 3 + \
                               ((full_season['is_win'] == 0) & (full_season['own_goals'] == full_season['opponent_goals'])).sum()
                actual_gf = full_season['own_goals'].sum()
                actual_ga = full_season['opponent_goals'].sum()
                
                X_list.append(features)
                y_points_list.append(actual_points)
                y_gf_list.append(actual_gf)
                y_ga_list.append(actual_ga)
        
        if len(X_list) < 50:
            print(f"Not enough training data ({len(X_list)} samples). Using statistical method.")
            return False
        
        X = np.array(X_list)
        y_points = np.array(y_points_list)
        y_gf = np.array(y_gf_list)
        y_ga = np.array(y_ga_list)
        
        print(f"Training on {len(X)} team seasons...")
        
        # Train models
        self.points_model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
        self.goals_for_model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
        self.goals_against_model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
        
        self.points_model.fit(X, y_points)
        self.goals_for_model.fit(X, y_gf)
        self.goals_against_model.fit(X, y_ga)
        
        self.is_trained = True
        print("✅ League models trained successfully!")
        return True
    
    def save_model(self, filepath):
        """Save trained models"""
        if not self.is_trained:
            return False
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'points_model': self.points_model,
                'goals_for_model': self.goals_for_model,
                'goals_against_model': self.goals_against_model
            }, f)
        print(f"✅ League models saved to {filepath}")
        return True
    
    def load_model(self, filepath):
        """Load trained models"""
        if not os.path.exists(filepath):
            return False
        
        with open(filepath, 'rb') as f:
            models = pickle.load(f)
            self.points_model = models['points_model']
            self.goals_for_model = models['goals_for_model']
            self.goals_against_model = models['goals_against_model']
        
        self.is_trained = True
        print(f"✅ League models loaded from {filepath}")
        return True
    
    def predict_league_table(self, league_id, clubs_df, club_games_df, games_df):
        """Predict final league table for a given league"""
        
        # Hardcoded current Premier League teams (2025/26 season)
        current_premier_league = [
            'Liverpool Football Club', 'Arsenal Football Club', 'Manchester City Football Club',
            'Chelsea Football Club', 'Newcastle United Football Club', 'Manchester United Football Club',
            'Tottenham Hotspur Football Club', 'Aston Villa Football Club', 'Brighton and Hove Albion Football Club',
            'Nottingham Forest Football Club', 'Fulham Football Club', 'Association Football Club Bournemouth',
            'Brentford Football Club', 'West Ham United Football Club', 'Crystal Palace Football Club',
            'Everton Football Club', 'Wolverhampton Wanderers Football Club', 'Leicester City',
            'Ipswich Town', 'Southampton FC'
        ]
        
        # Get teams in the league
        if league_id == 'GB1':  # Premier League
            teams = clubs_df[
                (clubs_df['domestic_competition_id'] == league_id) &
                (clubs_df['name'].isin(current_premier_league))
            ].copy()
        else:
            # For other leagues, use recent activity filter
            recent_date = games_df['date'].max() - pd.Timedelta(days=180)
            recent_games = games_df[games_df['date'] >= recent_date]
            recent_club_games = club_games_df.merge(recent_games[['game_id']], on='game_id', how='inner')
            active_club_ids = recent_club_games['club_id'].unique()
            teams = clubs_df[
                (clubs_df['domestic_competition_id'] == league_id) & 
                (clubs_df['club_id'].isin(active_club_ids))
            ].copy()
        
        if len(teams) == 0:
            return None
        
        table = []
        for _, team in teams.iterrows():
            team_games = club_games_df[club_games_df['club_id'] == team['club_id']].copy()
            if len(team_games) < 5:
                continue
            
            # Merge and sort by date
            team_games = team_games.merge(games_df[['game_id', 'date']], on='game_id', how='left')
            team_games = team_games.sort_values('date', ascending=False)
            
            # Get current season stats (all games played so far)
            current_season = team_games.head(25)  # Assume max 25 games played in current season
            
            # Calculate current standings
            games_played = len(current_season)
            current_wins = (current_season['is_win'] == 1).sum()
            current_draws = ((current_season['is_win'] == 0) & (current_season['own_goals'] == current_season['opponent_goals'])).sum()
            current_losses = games_played - current_wins - current_draws
            current_points = current_wins * 3 + current_draws
            current_gf = current_season['own_goals'].sum()
            current_ga = current_season['opponent_goals'].sum()
            
            # Use recent 10 games for form prediction
            recent_games = team_games.head(10)
            features = self._extract_features(recent_games).reshape(1, -1)
            
            # Calculate remaining games
            total_games = 38
            games_remaining = total_games - games_played
            
            if games_remaining <= 0:
                # Season complete, use actual stats
                final_points = int(current_points)
                final_gf = int(current_gf)
                final_ga = int(current_ga)
                final_wins = int(current_wins)
                final_draws = int(current_draws)
                final_losses = int(current_losses)
            else:
                # Predict remaining games
                if self.is_trained:
                    # Use ML to predict full season, then subtract current
                    predicted_full_points = self.points_model.predict(features)[0]
                    predicted_full_gf = self.goals_for_model.predict(features)[0]
                    predicted_full_ga = self.goals_against_model.predict(features)[0]
                    
                    # Project remaining games
                    remaining_points = max(0, predicted_full_points - current_points)
                    remaining_gf = max(0, predicted_full_gf - current_gf)
                    remaining_ga = max(0, predicted_full_ga - current_ga)
                else:
                    # Statistical projection for remaining games
                    win_rate = current_wins / games_played if games_played > 0 else 0
                    goals_per_game = current_gf / games_played if games_played > 0 else 0
                    conceded_per_game = current_ga / games_played if games_played > 0 else 0
                    draw_rate = current_draws / games_played if games_played > 0 else 0
                    
                    remaining_points = (win_rate * 3 + draw_rate) * games_remaining
                    remaining_gf = goals_per_game * games_remaining
                    remaining_ga = conceded_per_game * games_remaining
                
                # Calculate final stats
                final_points = int(current_points + remaining_points)
                final_gf = int(current_gf + remaining_gf)
                final_ga = int(current_ga + remaining_ga)
                
                # Estimate final W/D/L
                remaining_wins = remaining_points // 3
                remaining_draws = remaining_points % 3
                remaining_losses = games_remaining - remaining_wins - remaining_draws
                
                final_wins = int(current_wins + remaining_wins)
                final_draws = int(current_draws + remaining_draws)
                final_losses = int(current_losses + remaining_losses)
            
            table.append({
                'team_name': team['name'],
                'played': total_games,
                'won': final_wins,
                'drawn': final_draws,
                'lost': final_losses,
                'goals_for': final_gf,
                'goals_against': final_ga,
                'goal_diff': final_gf - final_ga,
                'points': final_points
            })
        
        # Sort by points, then goal difference
        table = sorted(table, key=lambda x: (x['points'], x['goal_diff']), reverse=True)
        
        # Add position
        for i, team in enumerate(table):
            team['position'] = i + 1
        
        return table
    
    def _extract_features(self, games_df):
        """Extract features from games"""
        if len(games_df) == 0:
            return np.zeros(15)
        
        # Basic stats
        played = len(games_df)
        won = (games_df['is_win'] == 1).sum()
        drawn = ((games_df['is_win'] == 0) & (games_df['own_goals'] == games_df['opponent_goals'])).sum()
        lost = played - won - drawn
        
        goals_for = games_df['own_goals'].sum()
        goals_against = games_df['opponent_goals'].sum()
        
        # Rates
        win_rate = won / played if played > 0 else 0
        goals_per_game = goals_for / played if played > 0 else 0
        conceded_per_game = goals_against / played if played > 0 else 0
        
        # Home/Away splits
        home_games = games_df[games_df['own_position'] == 'Home']
        away_games = games_df[games_df['own_position'] == 'Away']
        
        home_win_rate = (home_games['is_win'] == 1).sum() / len(home_games) if len(home_games) > 0 else 0
        away_win_rate = (away_games['is_win'] == 1).sum() / len(away_games) if len(away_games) > 0 else 0
        
        home_goals_avg = home_games['own_goals'].mean() if len(home_games) > 0 else 0
        away_goals_avg = away_games['own_goals'].mean() if len(away_games) > 0 else 0
        
        # Recent form (last 5)
        recent = games_df.tail(5)
        recent_wins = (recent['is_win'] == 1).sum()
        recent_goals = recent['own_goals'].mean()
        
        return np.array([
            win_rate,
            goals_per_game,
            conceded_per_game,
            home_win_rate,
            away_win_rate,
            home_goals_avg,
            away_goals_avg,
            won,
            drawn,
            lost,
            goals_for,
            goals_against,
            recent_wins,
            recent_goals,
            played
        ])
    
    def _get_team_season_stats(self, team_id, club_games_df, games_df):
        """Get current season statistics for a team"""
        
        team_games = club_games_df[club_games_df['club_id'] == team_id].copy()
        if len(team_games) == 0:
            return None
        
        team_games = team_games.merge(games_df, on='game_id', how='left')
        team_games = team_games.sort_values('date', ascending=False)
        recent_games = team_games.head(10)
        
        played = len(recent_games)
        won = len(recent_games[recent_games['is_win'] == 1])
        drawn = len(recent_games[(recent_games['is_win'] == 0) & (recent_games['own_goals'] == recent_games['opponent_goals'])])
        lost = played - won - drawn
        
        goals_for = recent_games['own_goals'].sum()
        goals_against = recent_games['opponent_goals'].sum()
        
        return {
            'played': played,
            'won': won,
            'drawn': drawn,
            'lost': lost,
            'goals_for': int(goals_for),
            'goals_against': int(goals_against),
            'goals_per_game': goals_for / played if played > 0 else 0,
            'conceded_per_game': goals_against / played if played > 0 else 0,
            'win_rate': won / played if played > 0 else 0
        }
