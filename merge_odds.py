import pandas as pd
import os

# Ensure the processed directory exists
os.makedirs('data/processed', exist_ok=True)

# 1. Load your filtered match data (2018-2026)
matches_df = pd.read_csv('data/raw/match_data.csv')
matches_df['date'] = pd.to_datetime(matches_df['date'], dayfirst=True)

# 2. Load the AusSportsBetting Excel workbook
# Note: AusSportsBetting puts a title banner in row 0, so column headers start on row 1 (header=1)
odds_df = pd.read_excel('data/raw/nrl.xlsx', sheet_name='Data', header=1)

# 3. Clean dates and filter to 2018 onwards
odds_df['Date'] = pd.to_datetime(odds_df['Date'])
odds_df = odds_df[odds_df['Date'] >= '2018-01-01'].copy()

# 4. Map AusSportsBetting team names to match your match_data.csv
odds_team_map = {
    'Brisbane': 'Brisbane Broncos',
    'Canberra': 'Canberra Raiders',
    'Canterbury': 'Canterbury Bankstown Bulldogs',
    'Cronulla': 'Cronulla Sutherland Sharks',
    'Dolphins': 'Dolphins',
    'Gold Coast': 'Gold Coast Titans',
    'Manly': 'Manly Warringah Sea Eagles',
    'Melbourne': 'Melbourne Storm',
    'Newcastle': 'Newcastle Knights',
    'North Queensland': 'North Queensland Cowboys',
    'Parramatta': 'Parramatta Eels',
    'Penrith': 'Penrith Panthers',
    'South Sydney': 'South Sydney Rabbitohs',
    'St George Illawarra': 'St George Illawarra Dragons',
    'Sydney Roosters': 'Sydney Roosters',
    'New Zealand': 'Warriors',
    'Wests Tigers': 'Wests Tigers'
}
odds_df['home_team_clean'] = odds_df['Home Team'].map(odds_team_map)

# 5. Identify closing odds columns and calculate normalized probabilities
home_odds_col = 'Home Odds Close' if 'Home Odds Close' in odds_df.columns else 'Home Odds'
away_odds_col = 'Away Odds Close' if 'Away Odds Close' in odds_df.columns else 'Away Odds'

odds_df[home_odds_col] = pd.to_numeric(odds_df[home_odds_col], errors='coerce')
odds_df[away_odds_col] = pd.to_numeric(odds_df[away_odds_col], errors='coerce')

raw_home_prob = 1 / odds_df[home_odds_col]
raw_away_prob = 1 / odds_df[away_odds_col]
booksum = raw_home_prob + raw_away_prob

odds_df['market_overround'] = booksum - 1
odds_df['market_home_prob'] = raw_home_prob / booksum
odds_df['market_away_prob'] = raw_away_prob / booksum

# 6. Merge odds with match_data.csv
cols_to_merge = ['Date', 'home_team_clean', home_odds_col, away_odds_col, 'market_home_prob', 'market_overround']

merged_df = pd.merge(
    matches_df,
    odds_df[cols_to_merge],
    left_on=['date', 'home_team'],
    right_on=['Date', 'home_team_clean'],
    how='left'
).drop(columns=['Date', 'home_team_clean'])

# 7. Save output
output_path = 'data/processed/matches_with_odds.csv'
merged_df.to_csv(output_path, index=False)

print(f"Success! Saved to {output_path}")
print(f"Matched odds for {merged_df['market_home_prob'].notna().sum()} out of {len(merged_df)} games.")
input("Press Enter to exit...")