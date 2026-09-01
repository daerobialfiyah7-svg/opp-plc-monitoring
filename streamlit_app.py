
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="OPP PLC Monitoring", page_icon="⚙️", layout="wide")
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

@st.cache_data
def load_data():
    files = sorted(DATA_DIR.glob("*.csv.gz"))
    if not files:
        raise FileNotFoundError("No historical PLC data files (*.csv.gz) were found in the data folder.")
    frames = [pd.read_csv(f, parse_dates=["ArchiveTime"]) for f in files]
    df = pd.concat(frames, ignore_index=True).sort_values("ArchiveTime")
    df = df.drop_duplicates(subset=["ArchiveTime"], keep="first")
    return df

try:
    df = load_data()
except Exception as e:
    st.error("Historical PLC data could not be loaded.")
    st.code(str(e))
    st.info("Make sure the repository contains the data folder with the three CSV.GZ files.")
    st.stop()

st.title("OPP Process Performance Monitoring")
st.caption("Phase 1.1 — Historical PLC Data & Continuous Trend")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Historical Records", f"{len(df):,}")
c2.metric("PLC Parameters", f"{len(df.columns)-1:,}")
c3.metric("Data Start", df["ArchiveTime"].min().strftime("%d %b %Y %H:%M"))
c4.metric("Data End", df["ArchiveTime"].max().strftime("%d %b %Y %H:%M"))
st.divider()

st.sidebar.header("Trend Controls")
params = [c for c in df.columns if c != "ArchiveTime"]
parameter = st.sidebar.selectbox("PLC Parameter", params)
min_date, max_date = df["ArchiveTime"].min().date(), df["ArchiveTime"].max().date()
start = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
end = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

trend = df.loc[
    (df["ArchiveTime"].dt.date >= start) & (df["ArchiveTime"].dt.date <= end),
    ["ArchiveTime", parameter]
]
st.subheader(f"Trend — {parameter}")
st.line_chart(trend.set_index("ArchiveTime")[parameter], height=420)

s = trend[parameter].dropna()
a,b,c,d,e = st.columns(5)
a.metric("Average", f"{s.mean():,.3f}")
b.metric("Minimum", f"{s.min():,.3f}")
c.metric("Maximum", f"{s.max():,.3f}")
d.metric("Std Dev", f"{s.std():,.3f}")
e.metric("Samples", f"{len(s):,}")

st.divider()
st.subheader("Daily PLC Excel Import")
uploaded = st.file_uploader("Upload daily PLC export (.xlsx)", type=["xlsx"])
if uploaded:
    try:
        incoming = pd.read_excel(uploaded)
        if "ArchiveTime" not in incoming.columns:
            st.error("Invalid PLC file: ArchiveTime column was not found.")
        else:
            incoming["ArchiveTime"] = pd.to_datetime(incoming["ArchiveTime"], errors="coerce")
            invalid_time = int(incoming["ArchiveTime"].isna().sum())
            dup_time = int(incoming["ArchiveTime"].duplicated().sum())
            known = set(df["ArchiveTime"])
            new_records = int((~incoming["ArchiveTime"].isin(known)).sum())
            st.write(f"**File:** {uploaded.name}")
            q1,q2,q3 = st.columns(3)
            q1.metric("New timestamps", f"{new_records:,}")
            q2.metric("Duplicate timestamps", f"{dup_time:,}")
            q3.metric("Invalid timestamps", f"{invalid_time:,}")
            st.dataframe(incoming.head(10), use_container_width=True)
            st.info("Validation is active. Permanent database import is planned for Phase 2.")
    except Exception as exc:
        st.error(f"Could not read the Excel file: {exc}")

st.divider()
st.subheader("Available PLC Tags")
search = st.text_input("Search tag", "")
shown = [p for p in params if search.lower() in p.lower()] if search else params
st.write(f"Showing **{len(shown):,}** of **{len(params):,}** tags")
st.dataframe(pd.DataFrame({"PLC Tag": shown}), use_container_width=True, height=300)
