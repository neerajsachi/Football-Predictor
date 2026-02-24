import pandas as pd
import numpy as np

def load_match_dataset():
    """Load comprehensive dataset for match prediction"""
    
    print("Loading datasets...")
    games = pd.read_csv('data/dataset/games.csv', encoding='utf-8')
    club_games = pd.read_csv('data/dataset/club_games.csv', encoding='utf-8')
    clubs = pd.read_csv('data/dataset/clubs.csv', encoding='utf-8')
    
    print(f"Loaded {len(games)} games")
    
    # Create club mapping
    club_map = dict(zip(clubs['club_id'], clubs['name']))
    
    training_data = []
    
    # Process each game
    for _, game in games.iterrows():
        if pd.isna(game['home_club_goals']) or pd.isna(game['away_club_goals']):
            continue
            
        home_id = game['home_club_id']
        away_id = game['away_club_id']
        season = game['season']
        
        # Get club game stats
        home_club_stats = club_games[(club_games['club_id'] == home_id) & (club_games['game_id'] <= game['game_id'])].tail(10)
        away_club_stats = club_games[(club_games['club_id'] == away_id) & (club_games['game_id'] <= game['game_id'])].tail(10)
        
        if len(home_club_stats) < 3 or len(away_club_stats) < 3:
            continue
        
        # Calculate features
        home_goals_avg = home_club_stats['own_goals'].mean()
        away_goals_avg = away_club_stats['own_goals'].mean()
        home_conceded_avg = home_club_stats['opponent_goals'].mean()
        away_conceded_avg = away_club_stats['opponent_goals'].mean()
        home_win_rate = home_club_stats['is_win'].mean() * 100
        away_win_rate = away_club_stats['is_win'].mean() * 100
        
        # Home advantage
        home_home_games = home_club_stats[home_club_stats['hosting'] == 'Home']
        away_away_games = away_club_stats[away_club_stats['hosting'] == 'Away']
        home_home_win_rate = home_home_games['is_win'].mean() * 100 if len(home_home_games) > 0 else home_win_rate
        away_away_win_rate = away_away_games['is_win'].mean() * 100 if len(away_away_games) > 0 else away_win_rate
        
        # Determine result
        if game['home_club_goals'] > game['away_club_goals']:
            result = 'home'
        elif game['away_club_goals'] > game['home_club_goals']:
            result = 'away'
        else:
            result = 'draw'
        
        training_data.append({
            'home_team': club_map.get(home_id, f'Club {home_id}'),
            'away_team': club_map.get(away_id, f'Club {away_id}'),
            'home_goals_avg': float(home_goals_avg),
            'away_goals_avg': float(away_goals_avg),
            'home_conceded_avg': float(home_conceded_avg),
            'away_conceded_avg': float(away_conceded_avg),
            'home_win_rate': float(home_win_rate),
            'away_win_rate': float(away_win_rate),
            'home_home_win_rate': float(home_home_win_rate),
            'away_away_win_rate': float(away_away_win_rate),
            'home_goals': int(game['home_club_goals']),
            'away_goals': int(game['away_club_goals']),
            'result': result
        })
    
    return training_data, club_map, {}

def get_team_stats(team_name, team_map, club_games_df):
    """Get current stats for a team with fuzzy matching"""
    team_id = None
    team_name_lower = team_name.lower().replace(' ', '')
    
    # Try exact match first
    for tid, tname in team_map.items():
        if tname.lower() == team_name.lower():
            team_id = tid
            break
    
    # Try partial match without spaces
    if team_id is None:
        for tid, tname in team_map.items():
            tname_clean = tname.lower().replace(' ', '')
            if team_name_lower in tname_clean or tname_clean in team_name_lower:
                team_id = tid
                print(f"Matched '{team_name}' to '{tname}'")
                break
    
    if team_id is None:
        print(f"Team '{team_name}' not found in database")
        return None
    
    # Get recent games
    recent_games = club_games_df[club_games_df['club_id'] == team_id].tail(10)
    
    if len(recent_games) == 0:
        print(f"No games found for team ID {team_id}")
        return None
    
    home_games = recent_games[recent_games['hosting'] == 'Home']
    
    return {
        'goals_avg': float(recent_games['own_goals'].mean()),
        'conceded_avg': float(recent_games['opponent_goals'].mean()),
        'win_rate': float(recent_games['is_win'].mean() * 100),
        'home_win_rate': float(home_games['is_win'].mean() * 100) if len(home_games) > 0 else 50,
        'team_id': team_id
    }

if __name__ == "__main__":
    data, team_map, _ = load_match_dataset()
    print(f"\nProcessed {len(data)} training samples")
    print("\nSample data:")
    for i in range(min(3, len(data))):
        print(f"\n{data[i]['home_team']} vs {data[i]['away_team']}: {data[i]['home_goals']}-{data[i]['away_goals']} ({data[i]['result']})")
