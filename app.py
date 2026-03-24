import streamlit as st
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIG ---
LEAGUE_ID = "38731"
ESPN_URL = f"https://fantasy.espn.com/baseball/recentactivity?leagueId={LEAGUE_ID}"
SHEET_URL = "https://docs.google.com/spreadsheets/d/14QoWSq3pl2uxT1O7lrOYU9cRdEjSVp4ikwOetWqf-j8/edit?usp=sharing"

st.set_page_config(page_title="FrankStatX Vault", layout="wide")
st.title("⚾ FrankStatX: Prospect Vault")

# --- EMAIL CONFIG ---
EMAIL_SENDER = "knuckleballinc@gmail.com"
EMAIL_RECEIVER = "knuckleballinc@gmail.com"
EMAIL_PASSWORD = "tqaa pukr xgrd nfrk"

def send_email_alert(message):
    try:
        msg= MIMEText(message)
        msg['Subject'] = "🚨 FrankStatX: PROSPECT ALERT!"
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        st.sidebar.success("📧 Email Alert Sent!")
    except Exception as e:st.sidebar.error(f"Email failed: {e}")

# --- CONNECT TO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Read the data
try:
    df = conn.read(spreadsheet=SHEET_URL, ttl=0)
except Exception as e:
    st.error("Could not connect to Google Sheet. Check your Secrets and Sheet URL.")
    st.stop()

# --- THE VAULT UI ---
st.subheader("12-Team Protected Vault (Live Sync)")
updated_data= []

h1, h2, h3, h4 = st.columns([2, 1, 1, 1])
h1.write("**TEAM NAME**")
h2.write("**SLOT 1**")
h3.write("**SLOT 2**")
h4.write("**SLOT 3**")

for i in range(12):
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    
    # SAFETY CHECK: If row doesn't exist insheet yet, use blank
    t_val = ""
    s1_val = ""
    s2_val = ""
    s3_val = ""
    
    if i < len(df):
        t_val = str(df.iloc[i, 0]) if notpd.isna(df.iloc[i, 0]) else ""
        s1_val = str(df.iloc[i, 1]) if len(df.columns) > 1 and not pd.isna(df.iloc[i, 1]) else ""
        s2_val = str(df.iloc[i, 2]) if len(df.columns) > 2 and not pd.isna(df.iloc[i, 2]) else ""
        s3_val = str(df.iloc[i, 3]) if len(df.columns) > 3 and not pd.isna(df.iloc[i, 3]) else ""

    with c1:
        t = st.text_input(f"T{i}", value=t_val, key=f"t_{i}", label_visibility="collapsed")
    with c2:
        s1 = st.text_input(f"S1_{i}", value=s1_val, key=f"s1_{i}", label_visibility="collapsed")
    with c3:
        s2 = st.text_input(f"S2_{i}", value=s2_val, key=f"s2_{i}", label_visibility="collapsed")
    with c4:
        s3 = st.text_input(f"S3_{i}", value=s3_val, key=f"s3_{i}", label_visibility="collapsed")
    
    updated_data.append([t, s1, s2, s3])

# --- THE SCOUT LOGIC ---
def check_espn(protected_ids):
    try:
        response = requests.get(ESPN_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        matches = []
        
        for row in rows:
            row_text = row.get_text()
            for p_id in protected_ids:
                if p_id and p_id.strip() != "" and p_id in row_text and len(p_id) > 2:
                    alert_msg = f"MATCH FOUND: Prospect {p_id} was moved!"
                    matches.append(alert_msg)
                    send_email_alert(alert_msg)
        
        if matches:
            for m in matches:
                st.error(f"🚨 {m}")
        else:
            st.success("✅ No protected prospects moved.")
    except Exception as e:st.error(f"Error scanning ESPN: {e}")

# --- SAVE & SCAN BUTTON ---
if st.button("💾 SAVE TO SHEET & SCAN ESPN"):
    new_df = pd.DataFrame(updated_data, columns=['TeamName', 'Slot1', 'Slot2', 'Slot3'])
    conn.update(spreadsheet=SHEET_URL, data=new_df)
    st.sidebar.success("✅ Saved to Google Sheets!")
    
    # Flatten IDs for scanning
    flat_ids = []
    for row in updated_data:
        flat_ids.extend([row[1], row[2], row[3]])
    
    check_espn(flat_ids)

st.info("Note: Changes saved here update the master Google Sheet for everyone.")
