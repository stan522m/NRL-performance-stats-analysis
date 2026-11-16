import pandas as pd
import numpy as np

# 1. Load and sort your filtered modern match data
df = pd.read_csv('data/processed/matches_with_odds.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(by=['date', 'match_id']).reset_index(drop=True)

# 2. Elo Parameters
INITIAL_ELO = 1500
K_FACTOR = 32
HOME_ADVANTAGE = 35  # Elo points awarded to the home team

# Dictionary to track current Elo ratings for each team
team_elos = {team: INITIAL_ELO for team in set(df['home_team']).union(set(df['away_team']))}

# Lists to store pre-match and post-match ratings
home_elo_before, away_elo_before = [], []
home_win_prob = []

for idx, row in df.iterrows():
    home = row['home_team']
    away = row['away_team']
    
    # Get current ratings
    h_elo = team_elos[home]
    a_elo = team_elos[away]
    
    # Store pre-match ratings
    home_elo_before.append(h_elo)
    away_elo_before.append(a_elo)
    
    # Calculate expected outcome with home-ground advantage
    h_elo_adjusted = h_elo + HOME_ADVANTAGE
    expected_home = 1 / (1 + 10 ** ((a_elo - h_elo_adjusted) / 400))
    home_win_prob.append(expected_home)
    
    # Skip Elo update if the match hasn't been played yet (missing scores)
    if pd.isna(row['home_team_score']) or pd.isna(row['away_team_score']):
        continue
    
    # Determine actual outcome (1 for home win, 0 for away win, 0.5 for draw)
    if row['home_team_score'] > row['away_team_score']:
        actual_home = 1.0
    elif row['home_team_score'] < row['away_team_score']:
        actual_home = 0.0
    else:
        actual_home = 0.5
        
    # Margin of Victory multiplier (rewards blowout wins more than narrow squeaks)
    score_diff = abs(row['home_team_score'] - row['away_team_score'])
    mov_multiplier = np.log(max(score_diff, 1) + 1) * (2.2 / ((h_elo - a_elo) * 0.001 + 2.2))
    
    # Update Elo ratings
    elo_change = K_FACTOR * mov_multiplier * (actual_home - expected_home)
    team_elos[home] = h_elo + elo_change
    team_elos[away] = a_elo - elo_change

# Add columns back to DataFrame
df['home_elo_before'] = home_elo_before
df['away_elo_before'] = away_elo_before
df['home_win_prob'] = home_win_prob

# Preview latest Elo ratings
current_ratings = pd.DataFrame(list(team_elos.items()), columns=['Team', 'Elo']).sort_values(by='Elo', ascending=False)
print("Current Team Elo Rankings:")
print(current_ratings.to_string(index=False))

# Save final dataset with Elo columns
df.to_csv('data/processed/final_nrl_dataset.csv', index=False)
print("\nSaved final_nrl_dataset.csv successfully to data/processed/")