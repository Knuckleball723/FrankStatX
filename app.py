import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

# --- CONFIGURATION ---
LEAGUE_ID = "38731"
ESPN_URL = f"https://fantasy.espn.com/baseball/recentactivity?leagueId={LEAGUE_ID}"

st.set_page_config(page_title="FrankStatX Web Vault", page_icon="⚾")

st.title("⚾ FrankStatX: Prospect Watchdog")
st.subheader("12-Team Protected Vault")

# --- THE VAULT (UI) ---
if 'vault' not in st.session_state:
    # We need 12 Team Names and 36 ID Slots
    st.session_state.teams = [""] * 12
    st.session_state.vault = [""] * 36

# Create 12 rows (One for each team)
for i in range(12):
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1]) # Team name gets more space
    
    with col1:
        st.session_state.teams[i] = st.text_input(f"Team {i+1}", value=st.session_state.teams[i],key=f"team_{i}")
    
    with col2:
        idx = i * 3
        st.session_state.vault[idx] = st.text_input(f"S1", value=st.session_state.vault[idx], key=f"s1_{i}", label_visibility="collapsed")
        
    with col3:
        idx = i * 3 + 1
        st.session_state.vault[idx] = st.text_input(f"S2", value=st.session_state.vault[idx], key=f"s2_{i}", label_visibility="collapsed")
        
    with col4:
        idx = i * 3 + 2
        st.session_state.vault[idx] = st.text_input(f"S3", value=st.session_state.vault[idx], key=f"s3_{i}", label_visibility="collapsed")

# --- THE SCOUT (LOGIC) ---
def check_espn(protected_ids):
    st.write(f"🔍 Scanning ESPN for {len(protected_ids)} prospects...")
    try:
        response = requests.get(ESPN_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        matches = []
        for row in rows:
            row_text = row.get_text()
            for p_id in protected_ids:
                if p_id in row_text and len(p_id) > 2:
                    matches.append(f"MATCH FOUND: Prospect {p_id} was moved!")
        return matches
    except Exception as e:
        return [f"Error connecting to ESPN: {e}"]

# --- THE BUTTONS ---if st.button("SAVE & SCAN NOW", type="primary"):
    # Filter out empty slots
    active_ids = [id for id in st.session_state.vault if id.strip() != ""]
    
    if not active_ids:
        st.warning("Vaultis empty! Enter some IDs first.")
    else:
        results = check_espn(active_ids)
        if results:
            for r in results:
                st.error(r) # Shows red alert on screen
                # TODO: Add Telegram/Discord alert here
        else:
            st.success("✅ No protected prospects moved in the last 50 transactions.")

st.info("Note: Keep this tab open to run manual scans, or we can set it to auto-run on a server.")
