import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIG ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/14QoWSq3pl2uxT1O7lrOYU9cRdEjSVp4ikwOetWqf-j8/edit?usp=sharing"

st.set_page_config(page_title="FrankStatX Vault", layout="wide")
st.title("⚾ FrankStatX: Prospect Vault")# --- CONNECT TO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Read the data
try:
    df = conn.read(spreadsheet=SHEET_URL, ttl=0)
except Exception as e:
    st.error("Connection Error. Make sure you shared the sheet with the Service Account email.")
    st.stop()

# --- THE VAULT UI ---
st.subheader("Live Prospect Entry")
updated_data = []

# New Header Labels
h1, h2, h3, h4 = st.columns([2, 2, 1, 2])
h1.write("**PLAYER**")
h2.write("**TEAM NAME / OWNER**")
h3.write("**BID $**")
h4.write("**TIMESTAMP**")

# Display 20 rows for entry
fori in range(20):
    c1, c2, c3, c4 = st.columns([2, 2, 1, 2])
    
    # Safety check for existing data
    p_val = str(df.iloc[i, 0]) if i <len(df) and not pd.isna(df.iloc[i, 0]) else ""
    t_val = str(df.iloc[i, 1]) if i < len(df) and len(df.columns) > 1 and not pd.isna(df.iloc[i, 1]) else ""
    b_val = str(df.iloc[i, 2]) if i < len(df) and len(df.columns) > 2 and not pd.isna(df.iloc[i, 2]) else ""
    ts_val= str(df.iloc[i, 3]) if i < len(df) and len(df.columns) > 3 and not pd.isna(df.iloc[i, 3]) else ""

    with c1:
        p = st.text_input(f"P{i}", value=p_val, key=f"p_{i}", label_visibility="collapsed")
    with c2:
        t = st.text_input(f"T{i}", value=t_val, key=f"t_{i}", label_visibility="collapsed")
    with c3:
        b = st.text_input(f"B{i}", value=b_val, key=f"b_{i}", label_visibility="collapsed")
    with c4:
        ts = st.text_input(f"TS{i}", value=ts_val, key=f"ts_{i}", label_visibility="collapsed")
    
    updated_data.append([p, t, b, ts])

# --- SAVE BUTTON ---
if st.button("💾 SAVE"):
    new_df = pd.DataFrame(updated_data, columns=['Player', 'Team Name / Owner', 'Bid $', 'Timestamp'])
    conn.update(spreadsheet=SHEET_URL, data=new_df)
    st.success("✅ Vault updated successfully!")
    st.balloons()

st.info("Note: Changes saved here update the master Google Sheet for everyone.")
