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
    st.session_state.teams = [""] * 12
    
    st.session_state.vault = [""] * 36

# 1. Create a Header Row for Alignment
h1, h2, h3, h4 = st.columns([2, 1, 1, 1])
h1.markdown("**TEAM NAME**")
h2.markdown("**SLOT 1**")
h3.markdown("**SLOT 2**")
h4.markdown("**SLOT 3**")

#2. Create the 12 Rows
for i in range(12):
    with st.container():
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        
        with c1:st.session_state.teams[i] = st.text_input(f"T{i}", value=st.session_state.teams[i], key=f"team_{i}", label_visibility="collapsed")
        
        with c2:
            idx2 = i *3
            st.session_state.vault[idx2] = st.text_input(f"S1_{i}", value=st.session_state.vault[idx2], key=f"s1_{i}", label_visibility="collapsed")
            
        with c3:idx3 = i * 3 + 1
            st.session_state.vault[idx3] = st.text_input(f"S2_{i}", value=st.session_state.vault[idx3], key=f"s2_{i}", label_visibility="collapsed")
            
        with c4:
            idx4 = i * 3 + 2
            st.session_state.vault[idx4] = st.text_input(f"S3_{i}", value=st.session_state.vault[idx4], key=f"s3_{i}", label_visibility="collapsed")

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
