import streamlit as st
import requestsfrom bs4 import BeautifulSoup
import time

# --- CONFIGURATION ---
LEAGUE_ID = "38731"
ESPN_URL = f"https://fantasy.espn.com/baseball/recentactivity?leagueId={LEAGUE_ID}"

st.set_page_config(page_title="FrankStatX Web Vault", page_icon="⚾")

st.title("⚾ FrankStatX: Prospect Watchdog")
st.subheader("12-Team Protected Vault")

# --- THE VAULT (UI) ---
# We create a 12x3 gridfor the IDs
if 'vault' not in st.session_state:
    st.session_state.vault = [""] * 36

cols = st.columns(3)
for i in range(36):
    with cols[i % 3]:
        st.session_state.vault[i] = st.text_input(f"Slot {i+1}", value=st.session_state.vault[i], key=f"slot_{i}")

# --- THE SCOUT (LOGIC) ---
def check_espn(protected_ids):st.write(f"🔍 Scanning ESPN for {len(protected_ids)} prospects...")
    try:
        response = requests.get(ESPN_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all transaction rows (ESPN uses specificclasses)
        rows = soup.find_all('tr', class_='Table__TR')
        
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
