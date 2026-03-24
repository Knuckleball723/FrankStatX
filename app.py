import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- CONFIG ---
LEAGUE_ID = "38731"
ESPN_URL = f"https://fantasy.espn.com/baseball/recentactivity?leagueId={LEAGUE_ID}"

st.set_page_config(page_title="FrankStatX Web", layout="wide")
st.title("⚾ FrankStatX: Prospect Watchdog")


from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONNECT TO GOOGLE SHEETS ---
conn= st.connection("gsheets", type=GSheetsConnection)

# Read the data (ttl=0 ensures it's always fresh)
df = conn.read(spreadsheet="https://docs.google.com/spreadsheets/d/14QoWSq3pl2uxT1O7lrOYU9cRdEjSVp4ikwOetWqf-j8/edit?usp=sharing", ttl=0)

# --- THE VAULT UI ---
st.subheader("12-Team Protected Vault (Live Sync)")

# Create a list to hold the updated values
updated_data= []

h1, h2, h3, h4 = st.columns([2, 1, 1, 1])
h1.write("**TEAM NAME**")
h2.write("**SLOT 1**")
h3.write("**SLOT 2**")
h4.write("**SLOT 3**")

for i in range(12):
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    
    # Get current values from the Google Sheet (or emptystring if NaN)
    t_val = str(df.iloc[i, 0]) if not pd.isna(df.iloc[i, 0]) else ""
    s1_val = str(df.iloc[i, 1]) if not pd.isna(df.iloc[i, 1]) else ""
    s2_val = str(df.iloc[i, 2]) if not pd.isna(df.iloc[i, 2]) else ""
    s3_val = str(df.iloc[i, 3]) if not pd.isna(df.iloc[i, 3]) else ""

    with c1:
        t = st.text_input(f"T{i}", value=t_val, key=f"t_{i}", label_visibility="collapsed")
    with c2:
        s1 = st.text_input(f"S1_{i}", value=s1_val, key=f"s1_{i}", label_visibility="collapsed")
    with c3:
        s2 = st.text_input(f"S2_{i}", value=s2_val, key=f"s2_{i}", label_visibility="collapsed")
    with c4:
        s3 = st.text_input(f"S3_{i}", value=s3_val, key=f"s3_{i}", label_visibility="collapsed")updated_data.append([t, s1, s2, s3])

# --- SAVE & SCAN BUTTON ---
if st.button("💾 SAVE TO SHEET & SCAN ESPN"):
    # 1. Update the Google Sheet
    new_df = pd.DataFrame(updated_data, columns=['TeamName', 'Slot1', 'Slot2', 'Slot3'])
    conn.update(spreadsheet="https://docs.google.com/spreadsheets/d/14QoWSq3pl2uxT1O7lrOYU9cRdEjSVp4ikwOetWqf-j8/edit?usp=sharing", data=new_df)
    st.sidebar.success("✅ Saved to Google Sheets!")
    
    # 2. Run the ESPN Scan
    # (Make sure your check_espn() function uses the 'updated_data'list)
    st.session_state.vault = [item for sublist in updated_data for item in sublist[1:]]
    check_espn()

# --- EMAIL CONFIG ---
EMAIL_SENDER = "knuckleballinc@gmail.com"
EMAIL_RECEIVER = "knuckleballinc@gmail.com"
EMAIL_PASSWORD = "tqaa pukr xgrd nfrk"

def send_email_alert(message):
    try:
        msg = MIMEText(message)
        msg['Subject'] = "🚨 FrankStatX: PROSPECT ALERT!"
        msg['From'] = EMAIL_SENDERmsg['To'] = EMAIL_RECEIVER
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        st.sidebar.success("📧 Email Alert Sent!")
    except Exception as e:
        st.sidebar.error(f"Email failed: {e}")

# --- THE SCOUT LOGIC ---
def check_espn():
    try:
        response = requests.get(ESPN_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        
        # Filter out empty slots
        protected_ids = [p for p in st.session_state.vault if p.strip() != ""]
        matches = []
        
        for row in rows:
            row_text = row.get_text()
            for p_id in protected_ids:
                if p_id in row_text and len(p_id) > 2:
                    alert_msg = f"MATCH FOUND: Prospect {p_id} was moved!"
                    matches.append(alert_msg)
                    # SEND THE EMAIL ALERTsend_email_alert(alert_msg)
        
        if matches:
            for m in matches:
                st.error(f"🚨 {m}")
        else:
            st.success("✅ No protected prospects moved.")
            
    except Exception as e:
        st.error(f"Error scanning ESPN: {e}")

# --- SCAN BUTTON ---
if st.button("💾 SAVE & SCAN NOW"):
    st.info("Scanning last 50 ESPN transactions...")
    check_espn()

st.info("Note: Do not refresh the page after entering newIDs manually, or they will clear.")
