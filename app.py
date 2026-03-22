import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- CONFIG ---
LEAGUE_ID = "38731"
ESPN_URL = f"https://fantasy.espn.com/baseball/recentactivity?leagueId={LEAGUE_ID}"

st.set_page_config(page_title="FrankStatX Web", layout="wide")
st.title("⚾ FrankStatX: Prospect Watchdog")

# --- INITIALIZE VAULT (Hard-Coded for Tonight) ---
if 'vault' not in st.session_state:
    # Your 12 Teams
    st.session_state.teams = ["Amato", "Cacciato", "Calise", "Callahan", "Canney", "Draper", "Ray", "Reynolds", "Townsend,J", "Townsend,K", "Utschig", "Vaccaro"]
    
    # Your current IDs (36 slots total)
    st.session_state.vault = [
        "", "", "",                # Amato
        "", "", "",# Cacciato
        "5124103", "", "",         # Calise
        "4917646", "5148963", "",  # Callahan
        "", "", "",                # Canney
        "5150947", "", "",         # Draper
        "", "", "",                # Ray
        "5218285", "", "",         # Reynolds
        "", "", "",                # Townsend,J
        "", "", "",                # Townsend,K
        "41282", "4987418", "",    # Utschig
        "4917690", "4837405", ""   # Vaccaro
    ]

# --- THE VAULT UI ---
st.subheader("12-Team Protected Vault")
h1, h2, h3, h4 = st.columns([2, 1, 1, 1])
h1.write("**TEAM NAME**")
h2.write("**SLOT 1**")
h3.write("**SLOT 2**")
h4.write("**SLOT3**")

for i in range(12):
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1:
        st.session_state.teams[i] = st.text_input(f"T{i}", value=st.session_state.teams[i], key=f"t_{i}", label_visibility="collapsed")
    with c2:
        st.session_state.vault[i*3] = st.text_input(f"S1_{i}", value=st.session_state.vault[i*3], key=f"s1_{i}", label_visibility="collapsed")
    with c3:
        st.session_state.vault[i*3+1] = st.text_input(f"S2_{i}", value=st.session_state.vault[i*3+1], key=f"s2_{i}", label_visibility="collapsed")
    with c4:
        st.session_state.vault[i*3+2] = st.text_input(f"S3_{i}", value=st.session_state.vault[i*3+2], key=f"s3_{i}", label_visibility="collapsed")

# --- THE SCOUT LOGIC ---
# (Keep your existing check_espn function and Scan Button belowthis)

import smtplib
from email.mime.text import MIMEText

# --- EMAIL CONFIG ---
EMAIL_SENDER = "your-email@gmail.com"
EMAIL_RECEIVER = "destination-email@gmail.com"
EMAIL_PASSWORD = "your-16-char-app-password"def send_email_alert(message):
    try:
        msg = MIMEText(message)
        msg['Subject'] = "🚨 FrankStatX: PROSPECT ALERT!"
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVERwith smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        st.sidebar.success("📧 Email Alert Sent!")
    except Exception as e:
        st.sidebar.error(f"Email failed: {e}")# --- THE SCOUT LOGIC ---
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
                    alert_msg = f"MATCH FOUND: Prospect{p_id} was moved!"
                    matches.append(alert_msg)
                    # --- ADD THIS LINE BELOW ---
                    send_email_alert(alert_msg)
                    
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
