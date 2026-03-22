import streamlit as st

import requests

from bs4 import BeautifulSoup

# --- CONFIG ---
LEAGUE_ID ="38731"

ESPN_URL = f"https://fantasy.espn.com/baseball/recentactivity?leagueId={LEAGUE_ID}"

st.set_page_config(page_title="FrankStatX Web", layout="wide")

st.title("⚾ FrankStatX: Prospect Watchdog")

# --- INITIALIZE VAULT ---
if'vault' not in st.session_state:
    st.session_state.teams = [""] * 12
    st.session_state.vault = [""] * 36

# --- SAVE/LOAD SYSTEM ---
st.sidebar.header("💾 Vault Management")

# 1.Create the data string to save
vault_data = ",".join(st.session_state.teams) + "|" + ",".join(st.session_state.vault)

# 2. Download Button
st.sidebar.download_button(
    label="📥 DOWNLOAD VAULT FILE",
    data=vault_data,
    file_name="frankstatx_vault.txt",
    mime="text/plain"
)

# 3. Upload Button
uploaded_file = st.sidebar.file_opener = st.sidebar.file_uploader("📤 UPLOAD VAULT FILE", type="txt")

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    try:
        teams_part, vault_part = content.split("|")
        st.session_state.teams = teams_part.split(",")
        st.session_state.vault = vault_part.split(",")
        st.sidebar.success("Vault Loaded!")
    except:
        st.sidebar.error("Invalid File")

# --- THE VAULT UI ---
st.subheader("12-Team Protected Vault")

h1, h2, h3, h4 = st.columns([2, 1, 1, 1])
h1.write("**TEAM NAME**")
h2.write("**SLOT 1**")
h3.write("**SLOT 2**")
h4.write("**SLOT 3**")

for i in range(12):
    c1, c2, c3, c4 =st.columns([2, 1, 1, 1])
    with c1:
        st.session_state.teams[i] = st.text_input(f"T{i}", value=st.session_state.teams[i], key=f"t_{i}", label_visibility="collapsed")
    with c2:
        st.session_state.vault[i*3] = st.text_input(f"S1_{i}", value=st.session_state.vault[i*3], key=f"s1_{i}", label_visibility="collapsed")
    with c3:
        st.session_state.vault[i*3+1] = st.text_input(f"S2_{i}", value=st.session_state.vault[i*3+1], key=f"s2_{i}", label_visibility="collapsed")
    with c4:
        st.session_state.vault[i*3+2] = st.text_input(f"S3_{i}", value=st.session_state.vault[i*3+2], key=f"s3_{i}", label_visibility="collapsed")

# --- THE SCOUT LOGIC ---
def check_espn(protected_ids):
    st.write(f"🔍 Scanning ESPN for {len(protected_ids)} prospects...")
    
    try:
        response =requests.get(ESPN_URL)
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
        return [f"Error: {e}"]

# --- SCAN BUTTON ---
if st.button("SAVE & SCAN NOW", type="primary"):
    active_ids = [id for id in st.session_state.vault if id.strip() != ""]
    
    if not active_ids:st.warning("Vault is empty!")
    else:
        results = check_espn(active_ids)
        if results:
            for r in results:
                st.error(r)
        else:
            st.success("✅ No protected prospects moved.")
            st.info("Note: Do not refresh the page after entering IDs, or they will clear.")
