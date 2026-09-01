
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import re

st.set_page_config(page_title="OPP Engineering Monitoring", page_icon="⚙️", layout="wide")

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
MASTER_PATH = ROOT / "config" / "tag_master.csv"

@st.cache_data
def load_data():
    files = sorted(DATA_DIR.glob("*.csv.gz"))
    frames = [pd.read_csv(f, parse_dates=["ArchiveTime"]) for f in files]
    return pd.concat(frames, ignore_index=True).sort_values("ArchiveTime")

@st.cache_data
def load_master():
    return pd.read_csv(MASTER_PATH)

df = load_data()
master = load_master()
tags = master["PLC Tag"].tolist()

st.title("⚙️ OPP Engineering Monitoring")
st.caption("Phase 2 — Tag Master + Historical PLC Trend")

# Top metrics
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Historical Records", f"{len(df):,}")
c2.metric("PLC Tags", f"{len(tags):,}")
c3.metric("Areas Detected", f"{master['Area'].replace('', np.nan).nunique():,}")
c4.metric("Mapped Tags", f"{(master['Mapping Status']=='Mapped').sum():,}")
c5.metric("Needs Review", f"{(master['Mapping Status']!='Mapped').sum():,}")

st.divider()

page = st.sidebar.radio("Navigation", ["Dashboard", "Tag Master", "Trend", "Data Import"])

if page == "Dashboard":
    st.subheader("Process Overview")
    area_counts = master.loc[master["Area"]!="", "Area"].value_counts().sort_index()
    cols = st.columns(4)
    for i, (area, count) in enumerate(area_counts.items()):
        cols[i % 4].metric(area, f"{count} tags")

    st.info("Tag-to-equipment mapping is intentionally left as 'Needs Review' until engineering mapping is confirmed. The inferred Area is based only on explicit area codes in PLC tag names.")

elif page == "Tag Master":
    st.subheader("PLC Tag Master")
    st.write("Gunakan tabel ini sebagai kamus resmi tag. AI hanya mengisi inferensi awal; Equipment, Parameter, Unit, dan limit engineering harus dikonfirmasi.")

    search = st.text_input("Search PLC Tag / Display Name / Equipment")
    area_filter = st.selectbox("Area", ["All"] + sorted([x for x in master["Area"].dropna().unique() if x]))
    status_filter = st.selectbox("Mapping Status", ["All", "Needs Review", "Mapped"])

    view = master.copy()
    if search:
        mask = view.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
        view = view[mask]
    if area_filter != "All":
        view = view[view["Area"] == area_filter]
    if status_filter != "All":
        view = view[view["Mapping Status"] == status_filter]

    st.dataframe(view, use_container_width=True, height=600)
    st.download_button(
        "Download Tag Master CSV",
        data=master.to_csv(index=False).encode("utf-8"),
        file_name="OPP_Tag_Master.csv",
        mime="text/csv"
    )

elif page == "Trend":
    st.subheader("Engineering Trend")
    area = st.selectbox("Area", ["All"] + sorted([x for x in master["Area"].dropna().unique() if x]))
    candidate = master if area == "All" else master[master["Area"] == area]
    tag = st.selectbox("PLC Tag", candidate["PLC Tag"].tolist())
    row = master[master["PLC Tag"] == tag].iloc[0]

    min_date = df["ArchiveTime"].min().date()
    max_date = df["ArchiveTime"].max().date()
    start = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    end = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

    d = df[(df["ArchiveTime"].dt.date >= start) & (df["ArchiveTime"].dt.date <= end)][["ArchiveTime", tag]].copy()
    s = d[tag].dropna()

    st.caption(f"Area: {row['Area'] or 'Unassigned'}  |  Equipment: {row['Equipment'] or 'Unassigned'}  |  Unit: {row['Unit'] or 'Not configured'}")
    if len(s):
        a,b,c,d1 = st.columns(4)
        a.metric("Average", f"{s.mean():,.3f}")
        b.metric("Minimum", f"{s.min():,.3f}")
        c.metric("Maximum", f"{s.max():,.3f}")
        d1.metric("Samples", f"{len(s):,}")
        st.line_chart(d.set_index("ArchiveTime")[tag], height=450)
        if s.nunique() <= 1:
            st.warning("Tag constant pada periode ini. Jangan otomatis menganggapnya fault; verifikasi fungsi tag.")
    else:
        st.warning("Tidak ada data valid pada periode terpilih.")

elif page == "Data Import":
    st.subheader("Daily PLC Excel Import")
    uploaded = st.file_uploader("Upload daily PLC export (.xlsx)", type=["xlsx"])
    if uploaded:
        try:
            incoming = pd.read_excel(uploaded)
            st.write(f"File: **{uploaded.name}**")
            st.write(f"Rows: **{len(incoming):,}** | Columns: **{len(incoming.columns):,}**")
            if "ArchiveTime" not in incoming.columns:
                st.error("ArchiveTime tidak ditemukan.")
            else:
                incoming["ArchiveTime"] = pd.to_datetime(incoming["ArchiveTime"], errors="coerce")
                known = set(df["ArchiveTime"])
                new_count = int((~incoming["ArchiveTime"].isin(known)).sum())
                dup_count = int(incoming["ArchiveTime"].duplicated().sum())
                bad_count = int(incoming["ArchiveTime"].isna().sum())
                a,b,c = st.columns(3)
                a.metric("New timestamps", f"{new_count:,}")
                b.metric("Duplicate timestamps", f"{dup_count:,}")
                c.metric("Invalid timestamps", f"{bad_count:,}")
                st.dataframe(incoming.head(20), use_container_width=True)
                st.info("Import validation aktif. Persistent database append akan menjadi tahap berikutnya.")
        except Exception as e:
            st.error(str(e))
