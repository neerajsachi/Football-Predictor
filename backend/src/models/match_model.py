import numpy as np
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
        features = [
            home_stats['goals_avg'],
            away_stats['goals_avg'],
            home_stats.get('conceded_avg', 1.5),
            away_stats.get('conceded_avg', 1.5),
            home_stats['goals_avg'] - away_stats['goals_avg'],  # Attack difference
            away_stats.get('conceded_avg', 1.5) - home_stats.get('conceded_avg', 1.5),  # Defense difference
            home_stats.get('win_rate', 50) / 100,
            away_stats.get('win_rate', 50) / 100,
            (home_stats.get('win_rate', 50) - away_stats.get('win_rate', 50)) / 100,  # Form difference
            home_stats.get('home_win_rate', 50) / 100,  # Home advantage
            away_stats.get('away_win_rate', 50) / 100,  # Away form
            home_stats['goals_avg'] / max(home_stats.get('conceded_avg', 1), 0.5),  # Home attack/defense ratio
            away_stats['goals_avg'] / max(away_stats.get('conceded_avg', 1), 0.5),  # Away attack/defense ratio
            0.3  # Reduced home advantage constant
        ]
        return np.array(features).reshape(1, -1)
    
    def train(self, training_data):
        X, y_result, y_home_goals, y_away_goals = [], [], [], []
        
        for data in training_data:
            home_stats = {
                'goals_avg': data['home_goals_avg'],
                'conceded_avg': data.get('home_conceded_avg', 1.5),
                'win_rate': data.get('home_win_rate', 50),
                'home_win_rate': data.get('home_home_win_rate', 50)
            }
            away_stats = {
                'goals_avg': data['away_goals_avg'],
                'conceded_avg': data.get('away_conceded_avg', 1.5),
                'win_rate': data.get('away_win_rate', 50),
                'away_win_rate': data.get('away_away_win_rate', 50)
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
        
        # Apply quality adjustment - if away team is significantly stronger, boost their chances
        quality_diff = (away_stats.get('win_rate', 50) - home_stats.get('win_rate', 50)) / 100
        goals_diff = away_stats['goals_avg'] - home_stats['goals_avg']
        
        # If away team is much stronger (>20% better win rate or >0.8 more goals), adjust probabilities
        if quality_diff > 0.2 or goals_diff > 0.8:
            adjustment = min(0.25, quality_diff * 0.5 + goals_diff * 0.1)
            result_proba[0] += adjustment  # Boost away win
            result_proba[2] -= adjustment * 0.8  # Reduce home win
            result_proba[1] -= adjustment * 0.2  # Slightly reduce draw
            # Normalize
            result_proba = result_proba / result_proba.sum()
        
        result_pred = np.argmax(result_proba)
        
        # Predict goals with realistic constraints
        home_goals_raw = self.home_goals_model.predict(features_scaled)[0]
        away_goals_raw = self.away_goals_model.predict(features_scaled)[0]
        
        # Apply quality adjustment to goals - stronger team should score more
        if quality_diff > 0.2 or goals_diff > 0.8:
            # Boost away goals, reduce home goals
            goal_adjustment = min(1.0, quality_diff * 1.5 + goals_diff * 0.5)
            away_goals_raw += goal_adjustment
            home_goals_raw -= goal_adjustment * 0.5
        elif quality_diff < -0.2 or goals_diff < -0.8:
            # Boost home goals, reduce away goals
            goal_adjustment = min(1.0, abs(quality_diff) * 1.5 + abs(goals_diff) * 0.5)
            home_goals_raw += goal_adjustment
            away_goals_raw -= goal_adjustment * 0.5
        
        # Apply realistic constraints (max 5 goals per team, max 8 total)
        home_goals = max(0, min(5, int(round(home_goals_raw))))
        away_goals = max(0, min(5, int(round(away_goals_raw))))
        
        # If total goals > 7, scale down proportionally
        total_goals = home_goals + away_goals
        if total_goals > 7:
            scale_factor = 7 / total_goals
            home_goals = max(0, int(round(home_goals * scale_factor)))
            away_goals = max(0, int(round(away_goals * scale_factor)))
        
        result_map = {0: 'away', 1: 'draw', 2: 'home'}
        
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
