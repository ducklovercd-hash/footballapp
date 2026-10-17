import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import random

import os
from dotenv import load_dotenv

# 1. Load local .env file if it exists (for local development)
load_dotenv()

# 2. Retrieve keys with fallback to Streamlit Secrets
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
if not API_FOOTBALL_KEY and "API_FOOTBALL_KEY" in st.secrets:
    API_FOOTBALL_KEY = st.secrets["API_FOOTBALL_KEY"]

print(API_FOOTBALL_KEY)

FOOTBALL_DATA_KEY = os.getenv("FOOTBALL_DATA_KEY")
if not FOOTBALL_DATA_KEY and "FOOTBALL_DATA_KEY" in st.secrets:
    FOOTBALL_DATA_KEY = st.secrets["FOOTBALL_DATA_KEY"]

print(FOOTBALL_DATA_KEY)
# ==============================================================================
# 1. PAGE CONFIGURATION & THEME
# ==============================================================================
st.set_page_config(
    page_title="PitchSide Analytics - Football Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Modern Football Dashboard Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge-live {
        background-color: #EF4444;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .badge-upcoming {
        background-color: #3B82F6;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-finished {
        background-color: #64748B;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .score-box {
        font-size: 1.8rem;
        font-weight: 900;
        color: #0F172A;
        text-align: center;
    }
    .team-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1E293B;
    }
</style>
""", unsafe_allow_html=True)

# League Mapping Constants
LEAGUES_CONFIG = {
    "English Premier League": {
        "api_football_id": 39,
        "football_data_code": "PL"
    },
    "Italian Serie A": {
        "api_football_id": 135,
        "football_data_code": "SA"
    },
    "Spanish La Liga": {
        "api_football_id": 140,
        "football_data_code": "PD"
    },
    "German Bundesliga": {
        "api_football_id": 78,
        "football_data_code": "BL1"
    },
    "French Ligue 1": {
        "api_football_id": 61,
        "football_data_code": "FL1"
    }
}

# ==============================================================================
# 2. HELPER FUNCTIONS & API INTEGRATION WITH CACHING
# ==============================================================================

@st.cache_data(ttl=60)
def fetch_football_data_matches(api_key, date_str, league_codes):
    """Fetch matches from Football-Data.org v4 API for specific league codes."""
    if not api_key or not league_codes:
        return None
    
    competitions = ",".join(league_codes)
    url = f"https://api.football-data.org/v4/matches?dateFrom={date_str}&dateTo={date_str}&competitions={competitions}"
    headers = {"X-Auth-Token": api_key}
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

@st.cache_data(ttl=60)
def fetch_api_football_fixtures(api_key, date_str, league_ids, fetch_live=False):
    """Fetch fixtures or live matches from API-Football v3 without conflicting parameters."""
    if not api_key or not league_ids:
        return None
    
    all_fixtures = []
    headers = {'x-apisports-key': api_key}
    
    for league_id in league_ids:
        url = "https://v3.football.api-sports.io/fixtures"
        
        # FIX: Do not pass 'season' when querying by a specific 'date'
        if fetch_live:
            params = {"live": "all"}
        else:
            params = {"date": date_str, "league": league_id}
            
        try:
            response = requests.get(url, headers=headers, params=params, timeout=8)
            
            # Fallback for RapidAPI headers if direct auth fails
            if response.status_code in [401, 403]:
                rapid_headers = {
                    'x-rapidapi-host': "v3.football.api-sports.io",
                    'x-rapidapi-key': api_key
                }
                response = requests.get(url, headers=rapid_headers, params=params, timeout=8)

            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    for item in data["response"]:
                        if fetch_live:
                            if item["league"]["id"] == league_id:
                                all_fixtures.append(item)
                        else:
                            all_fixtures.append(item)
            else:
                st.write(f"API Error ({response.status_code}) for League {league_id}: {response.text}")
        except Exception as e:
            st.write(f"Connection Exception: {e}")
            continue
            
    return {"response": all_fixtures}# Mock Data Generator with League Filtering
def get_mock_matches(selected_league_names):
    all_mock = [
        {
            "fixture_id": 1001,
            "league": "English Premier League",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "home_logo": "🔴",
            "away_logo": "🔵",
            "status": "LIVE",
            "elapsed": 67,
            "score": {"home": 2, "away": 1},
            "kickoff": "17:30 UTC"
        },
        {
            "fixture_id": 1002,
            "league": "Italian Serie A",
            "home_team": "Inter Milan",
            "away_team": "AC Milan",
            "home_logo": "🔵⚫",
            "away_logo": "🔴⚫",
            "status": "LIVE",
            "elapsed": 34,
            "score": {"home": 0, "away": 0},
            "kickoff": "20:00 UTC"
        },
        {
            "fixture_id": 1003,
            "league": "English Premier League",
            "home_team": "Liverpool",
            "away_team": "Manchester City",
            "home_logo": "🔴",
            "away_logo": "🩵",
            "status": "UPCOMING",
            "elapsed": 0,
            "score": {"home": None, "away": None},
            "kickoff": "Tomorrow 16:30 UTC"
        },
        {
            "fixture_id": 1004,
            "league": "Italian Serie A",
            "home_team": "Juventus",
            "away_team": "AS Roma",
            "home_logo": "⚪⚫",
            "away_logo": "🔴🟡",
            "status": "UPCOMING",
            "elapsed": 0,
            "score": {"home": None, "away": None},
            "kickoff": "Sunday 19:45 UTC"
        },
        {
            "fixture_id": 1005,
            "league": "Spanish La Liga",
            "home_team": "Real Madrid",
            "away_team": "FC Barcelona",
            "home_logo": "⚪",
            "away_logo": "🔵🔴",
            "status": "FINISHED",
            "elapsed": 90,
            "score": {"home": 3, "away": 2},
            "kickoff": "Completed"
        }
    ]
    return [m for m in all_mock if m["league"] in selected_league_names]

# ==============================================================================
# 3. MAIN APP HEADER & TOP CONTROLS
# ==============================================================================
st.markdown("<div class='main-header'>⚽ PitchSide Analytics</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Real-time match statistics, live player insights, predictive analytics & odds intelligence.</div>", unsafe_allow_html=True)

# Top Control Bar
ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([1.5, 1, 1, 1])

with ctrl_col1:
    selected_leagues = st.multiselect(
        "Select Leagues:",
        options=list(LEAGUES_CONFIG.keys()),
        default=["English Premier League", "Italian Serie A"]
    )

with ctrl_col2:
    date_selection = st.date_input("Select Date", datetime.now().date())

with ctrl_col3:
    st.write("") 
    use_mock_data = st.checkbox("Force Mock Data", value=False)

with ctrl_col4:
    st.write("")
    auto_refresh = st.checkbox("🔄 Auto-Refresh Live", value=False)
    if auto_refresh:
        st.rerun()

if not API_FOOTBALL_KEY and not FOOTBALL_DATA_KEY and not use_mock_data:
    st.warning("⚠️ No API keys found in `.env` or Streamlit Secrets. Tick 'Force Mock Data' to test offline.")

st.divider()
st.cache_data.clear()

st.write("---")
st.subheader("🛠️ API Debugger Diagnostics")

raw_matches = []
target_api_ids = [LEAGUES_CONFIG[l]["api_football_id"] for l in selected_leagues if l in LEAGUES_CONFIG]
target_data_codes = [LEAGUES_CONFIG[l]["football_data_code"] for l in selected_leagues if l in LEAGUES_CONFIG]

if API_FOOTBALL_KEY and not use_mock_data and target_api_ids:
    # Test live fetch and show raw response
    st.write(f"Fetching live matches for leagues: {target_api_ids}...")
    live_res = fetch_api_football_fixtures(API_FOOTBALL_KEY, str(date_selection), target_api_ids, fetch_live=True)
    st.write("Live API Response:", live_res)
    
    live_fixture_ids = set()
    if live_res and "response" in live_res:
        for item in live_res["response"]:
            live_fixture_ids.add(item["fixture"]["id"])
            goals = item.get("goals") or {"home": 0, "away": 0}
            raw_matches.append({
                "fixture_id": item["fixture"]["id"],
                "league": item["league"]["name"],
                "home_team": item["teams"]["home"]["name"],
                "away_team": item["teams"]["away"]["name"],
                "home_logo": "⚽",
                "away_logo": "⚽",
                "status": "LIVE",
                "elapsed": item["fixture"]["status"]["elapsed"] or 0,
                "score": {"home": goals.get("home", 0), "away": goals.get("home", 0)},
                "kickoff": item["fixture"]["date"][11:16] + " UTC"
            })

    # Test date fixtures fetch and show raw response
    st.write(f"Fetching date fixtures for {date_selection}...")
    date_res = fetch_api_football_fixtures(API_FOOTBALL_KEY, str(date_selection), target_api_ids, fetch_live=False)
    st.write("Date Fixtures API Response:", date_res)
    
    if date_res and "response" in date_res:
        for item in date_res["response"]:
            fid = item["fixture"]["id"]
            if fid not in live_fixture_ids:
                status_short = item["fixture"]["status"]["short"]
                status_clean = "FINISHED" if status_short == "FT" else "UPCOMING"
                goals = item.get("goals") or {"home": None, "away": None}
                raw_matches.append({
                    "fixture_id": fid,
                    "league": item["league"]["name"],
                    "home_team": item["teams"]["home"]["name"],
                    "away_team": item["teams"]["away"]["name"],
                    "home_logo": "⚽",
                    "away_logo": "⚽",
                    "status": status_clean,
                    "elapsed": 0,
                    "score": {"home": goals.get("home"), "away": goals.get("away")},
                    "kickoff": item["fixture"]["date"][11:16] + " UTC"
                })

if not raw_matches:
    st.warning("⚠️ API returned 0 matches, falling back to mock data.")
    raw_matches = get_mock_matches(selected_leagues)

st.write("Final `raw_matches` count:", len(raw_matches))
st.write("---")

main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs([
    "🏟️ Live & Weekend Matches", 
    "📊 Match Stats & Lineups", 
    "🔮 Predictions & Analytics", 
    "💰 Odds Center"
])

# Process Match Data Source based on selected leagues (combining live and scheduled date fixtures)
raw_matches = []
target_api_ids = [LEAGUES_CONFIG[l]["api_football_id"] for l in selected_leagues if l in LEAGUES_CONFIG]
target_data_codes = [LEAGUES_CONFIG[l]["football_data_code"] for l in selected_leagues if l in LEAGUES_CONFIG]

if API_FOOTBALL_KEY and not use_mock_data and target_api_ids:
    # 1. Fetch active live matches right now
    live_res = fetch_api_football_fixtures(API_FOOTBALL_KEY, str(date_selection), target_api_ids, fetch_live=True)
    live_fixture_ids = set()
    if live_res and "response" in live_res:
        for item in live_res["response"]:
            live_fixture_ids.add(item["fixture"]["id"])
            status_short = item["fixture"]["status"]["short"]
            raw_matches.append({
                "fixture_id": item["fixture"]["id"],
                "league": item["league"]["name"],
                "home_team": item["teams"]["home"]["name"],
                "away_team": item["teams"]["away"]["name"],
                "home_logo": "⚽",
                "away_logo": "⚽",
                "status": "LIVE",
                "elapsed": item["fixture"]["status"]["elapsed"] or 0,
                "score": {"home": item["goals"]["home"], "away": item["goals"]["away"]},
                "kickoff": item["fixture"]["date"][11:16] + " UTC"
            })

    # 2. Fetch date fixtures (upcoming / finished) avoiding duplicates with live
    date_res = fetch_api_football_fixtures(API_FOOTBALL_KEY, str(date_selection), target_api_ids, fetch_live=False)
    if date_res and "response" in date_res:
        for item in date_res["response"]:
            fid = item["fixture"]["id"]
            if fid not in live_fixture_ids:
                status_short = item["fixture"]["status"]["short"]
                status_clean = "FINISHED" if status_short == "FT" else "UPCOMING"
                raw_matches.append({
                    "fixture_id": fid,
                    "league": item["league"]["name"],
                    "home_team": item["teams"]["home"]["name"],
                    "away_team": item["teams"]["away"]["name"],
                    "home_logo": "⚽",
                    "away_logo": "⚽",
                    "status": status_clean,
                    "elapsed": 0,
                    "score": {"home": item["goals"]["home"], "away": item["goals"]["away"]},
                    "kickoff": item["fixture"]["date"][11:16] + " UTC"
                })

if not raw_matches and FOOTBALL_DATA_KEY and not use_mock_data and target_data_codes:
    res = fetch_football_data_matches(FOOTBALL_DATA_KEY, str(date_selection), target_data_codes)
    if res and "matches" in res:
        for item in res["matches"]:
            status_clean = "LIVE" if item["status"] in ["IN_PLAY", "PAUSED"] else ("FINISHED" if item["status"] == "FINISHED" else "UPCOMING")
            raw_matches.append({
                "fixture_id": item["id"],
                "league": item["competition"]["name"],
                "home_team": item["homeTeam"]["name"],
                "away_team": item["awayTeam"]["name"],
                "home_logo": "⚽",
                "away_logo": "⚽",
                "status": status_clean,
                "elapsed": 45 if status_clean == "LIVE" else 0,
                "score": {
                    "home": item.get("score", {}).get("fullTime", {}).get("home"),
                    "away": item.get("score", {}).get("fullTime", {}).get("away")
                },
                "kickoff": item.get("utcDate", "")[11:16] + " UTC"
            })

if not raw_matches:
    raw_matches = get_mock_matches(selected_leagues)

# ==============================================================================
# TAB 1: LIVE & WEEKEND MATCHES
# ==============================================================================
with main_tab1:
    st.subheader("🔴 Live Games Playing Now")
    live_games = [m for m in raw_matches if m["status"] == "LIVE"]
    
    if live_games:
        cols = st.columns(min(len(live_games), 3))
        for idx, game in enumerate(live_games):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="card">
                    <span class="badge-live">LIVE {game['elapsed']}'</span>
                    <p style="font-size: 0.85rem; color: #64748B; margin-top:5px;">{game['league']}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin: 10px 0;">
                        <span class="team-title">{game['home_logo']} {game['home_team']}</span>
                        <span class="score-box">{game['score']['home']} - {game['score']['away']}</span>
                        <span class="team-title">{game['away_team']} {game['away_logo']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No matches are currently live right now for the selected leagues. Showing upcoming fixtures below.")

    st.divider()
    st.subheader("🗓️ Weekend & Upcoming Fixtures")
    
    if raw_matches:
        df_matches = pd.DataFrame([
            {
                "League": m["league"],
                "Home Team": f"{m['home_logo']} {m['home_team']}",
                "Score / Time": f"{m['score']['home']} - {m['score']['away']}" if m['status'] in ['LIVE', 'FINISHED'] else m['kickoff'],
                "Away Team": f"{m['away_team']} {m['away_logo']}",
                "Status": m["status"]
            } for m in raw_matches
        ])
        st.dataframe(df_matches, width="stretch", hide_index=True)
    else:
        st.warning("No matches available for the selected leagues and date.")

# ==============================================================================
# TAB 2: MATCH STATS & LINEUPS
# ==============================================================================
with main_tab2:
    st.subheader("🔍 Detailed Match Center")
    
    if raw_matches:
        selected_match_str = st.selectbox(
            "Select Match to Inspect:",
            options=[f"{m['home_team']} vs {m['away_team']} ({m['league']})" for m in raw_matches]
        )
        
        selected_index = [f"{m['home_team']} vs {m['away_team']} ({m['league']})" for m in raw_matches].index(selected_match_str)
        selected_game = raw_matches[selected_index]
        
        st.markdown(f"""
        <div class="card" style="text-align: center; background: linear-gradient(135deg, #1E293B, #0F172A); color: white;">
            <h4>{selected_game['league']}</h4>
            <h2>{selected_game['home_team']} &nbsp; <span style="color:#10B981;">{selected_game['score']['home'] if selected_game['score']['home'] is not None else 0} - {selected_game['score']['away'] if selected_game['score']['away'] is not None else 0}</span> &nbsp; {selected_game['away_team']}</h2>
            <p>Status: {selected_game['status']} {f'({selected_game["elapsed"]}\')' if selected_game['status'] == 'LIVE' else ''}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_lineup, col_stats = st.columns([1, 1])
        
        with col_lineup:
            st.markdown("### 📋 Starting Lineups")
            l_col1, l_col2 = st.columns(2)
            
            with l_col1:
                st.markdown(f"**{selected_game['home_team']}** (4-3-3)")
                home_players = ["Goalkeeper", "Defender 1", "Defender 2", "Defender 3", "Defender 4", "Midfielder 1", "Midfielder 2", "Midfielder 3", "Forward 1", "Forward 2", "Forward 3"]
                for p in home_players:
                    st.caption(f"👕 {p}")
                    
            with l_col2:
                st.markdown(f"**{selected_game['away_team']}** (4-2-3-1)")
                away_players = ["Goalkeeper", "Defender 1", "Defender 2", "Defender 3", "Defender 4", "Midfielder 1", "Midfielder 2", "Midfielder 3", "Forward 1", "Forward 2", "Forward 3"]
                for p in away_players:
                    st.caption(f"👕 {p}")

        with col_stats:
            st.markdown("### 📊 Team Match Statistics")
            possession_home = random.randint(40, 65)
            possession_away = 100 - possession_home
            
            st.write(f"**Possession (%):** {possession_home}% vs {possession_away}%")
            st.progress(possession_home / 100)
            
            st.write("**Shots on Target:** 6 vs 4")
            st.progress(0.6)
            
            st.write("**Pass Accuracy:** 88% vs 82%")
            st.progress(0.88)
            
            st.write("**Corners:** 5 vs 3")
            st.progress(0.62)

        st.divider()
        st.markdown("### 🏃 Individual Player Performance Metrics")
        player_data = [
            {"Player": "Star Forward", "Team": selected_game['home_team'], "Rating": 8.4, "Goals": 1, "Assists": 1, "Passes": "34/40", "Tackles": 2},
            {"Player": "Playmaker", "Team": selected_game['home_team'], "Rating": 7.9, "Goals": 1, "Assists": 0, "Passes": "52/58", "Tackles": 1},
            {"Player": "Attacking Mid", "Team": selected_game['away_team'], "Rating": 8.1, "Goals": 1, "Assists": 0, "Passes": "41/46", "Tackles": 0},
            {"Player": "Central Mid", "Team": selected_game['away_team'], "Rating": 7.2, "Goals": 0, "Assists": 1, "Passes": "60/68", "Tackles": 4},
        ]
        st.table(pd.DataFrame(player_data))
    else:
        st.info("Please select at least one league to view match statistics.")

# ==============================================================================
# TAB 3: PREDICTIONS & ANALYTICS
# ==============================================================================
with main_tab3:
    st.subheader("🔮 Predictive Analytics & AI Insights")
    
    if raw_matches:
        pred_game = st.selectbox(
            "Select Game for Win/Draw Probability Analysis:",
            options=[f"{m['home_team']} vs {m['away_team']}" for m in raw_matches],
            key="pred_select"
        )
        
        st.markdown("#### Match Result Probability Matrix")
        
        p_home = random.randint(35, 55)
        p_draw = random.randint(20, 30)
        p_away = 100 - (p_home + p_draw)
        
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric(label="Home Win Prob.", value=f"{p_home}%", delta="+3% form")
        col_p2.metric(label="Draw Prob.", value=f"{p_draw}%")
        col_p3.metric(label="Away Win Prob.", value=f"{p_away}%", delta="-2% form")
        
        st.markdown("#### Expected Goals (xG) & Scoreline Prediction")
        c_xg1, c_xg2 = st.columns(2)
        with c_xg1:
            st.info("🎯 **Predicted Scoreline:** 2 - 1")
        with c_xg2:
            st.success("📈 **Expected Goals (xG):** Home (1.85) - Away (1.12)")

# ==============================================================================
# TAB 4: ODDS CENTER
# ==============================================================================
with main_tab4:
    st.subheader("💰 Live & Pre-Match Odds Intelligence")
    
    if raw_matches:
        odds_game = st.selectbox(
            "Select Game to View Bookmaker Odds:",
            options=[f"{m['home_team']} vs {m['away_team']} [{m['status']}]" for m in raw_matches],
            key="odds_select"
        )
        
        odds_index = [f"{m['home_team']} vs {m['away_team']} [{m['status']}]" for m in raw_matches].index(odds_game)
        matched_game = raw_matches[odds_index]
        
        if matched_game['status'] == 'LIVE':
            st.warning("⚡ **IN-PLAY ODDS (Real-time Dynamic Fluctuation)**")
            st.caption("Odds update automatically as match momentum shifts.")
            
            o_col1, o_col2, o_col3 = st.columns(3)
            o_col1.metric("Home Win (In-Play)", "1.65", delta="-0.25 (Favorite)")
            o_col2.metric("Draw (In-Play)", "3.80", delta="+0.40")
            o_col3.metric("Away Win (In-Play)", "5.25", delta="+1.10")
            
        else:
            st.info("📅 **PRE-MATCH ODDS (Opening vs Current Market)**")
            
            o_col1, o_col2, o_col3 = st.columns(3)
            o_col1.metric("Home Win", "2.10", delta="Opening 2.20")
            o_col2.metric("Draw", "3.40", delta="Opening 3.30")
            o_col3.metric("Away Win", "3.10", delta="Opening 2.95")

        st.markdown("#### Market Over/Under 2.5 Goals")
        ou_col1, ou_col2 = st.columns(2)
        ou_col1.metric("Over 2.5 Goals", "1.85")
        ou_col2.metric("Under 2.5 Goals", "1.95")

st.divider()
st.caption("PitchSide Analytics Dashboard • Powered by Streamlit, Football-Data.org & API-Football")