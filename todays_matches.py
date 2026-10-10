import streamlit as st
import requests

# Page configuration
st.set_page_config(page_title="Today's Football Matches", page_icon="⚽", layout="wide")

st.title("⚽ Today's Football Matches")
st.markdown("Fetching live scores and fixtures for today from **football-data.org**.")

# Input for API key via sidebar (or you can prefill it / use st.secrets)
api_key = st.sidebar.text_input("Enter your Football-Data API Key", type="password")

if not api_key:
    st.warning("👈 Please enter your API key in the sidebar to load the matches.")
else:
    # Endpoint for today's matches defaults automatically to current date in UTC
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": api_key}
    
    with st.spinner("Fetching today's matches..."):
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get("matches", [])
                
                if not matches:
                    st.info("No matches scheduled for today.")
                else:
                    st.success(f"Successfully loaded {len(matches)} matches for today!")
                    st.divider()
                    
                    # Loop through and display each match cleanly
                    for match in matches:
                        competition = match.get("competition", {}).get("name", "Unknown Competition")
                        home_team = match.get("homeTeam", {}).get("name", "Home Team")
                        away_team = match.get("awayTeam", {}).get("name", "Away Team")
                        status = match.get("status", "SCHEDULED")
                        utc_date = match.get("utcDate", "")
                        
                        score = match.get("score", {})
                        home_score = score.get("fullTime", {}).get("home")
                        away_score = score.get("fullTime", {}).get("away")
                        
                        with st.container():
                            col1, col2, col3 = st.columns([3, 2, 3])
                            
                            with col1:
                                st.markdown(f"#### {home_team}")
                            
                            with col2:
                                if status in ["IN_PLAY", "PAUSED", "FINISHED"]:
                                    st.markdown(f"<h3 style='text-align: center; margin: 0;'>{home_score} - {away_score}</h3>", unsafe_allow_html=True)
                                    st.caption(f"<p style='text-align: center;'>Status: {status}</p>", unsafe_allow_html=True)
                                else:
                                    # Extract time (HH:MM) from UTC string
                                    time_str = utc_date.split("T")[1][:5] if "T" in utc_date else ""
                                    st.markdown(f"<h4 style='text-align: center; margin: 0;'>vs</h4>", unsafe_allow_html=True)
                                    st.caption(f"<p style='text-align: center;'>{time_str} UTC</p>", unsafe_allow_html=True)
                                    
                            with col3:
                                st.markdown(f"#### {away_team}")
                            
                            st.caption(f"🏆 **League:** {competition}")
                            st.divider()
                            
            else:
                st.error(f"Failed to fetch data. Status Code: {response.status_code}")
                st.json(response.json())
                
        except Exception as e:
            st.error(f"An error occurred: {e}")