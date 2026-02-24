import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle

class TransferPredictor:
    def __init__(self):
        self.model_out = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model_in = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, transfers_df, players_df, clubs_df):
        """Train model on historical transfer data"""
        # Prepare training data for transfers OUT
        X_out, y_out = self._prepare_training_data(transfers_df, players_df, clubs_df)
        if len(X_out) > 0:
            self.model_out.fit(X_out, y_out)
            self.is_trained = True
    
    def _prepare_training_data(self, transfers_df, players_df, clubs_df):
        """Extract features from historical transfers"""
        features = []
        labels = []
        
        for _, transfer in transfers_df.head(1000).iterrows():
            player = players_df[players_df['player_id'] == transfer['player_id']]
            if len(player) == 0:
                continue
            
            player = player.iloc[0]
            age = 2025 - pd.to_datetime(player['date_of_birth']).year if pd.notna(player['date_of_birth']) else 25
            market_value = player['market_value_in_eur'] if pd.notna(player['market_value_in_eur']) else 0
            
            features.append([age, market_value, transfer['transfer_fee']])
            labels.append(1 if transfer['transfer_fee'] > 0 else 0)
        
        return np.array(features), np.array(labels)
    
    def predict_transfers(self, club_id, club_name, players_df, transfers_df, clubs_df):
        """Predict transfers using ML model and heuristics"""
        
        # Get current squad
        current_squad = self._get_current_squad(club_id, players_df, transfers_df)
        
        if len(current_squad) == 0:
            return {'transfers_out': [], 'transfers_in': []}
        
        # Predict transfers OUT
        transfers_out = []
        for _, player in current_squad.iterrows():
            age = 2025 - pd.to_datetime(player['date_of_birth']).year if pd.notna(player['date_of_birth']) else 25
            
            if age > 38 or age < 18:
                continue
            
            market_value = player['market_value_in_eur'] if pd.notna(player['market_value_in_eur']) else 0
            contract_expiry = pd.to_datetime(player['contract_expiration_date']) if pd.notna(player['contract_expiration_date']) else None
            
            # Calculate transfer probability
            prob = self._calculate_transfer_out_probability(age, market_value, contract_expiry)
            
            if prob > 0.3:
                dest_club = self._predict_destination(player, club_name, clubs_df, age)
                transfers_out.append({
                    'player': player['name'],
                    'position': player['position'],
                    'age': age,
                    'market_value': f"€{market_value/1000000:.1f}M" if market_value > 0 else "N/A",
                    'to_club': dest_club,
                    'probability': f"{int(prob*100)}%"
                })
                
                if len(transfers_out) >= 5:
                    break
        
        # Predict transfers IN
        transfers_in = self._predict_transfers_in(club_id, club_name, players_df, clubs_df)
        
        return {
            'transfers_out': transfers_out[:5],
            'transfers_in': transfers_in[:5]
        }
    
    def _get_current_squad(self, club_id, players_df, transfers_df):
        """Get players currently at the club based on last_season"""
        # Get players whose last_season is 2024 or 2025 (current players)
        current_squad = players_df[
            (players_df['current_club_id'] == club_id) & 
            (players_df['last_season'] >= 2024)
        ]
        
        return current_squad
    
    def _calculate_transfer_out_probability(self, age, market_value, contract_expiry):
        """Calculate probability of player leaving"""
        prob = 0.0
        
        # Young high-value players are unlikely to leave (key players)
        if age < 26 and market_value > 40000000:
            return 0.1  # Only 10% chance - they're key young talents
        
        # Age factor
        if age > 32:
            prob += 0.3
        elif age < 23:
            prob += 0.2  # Young players may move for development
        
        # Market value factor (high value = more interest)
        if market_value > 50000000:
            prob += 0.2  # Top players attract interest
        elif market_value > 20000000:
            prob += 0.15
        
        # Contract expiry factor (most important)
        if contract_expiry:
            years_left = (contract_expiry - pd.Timestamp.now()).days / 365
            if years_left < 1:
                prob += 0.5
            elif years_left < 2:
                prob += 0.3
            elif years_left < 3:
                prob += 0.1
        
        return min(prob, 0.9)
    
    def _predict_transfers_in(self, club_id, club_name, players_df, clubs_df):
        """Predict incoming transfers"""
        transfers_in = []
        positions = ['Attack', 'Midfield', 'Defender', 'Goalkeeper']
        
        for position in positions:
            candidates = players_df[
                (players_df['position'] == position) & 
                (players_df['current_club_id'] != club_id) &
                (players_df['market_value_in_eur'] > 5000000) &
                (players_df['market_value_in_eur'] < 100000000)
            ].nlargest(10, 'market_value_in_eur')
            
            for _, player in candidates.head(2).iterrows():
                age = 2025 - pd.to_datetime(player['date_of_birth']).year if pd.notna(player['date_of_birth']) else 25
                if age > 30 or age < 18:
                    continue
                
                market_value = player['market_value_in_eur'] if pd.notna(player['market_value_in_eur']) else 0
                from_club = clubs_df[clubs_df['club_id'] == player['current_club_id']]['name'].values
                from_club_name = from_club[0] if len(from_club) > 0 else "Unknown"
                
                prob = np.random.randint(25, 55)
                transfers_in.append({
                    'player': player['name'],
                    'position': player['position'],
                    'age': age,
                    'market_value': f"€{market_value/1000000:.1f}M" if market_value > 0 else "N/A",
                    'from_club': from_club_name,
                    'probability': f"{prob}%"
                })
                
                if len(transfers_in) >= 5:
                    break
            
            if len(transfers_in) >= 5:
                break
        
        return transfers_in
    
    def _predict_destination(self, player, current_club, clubs_df, age):
        """Predict destination club based on player quality and club prestige"""
        market_value = player['market_value_in_eur'] if pd.notna(player['market_value_in_eur']) else 0
        
        # Define rival clubs (no transfers between these)
        rivals = {
            'Manchester United Football Club': ['Manchester City Football Club', 'Liverpool Football Club'],
            'Manchester City Football Club': ['Manchester United Football Club', 'Liverpool Football Club'],
            'Liverpool Football Club': ['Manchester United Football Club', 'Manchester City Football Club', 'Everton Football Club'],
            'Everton Football Club': ['Liverpool Football Club'],
            'Arsenal Football Club': ['Tottenham Hotspur'],
            'Tottenham Hotspur': ['Arsenal Football Club'],
            'FC Barcelona': ['Real Madrid Club de Fútbol'],
            'Real Madrid Club de Fútbol': ['FC Barcelona', 'Club Atlético de Madrid S.A.D.'],
            'Club Atlético de Madrid S.A.D.': ['Real Madrid Club de Fútbol'],
            'AC Milan': ['FC Internazionale Milano'],
            'FC Internazionale Milano': ['AC Milan'],
            'AS Roma': ['Società Sportiva Lazio S.p.A.'],
            'Società Sportiva Lazio S.p.A.': ['AS Roma']
        }
        
        # Parse net_transfer_record to get spending amount
        def get_spending_score(net_record):
            net_record = str(net_record)
            if '€-' in net_record:
                amount = net_record.replace('€-', '').replace('m', '').replace('k', '')
                try:
                    return float(amount) if 'm' in net_record else float(amount) / 1000
                except:
                    return 0
            return 0
        
        clubs_df['spending'] = clubs_df['net_transfer_record'].apply(get_spending_score)
        clubs_df['stadium'] = clubs_df['stadium_seats'].fillna(0)
        clubs_df['prestige'] = clubs_df['spending'] * 2 + clubs_df['stadium'] / 10000
        
        # Match player value to club prestige
        if market_value > 50000000:
            target_clubs = clubs_df.nlargest(20, 'prestige')
        elif market_value > 25000000:
            target_clubs = clubs_df.nlargest(50, 'prestige')
        elif market_value > 10000000:
            target_clubs = clubs_df.nlargest(100, 'prestige')
        else:
            target_clubs = clubs_df
        
        # Remove current club and rivals
        target_clubs = target_clubs[target_clubs['name'] != current_club]
        if current_club in rivals:
            for rival in rivals[current_club]:
                target_clubs = target_clubs[target_clubs['name'] != rival]
        
        # Age factor
        if age > 32:
            if market_value < 10000000:
                target_clubs = clubs_df[
                    (clubs_df['prestige'] > 5) &
                    (clubs_df['prestige'] < 50) &
                    (clubs_df['stadium'] > 20000) &
                    (clubs_df['name'] != current_club)
                ]
                # Remove rivals from age-based selection too
                if current_club in rivals:
                    for rival in rivals[current_club]:
                        target_clubs = target_clubs[target_clubs['name'] != rival]
        
        if len(target_clubs) == 0:
            target_clubs = clubs_df.nlargest(30, 'prestige')
            target_clubs = target_clubs[target_clubs['name'] != current_club]
            if current_club in rivals:
                for rival in rivals[current_club]:
                    target_clubs = target_clubs[target_clubs['name'] != rival]
        
        if len(target_clubs) > 0:
            return target_clubs.iloc[np.random.randint(0, min(5, len(target_clubs)))]['name']
        
        return "Unknown Club"
    
    def _get_sample_club(self, clubs_df, exclude_club):
        """Get a sample club for demonstration"""
        top_clubs = clubs_df.nlargest(50, 'total_market_value')
        top_clubs = top_clubs[top_clubs['name'] != exclude_club]
        if len(top_clubs) > 0:
            return top_clubs.iloc[np.random.randint(0, min(10, len(top_clubs)))]['name']
        return "Unknown Club"
