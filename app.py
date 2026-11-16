import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="NRL Performance & Elo Analytics", page_icon="🏉", layout="wide")

st.title("🏉 NRL Teams Performance & Dynamic Elo Analytics")
st.markdown("Professional data science portfolio dashboard comparing proprietary Elo ratings against normalized bookmaker markets (2018–2026).")

@st.cache_data
def load_data():
    df = pd.read_csv('data/processed/final_nrl_dataset.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("Dashboard Controls")
selected_season = st.sidebar.selectbox("Select Season / Year", sorted(df['competition_year'].unique(), reverse=True))

season_df = df[df['competition_year'] == selected_season]

# Top Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Matches Analyzed", len(season_df))
col2.metric("Matches with Bookmaker Odds", season_df['market_home_prob'].notna().sum())
col3.metric("Teams Tracked", len(set(season_df['home_team']).union(set(season_df['away_team']))))

st.divider()

# Section 1: Team Elo Trajectory Explorer
st.subheader("📈 Team Elo Rating Trajectories")
all_teams = sorted(list(set(df['home_team']).union(set(df['away_team']))))
chosen_team = st.selectbox("Select a Team to View Elo History", all_teams, index=all_teams.index("Sydney Roosters") if "Sydney Roosters" in all_teams else 0)

team_matches = df[(df['home_team'] == chosen_team) | (df['away_team'] == chosen_team)].sort_values('date')

if not team_matches.empty:
    # Build timeline dataframe for selected team
    timeline_data = []
    for _, row in team_matches.iterrows():
        if row['home_team'] == chosen_team:
            timeline_data.append({'date': row['date'], 'elo': row['home_elo_before'], 'opponent': row['away_team'], 'venue': 'Home'})
        else:
            timeline_data.append({'date': row['date'], 'elo': row['away_elo_before'], 'opponent': row['home_team'], 'venue': 'Away'})
    
    t_df = pd.DataFrame(timeline_data)
    fig = px.line(t_df, x='date', y='elo', markers=True, title=f"{chosen_team} - Elo Rating Over Time",
                  hover_data=['opponent', 'venue'])
    st.plotly_chart(fig, use_container_width=True)

# Section 2: Matchup Simulator / Model vs Market
st.subheader("⚖️ Model Win Probability vs. Normalized Market Odds")
st.markdown("Comparing your Elo-derived home win probability directly against the overround-free market probability.")

comparison_df = season_df.dropna(subset=['market_home_prob', 'home_win_prob'])
if not comparison_df.empty:
    comparison_df['Matchup'] = comparison_df['home_team'] + " vs " + comparison_df['away_team'] + " (" + comparison_df['date'].dt.strftime('%Y-%m-%d') + ")"
    selected_match = st.selectbox("Select Matchup", comparison_df['Matchup'].unique())
    
    match_row = comparison_df[comparison_df['Matchup'] == selected_match].iloc[0]
    
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Model Home Win Probability", f"{match_row['home_win_prob'] * 100:.1f}%")
    m_col2.metric("Normalized Market Probability", f"{match_row['market_home_prob'] * 100:.1f}%")
else:
    st.info("No market odds available for matches in this specific season selection.")