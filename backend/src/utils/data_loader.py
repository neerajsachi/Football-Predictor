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
    club_value_map = dict(zip(clubs['club_id'], clubs['total_market_value']))
    
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
        
        # NEW: Head-to-head history (last 5 meetings)
        h2h_games = games[
            (((games['home_club_id'] == home_id) & (games['away_club_id'] == away_id)) |
             ((games['home_club_id'] == away_id) & (games['away_club_id'] == home_id))) &
            (games['game_id'] < game['game_id'])
        ].tail(5)
        
        h2h_home_wins = 0
        h2h_away_wins = 0
        h2h_draws = 0
        h2h_home_goals = 0
        h2h_away_goals = 0
        
        for _, h2h in h2h_games.iterrows():
            if h2h['home_club_id'] == home_id:
                h2h_home_goals += h2h['home_club_goals']
                h2h_away_goals += h2h['away_club_goals']
                if h2h['home_club_goals'] > h2h['away_club_goals']:
                    h2h_home_wins += 1
                elif h2h['home_club_goals'] < h2h['away_club_goals']:
                    h2h_away_wins += 1
                else:
                    h2h_draws += 1
            else:
                h2h_home_goals += h2h['away_club_goals']
                h2h_away_goals += h2h['home_club_goals']
                if h2h['away_club_goals'] > h2h['home_club_goals']:
                    h2h_home_wins += 1
                elif h2h['away_club_goals'] < h2h['home_club_goals']:
                    h2h_away_wins += 1
                else:
                    h2h_draws += 1
        
        h2h_count = len(h2h_games)
        h2h_home_win_rate = (h2h_home_wins / h2h_count * 100) if h2h_count > 0 else 50
        h2h_home_goals_avg = (h2h_home_goals / h2h_count) if h2h_count > 0 else home_goals_avg
        h2h_away_goals_avg = (h2h_away_goals / h2h_count) if h2h_count > 0 else away_goals_avg
        
        # NEW: League positions
        home_position = home_club_stats.iloc[-1]['own_position'] if pd.notna(home_club_stats.iloc[-1]['own_position']) else 10
        away_position = away_club_stats.iloc[-1]['own_position'] if pd.notna(away_club_stats.iloc[-1]['own_position']) else 10
        
        # NEW: Squad market value
        home_value = club_value_map.get(home_id, 0)
        away_value = club_value_map.get(away_id, 0)
        # Handle zero values
        if home_value == 0:
            home_value = 100000000  # Default 100M
        if away_value == 0:
            away_value = 100000000
        value_ratio = (home_value / away_value) if away_value > 0 else 1.0
        
        # NEW: Manager consistency (same manager in recent games)
        home_manager = home_club_stats.iloc[-1]['own_manager_name']
        away_manager = away_club_stats.iloc[-1]['own_manager_name']
        home_manager_games = len(home_club_stats[home_club_stats['own_manager_name'] == home_manager]) if pd.notna(home_manager) else 5
        away_manager_games = len(away_club_stats[away_club_stats['own_manager_name'] == away_manager]) if pd.notna(away_manager) else 5
        
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
            'h2h_home_win_rate': float(h2h_home_win_rate),
            'h2h_home_goals_avg': float(h2h_home_goals_avg),
            'h2h_away_goals_avg': float(h2h_away_goals_avg),
            'h2h_count': int(h2h_count),
            'home_position': float(home_position),
            'away_position': float(away_position),
            'home_value': float(home_value),
            'away_value': float(away_value),
            'value_ratio': float(value_ratio),
            'home_manager_games': int(home_manager_games),
            'away_manager_games': int(away_manager_games),
            'home_goals': int(game['home_club_goals']),
            'away_goals': int(game['away_club_goals']),
            'result': result
        })
    
    return training_data, club_map, {}

def get_team_stats(team_name, team_map, club_games_df, games_df=None, clubs_df=None, opponent_id=None):
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
    
    # Load games.csv if not provided
    if games_df is None:
        games_df = pd.read_csv('data/dataset/games.csv', encoding='utf-8')
    games_df['date'] = pd.to_datetime(games_df['date'])
    
    # Load clubs.csv if not provided
    if clubs_df is None:
        clubs_df = pd.read_csv('data/dataset/clubs.csv', encoding='utf-8')
    
    team_games = club_games_df[club_games_df['club_id'] == team_id].copy()
    team_games = team_games.merge(games_df[['game_id', 'date']], on='game_id', how='left')
    recent_games = team_games.sort_values('date', ascending=False).head(10)
    
    if len(recent_games) == 0:
        print(f"No games found for team ID {team_id}")
        return None
    
    home_games = recent_games[recent_games['hosting'] == 'Home']
    
    # Get last 5 results for form
    last_5 = recent_games.head(5)
    form = []
    for _, game in last_5.iterrows():
        if game['own_goals'] > game['opponent_goals']:
            form.append('W')
        elif game['own_goals'] < game['opponent_goals']:
            form.append('L')
        else:
            form.append('D')
    
    # Get current league position from most recent game with position data
    league_position = None
    for _, game in recent_games.iterrows():
        if pd.notna(game['own_position']):
            league_position = game['own_position']
            break
    
    # Get squad market value
    club_info = clubs_df[clubs_df['club_id'] == team_id]
    squad_value = club_info.iloc[0]['total_market_value'] if len(club_info) > 0 else 0
    
    # Get manager info
    current_manager = recent_games.iloc[0]['own_manager_name']
    manager_games = len(recent_games[recent_games['own_manager_name'] == current_manager])
    
    # Head-to-head stats (if opponent provided)
    h2h_stats = {}
    if opponent_id:
        h2h_games = games_df[
            (((games_df['home_club_id'] == team_id) & (games_df['away_club_id'] == opponent_id)) |
             ((games_df['home_club_id'] == opponent_id) & (games_df['away_club_id'] == team_id)))
        ].tail(5)
        
        h2h_wins = 0
        h2h_goals = 0
        h2h_conceded = 0
        
        for _, h2h in h2h_games.iterrows():
            if h2h['home_club_id'] == team_id:
                h2h_goals += h2h['home_club_goals']
                h2h_conceded += h2h['away_club_goals']
                if h2h['home_club_goals'] > h2h['away_club_goals']:
                    h2h_wins += 1
            else:
                h2h_goals += h2h['away_club_goals']
                h2h_conceded += h2h['home_club_goals']
                if h2h['away_club_goals'] > h2h['home_club_goals']:
                    h2h_wins += 1
        
        h2h_count = len(h2h_games)
        h2h_stats = {
            'h2h_win_rate': (h2h_wins / h2h_count * 100) if h2h_count > 0 else 50,
            'h2h_goals_avg': (h2h_goals / h2h_count) if h2h_count > 0 else recent_games['own_goals'].mean(),
            'h2h_conceded_avg': (h2h_conceded / h2h_count) if h2h_count > 0 else recent_games['opponent_goals'].mean(),
            'h2h_count': h2h_count
        }
    
    return {
        'goals_avg': float(recent_games['own_goals'].mean()),
        'conceded_avg': float(recent_games['opponent_goals'].mean()),
        'win_rate': float(recent_games['is_win'].mean() * 100),
        'home_win_rate': float(home_games['is_win'].mean() * 100) if len(home_games) > 0 else 50,
        'team_id': team_id,
        'form': form,
        'league_position': int(league_position) if league_position else None,
        'squad_value': float(squad_value),
        'manager_name': current_manager,
        'manager_games': int(manager_games),
        **h2h_stats
    }

if __name__ == "__main__":
    data, team_map, _ = load_match_dataset()
    print(f"\nProcessed {len(data)} training samples")
    print("\nSample data:")
    for i in range(min(3, len(data))):
        print(f"\n{data[i]['home_team']} vs {data[i]['away_team']}: {data[i]['home_goals']}-{data[i]['away_goals']} ({data[i]['result']})")
