
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import json

st.set_page_config(page_title="OPP PLC Monitoring", page_icon="⚙️", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

@st.cache_data
def load_data():
    files = sorted(DATA_DIR.glob("*.pkl"))
    frames = []
    for f in files:
        frames.append(pd.read_pickle(f))
    df = pd.concat(frames, ignore_index=True)
    df = df.sort_values("ArchiveTime").drop_duplicates(subset=["ArchiveTime"], keep="first")
    return df

df = load_data()

st.title("OPP Process Performance Monitoring")
st.caption("Phase 1 prototype — Historical PLC Data & Continuous Trend")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Historical Records", f"{len(df):,}")
c2.metric("PLC Parameters", f"{len(df.columns)-1:,}")
c3.metric("Data Start", df["ArchiveTime"].min().strftime("%d %b %Y %H:%M"))
c4.metric("Data End", df["ArchiveTime"].max().strftime("%d %b %Y %H:%M"))

st.divider()

# Sidebar controls
st.sidebar.header("Trend Controls")
params = [c for c in df.columns if c != "ArchiveTime"]
parameter = st.sidebar.selectbox("PLC Parameter", params, index=0)

min_dt = df["ArchiveTime"].min().date()
max_dt = df["ArchiveTime"].max().date()
start = st.sidebar.date_input("Start Date", min_dt, min_value=min_dt, max_value=max_dt)
end = st.sidebar.date_input("End Date", max_dt, min_value=min_dt, max_value=max_dt)

mask = (df["ArchiveTime"].dt.date >= start) & (df["ArchiveTime"].dt.date <= end)
trend = df.loc[mask, ["ArchiveTime", parameter]].copy()

st.subheader(f"Trend — {parameter}")
st.line_chart(trend.set_index("ArchiveTime")[parameter], height=420)

# Statistics
s = trend[parameter].dropna()
a, b, c, d, e = st.columns(5)
a.metric("Average", f"{s.mean():,.3f}")
b.metric("Minimum", f"{s.min():,.3f}")
c.metric("Maximum", f"{s.max():,.3f}")
d.metric("Std Dev", f"{s.std():,.3f}")
e.metric("Samples", f"{len(s):,}")

# Upload area
st.divider()
st.subheader("Daily PLC Excel Import")
uploaded = st.file_uploader("Upload daily PLC export (.xlsx)", type=["xlsx"])

if uploaded:
    try:
        incoming = pd.read_excel(uploaded)
        st.write(f"**File:** {uploaded.name}")
        st.write(f"Rows: **{len(incoming):,}** | Columns: **{len(incoming.columns):,}**")
        if "ArchiveTime" not in incoming.columns:
            st.error("Invalid PLC file: ArchiveTime column was not found.")
        else:
            incoming["ArchiveTime"] = pd.to_datetime(incoming["ArchiveTime"], errors="coerce")
            invalid_time = int(incoming["ArchiveTime"].isna().sum())
            dup_time = int(incoming["ArchiveTime"].duplicated().sum())
            known = set(df["ArchiveTime"])
            new_records = int((~incoming["ArchiveTime"].isin(known)).sum())

            q1, q2, q3 = st.columns(3)
            q1.metric("New timestamps", f"{new_records:,}")
            q2.metric("Duplicate timestamps", f"{dup_time:,}")
            q3.metric("Invalid timestamps", f"{invalid_time:,}")

            st.dataframe(incoming.head(10), use_container_width=True)
            st.info("Phase 1 prototype: upload validation is active. Persistent import will be connected to the production database in the next phase.")
    except Exception as exc:
        st.error(f"Could not read the Excel file: {exc}")

st.divider()
st.subheader("Available PLC Tags")
search = st.text_input("Search tag", "")
shown = [p for p in params if search.lower() in p.lower()] if search else params
st.write(f"Showing **{len(shown):,}** of **{len(params):,}** tags")
st.dataframe(pd.DataFrame({"PLC Tag": shown}), use_container_width=True, height=300)
