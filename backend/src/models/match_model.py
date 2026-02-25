import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import os

class MatchPredictor:
    def __init__(self):
        # Use ensemble of best models
        self.result_model_rf = RandomForestClassifier(n_estimators=250, max_depth=20, min_samples_split=4, random_state=42)
        self.result_model_gb = GradientBoostingClassifier(n_estimators=200, max_depth=6, learning_rate=0.08, random_state=42)
        self.home_goals_model = GradientBoostingRegressor(n_estimators=200, max_depth=6, learning_rate=0.08, random_state=42)
        self.away_goals_model = GradientBoostingRegressor(n_estimators=200, max_depth=6, learning_rate=0.08, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_features(self, home_stats, away_stats):
        # Helper to safely get values with defaults
        def safe_get(stats, key, default):
            val = stats.get(key, default)
            return default if pd.isna(val) or val is None else val
        
        features = [
            safe_get(home_stats, 'goals_avg', 1.5),
            safe_get(away_stats, 'goals_avg', 1.5),
            safe_get(home_stats, 'conceded_avg', 1.5),
            safe_get(away_stats, 'conceded_avg', 1.5),
            safe_get(home_stats, 'goals_avg', 1.5) - safe_get(away_stats, 'goals_avg', 1.5),
            safe_get(away_stats, 'conceded_avg', 1.5) - safe_get(home_stats, 'conceded_avg', 1.5),
            safe_get(home_stats, 'win_rate', 50) / 100,
            safe_get(away_stats, 'win_rate', 50) / 100,
            (safe_get(home_stats, 'win_rate', 50) - safe_get(away_stats, 'win_rate', 50)) / 100,
            safe_get(home_stats, 'home_win_rate', 50) / 100,
            safe_get(away_stats, 'away_win_rate', 50) / 100,
            safe_get(home_stats, 'goals_avg', 1.5) / max(safe_get(home_stats, 'conceded_avg', 1), 0.5),
            safe_get(away_stats, 'goals_avg', 1.5) / max(safe_get(away_stats, 'conceded_avg', 1), 0.5),
            0.3,
            # Head-to-head features
            safe_get(home_stats, 'h2h_win_rate', 50) / 100,
            safe_get(home_stats, 'h2h_goals_avg', safe_get(home_stats, 'goals_avg', 1.5)),
            safe_get(away_stats, 'h2h_goals_avg', safe_get(away_stats, 'goals_avg', 1.5)),
            safe_get(home_stats, 'h2h_count', 0) / 10,
            # League position features
            (20 - safe_get(home_stats, 'league_position', 10)) / 20,
            (20 - safe_get(away_stats, 'league_position', 10)) / 20,
            # Squad value features
            safe_get(home_stats, 'squad_value', 100000000) / 1e9,
            safe_get(away_stats, 'squad_value', 100000000) / 1e9,
            safe_get(home_stats, 'squad_value', 100000000) / max(safe_get(away_stats, 'squad_value', 100000000), 1),
            # Manager stability
            safe_get(home_stats, 'manager_games', 5) / 10,
            safe_get(away_stats, 'manager_games', 5) / 10
        ]
        return np.array(features).reshape(1, -1)
    
    def train(self, training_data):
        X, y_result, y_home_goals, y_away_goals = [], [], [], []
        
        for data in training_data:
            home_stats = {
                'goals_avg': data['home_goals_avg'],
                'conceded_avg': data.get('home_conceded_avg', 1.5),
                'win_rate': data.get('home_win_rate', 50),
                'home_win_rate': data.get('home_home_win_rate', 50),
                'h2h_win_rate': data.get('h2h_home_win_rate', 50),
                'h2h_goals_avg': data.get('h2h_home_goals_avg', data['home_goals_avg']),
                'h2h_count': data.get('h2h_count', 0),
                'league_position': data.get('home_position', 10),
                'squad_value': data.get('home_value', 0),
                'manager_games': data.get('home_manager_games', 5)
            }
            away_stats = {
                'goals_avg': data['away_goals_avg'],
                'conceded_avg': data.get('away_conceded_avg', 1.5),
                'win_rate': data.get('away_win_rate', 50),
                'away_win_rate': data.get('away_away_win_rate', 50),
                'h2h_win_rate': 100 - data.get('h2h_home_win_rate', 50),  # Inverse of home
                'h2h_goals_avg': data.get('h2h_away_goals_avg', data['away_goals_avg']),
                'h2h_count': data.get('h2h_count', 0),
                'league_position': data.get('away_position', 10),
                'squad_value': data.get('away_value', 0),
                'manager_games': data.get('away_manager_games', 5)
            }
            
            features = self.prepare_features(home_stats, away_stats)
            X.append(features[0])
            
            # Encode result
            if data['result'] == 'home':
                y_result.append(2)
            elif data['result'] == 'draw':
                y_result.append(1)
            else:
                y_result.append(0)
            
            y_home_goals.append(data['home_goals'])
            y_away_goals.append(data['away_goals'])
        
        X = np.array(X)
        X_scaled = self.scaler.fit_transform(X)
        
        print("Training ensemble models...")
        self.result_model_rf.fit(X_scaled, y_result)
        self.result_model_gb.fit(X_scaled, y_result)
        self.home_goals_model.fit(X_scaled, y_home_goals)
        self.away_goals_model.fit(X_scaled, y_away_goals)
        self.is_trained = True
        
    def predict(self, home_stats, away_stats):
        features = self.prepare_features(home_stats, away_stats)
        features_scaled = self.scaler.transform(features)
        
        # Ensemble prediction - weighted average
        result_proba_rf = self.result_model_rf.predict_proba(features_scaled)[0]
        result_proba_gb = self.result_model_gb.predict_proba(features_scaled)[0]
        result_proba = (result_proba_rf * 0.4 + result_proba_gb * 0.6)  # GB weighted more
        
        # Ensure probabilities are valid (no negatives, sum to 1)
        result_proba = np.clip(result_proba, 0, 1)
        result_proba = result_proba / result_proba.sum()
        
        # Get winner
        result_pred = np.argmax(result_proba)
        result_map = {0: 'away', 1: 'draw', 2: 'home'}
        
        # Predict goals with realistic constraints
        home_goals_raw = self.home_goals_model.predict(features_scaled)[0]
        away_goals_raw = self.away_goals_model.predict(features_scaled)[0]
        
        # Apply realistic constraints (max 5 goals per team, max 8 total)
        home_goals = max(0, min(5, int(round(home_goals_raw))))
        away_goals = max(0, min(5, int(round(away_goals_raw))))
        
        # If total goals > 7, scale down proportionally
        total_goals = home_goals + away_goals
        if total_goals > 7:
            scale_factor = 7 / total_goals
            home_goals = max(0, int(round(home_goals * scale_factor)))
            away_goals = max(0, int(round(away_goals * scale_factor)))
        
        return {
            'winner': result_map[result_pred],
            'home_win_prob': float(result_proba[2]) if len(result_proba) > 2 else 0.33,
            'draw_prob': float(result_proba[1]) if len(result_proba) > 1 else 0.33,
            'away_win_prob': float(result_proba[0]) if len(result_proba) > 0 else 0.33,
            'predicted_score': f"{home_goals}-{away_goals}",
            'home_goals': home_goals,
            'away_goals': away_goals
        }
    
    def save_model(self, filepath='match_model.pkl'):
        with open(filepath, 'wb') as f:
            pickle.dump({
                'result_model_rf': self.result_model_rf,
                'result_model_gb': self.result_model_gb,
                'home_goals_model': self.home_goals_model,
                'away_goals_model': self.away_goals_model,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }, f)
    
    def load_model(self, filepath='match_model.pkl'):
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.result_model_rf = data['result_model_rf']
                self.result_model_gb = data['result_model_gb']
                self.home_goals_model = data['home_goals_model']
                self.away_goals_model = data['away_goals_model']
                self.scaler = data['scaler']
                self.is_trained = data['is_trained']
            return True
        return False
