from src.models.match_model import MatchPredictor
from src.utils.data_loader import load_match_dataset
from sklearn.metrics import accuracy_score, classification_report
import numpy as np

def train_match_model():
    print("Loading match dataset...")
    training_data, team_map, player_map = load_match_dataset()
    print(f"Loaded {len(training_data)} match samples")
    
    # Split data
    train_size = int(0.8 * len(training_data))
    train_data = training_data[:train_size]
    test_data = training_data[train_size:]
    
    print(f"\nTraining set: {len(train_data)} matches")
    print(f"Test set: {len(test_data)} matches")
    
    print("\nTraining match prediction model...")
    predictor = MatchPredictor()
    predictor.train(train_data)
    
    predictor.save_model('models/match_model.pkl')
    print("Model trained and saved to models/match_model.pkl")
    
    # Evaluate
    print("\n" + "="*50)
    print("MODEL ACCURACY EVALUATION")
    print("="*50)
    
    correct_results = 0
    correct_scores = 0
    actual_results = []
    predicted_results = []
    goal_errors = []
    
    for match in test_data:
        home_stats = {
            'goals_avg': match['home_goals_avg'],
            'conceded_avg': match.get('home_conceded_avg', 1.5),
            'win_rate': match.get('home_win_rate', 50),
            'home_win_rate': match.get('home_home_win_rate', 50)
        }
        away_stats = {
            'goals_avg': match['away_goals_avg'],
            'conceded_avg': match.get('away_conceded_avg', 1.5),
            'win_rate': match.get('away_win_rate', 50),
            'away_win_rate': match.get('away_away_win_rate', 50)
        }
        
        prediction = predictor.predict(home_stats, away_stats)
        
        if prediction['winner'] == match['result']:
            correct_results += 1
        
        if prediction['home_goals'] == match['home_goals'] and prediction['away_goals'] == match['away_goals']:
            correct_scores += 1
        
        home_error = abs(prediction['home_goals'] - match['home_goals'])
        away_error = abs(prediction['away_goals'] - match['away_goals'])
        goal_errors.append((home_error + away_error) / 2)
        
        actual_results.append(match['result'])
        predicted_results.append(prediction['winner'])
    
    result_accuracy = (correct_results / len(test_data)) * 100
    score_accuracy = (correct_scores / len(test_data)) * 100
    avg_goal_error = np.mean(goal_errors)
    
    print(f"\nResult Accuracy (Win/Draw/Loss): {result_accuracy:.2f}%")
    print(f"Exact Score Accuracy: {score_accuracy:.2f}%")
    print(f"Average Goal Prediction Error: {avg_goal_error:.2f} goals")
    
    print("\nDetailed Classification Report:")
    print(classification_report(actual_results, predicted_results, 
                                target_names=['Away Win', 'Draw', 'Home Win'],
                                zero_division=0))
    
    # Sample predictions
    print("\n" + "="*50)
    print("SAMPLE PREDICTIONS")
    print("="*50)
    for i in range(min(5, len(test_data))):
        match = test_data[i]
        home_stats = {
            'goals_avg': match['home_goals_avg'],
            'conceded_avg': match.get('home_conceded_avg', 1.5),
            'win_rate': match.get('home_win_rate', 50),
            'home_win_rate': match.get('home_home_win_rate', 50)
        }
        away_stats = {
            'goals_avg': match['away_goals_avg'],
            'conceded_avg': match.get('away_conceded_avg', 1.5),
            'win_rate': match.get('away_win_rate', 50),
            'away_win_rate': match.get('away_away_win_rate', 50)
        }
        
        result = predictor.predict(home_stats, away_stats)
        print(f"\n{match['home_team']} vs {match['away_team']}")
        print(f"  Actual: {match['home_goals']}-{match['away_goals']} ({match['result']})")
        print(f"  Predicted: {result['predicted_score']} ({result['winner']})")
        print(f"  Probabilities: H:{result['home_win_prob']*100:.1f}% D:{result['draw_prob']*100:.1f}% A:{result['away_win_prob']*100:.1f}%")

if __name__ == "__main__":
    train_match_model()
