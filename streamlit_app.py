
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(page_title="OPP Engineering Monitoring", page_icon="⚙️", layout="wide")
ROOT=Path(__file__).resolve().parent

@st.cache_data
def load_history():
    fs=sorted((ROOT/"data").glob("*.csv.gz"))
    return pd.concat([pd.read_csv(f,parse_dates=["ArchiveTime"]) for f in fs],ignore_index=True).sort_values("ArchiveTime")

@st.cache_data
def load_master():
    return pd.read_csv(ROOT/"config"/"tag_master.csv").fillna("")

df=load_history()
master=load_master()

# Defensive schema
required=["Area","Equipment Code","Equipment","Instrument Tag","Suggested Parameter","Suggested Unit",
          "IO Type","Instrument Type","Calibration Range","Evidence","Reference Source","Confidence","Mapping Status"]
for c in required:
    if c not in master.columns: master[c]=""

st.sidebar.header("Navigation")
page=st.sidebar.radio("Go to",["Dashboard","Tag Master","Engineering Trend","Data Import"])

st.title("⚙️ OPP Engineering Monitoring")
st.caption("Phase 2.2 — Evidence-based PLC Tag Master")

high=int((master["Confidence"]=="High").sum())
medium=int((master["Confidence"]=="Medium").sum())
low=int((master["Confidence"]=="Low").sum())

a,b,c,d,e=st.columns(5)
a.metric("Historical Records",f"{len(df):,}")
b.metric("PLC Tags",f"{len(master):,}")
c.metric("High Confidence",f"{high:,}")
d.metric("Medium Confidence",f"{medium:,}")
e.metric("Low Confidence",f"{low:,}")

st.divider()

if page=="Dashboard":
    st.subheader("Reference Mapping Overview")
    st.write("Mapping menggunakan evidence dari Instrument List dan Essential Equipment List. Confidence menunjukkan kekuatan evidence, bukan final approval.")
    x,y,z=st.columns(3)
    x.metric("High","{:,}".format(high),"Exact Instrument List")
    y.metric("Medium","{:,}".format(medium),"Equipment / family evidence")
    z.metric("Low","{:,}".format(low),"Pattern only")

    st.subheader("Area Coverage")
    ac=master[master["Area"]!=""]["Area"].value_counts().sort_index()
    cols=st.columns(4)
    for i,(area,n) in enumerate(ac.items()):
        cols[i%4].metric(area,f"{n} tags")

elif page=="Tag Master":
    st.subheader("PLC Tag Master")
    q=st.text_input("Search tag / equipment / parameter")
    area=st.selectbox("Area",["All"]+sorted([x for x in master["Area"].unique() if x]))
    conf=st.selectbox("Confidence",["All","High","Medium","Low"])
    view=master.copy()
    if q:
        mask=view.astype(str).apply(lambda s:s.str.contains(q,case=False,na=False)).any(axis=1)
        view=view[mask]
    if area!="All": view=view[view["Area"]==area]
    if conf!="All": view=view[view["Confidence"]==conf]
    st.dataframe(view,use_container_width=True,height=620)
    st.download_button("Download Tag Master CSV",master.to_csv(index=False).encode("utf-8"),
                       "OPP_Tag_Master_Phase2_2.csv","text/csv")

elif page=="Engineering Trend":
    st.subheader("Engineering Trend")
    area=st.selectbox("Area",["All"]+sorted([x for x in master["Area"].unique() if x]))
    cand=master if area=="All" else master[master["Area"]==area]
    tag=st.selectbox("PLC Tag",cand["PLC Tag"].tolist())
    meta=master[master["PLC Tag"]==tag].iloc[0]

    min_d,max_d=df["ArchiveTime"].min().date(),df["ArchiveTime"].max().date()
    start=st.date_input("Start Date",min_d,min_value=min_d,max_value=max_d)
    end=st.date_input("End Date",max_d,min_value=min_d,max_value=max_d)

    d=df[(df["ArchiveTime"].dt.date>=start)&(df["ArchiveTime"].dt.date<=end)][["ArchiveTime",tag]].copy()
    s=d[tag].dropna()

    st.markdown(f"**{tag}**")
    st.caption(
        f"Area: {meta['Area'] or 'Unassigned'} | "
        f"Equipment: {meta['Equipment'] or 'Unassigned'} | "
        f"Suggested Parameter: {meta['Suggested Parameter'] or 'Unassigned'} | "
        f"Unit: {meta['Suggested Unit'] or 'Not configured'}"
    )
    st.caption(f"Confidence: {meta['Confidence'] or 'Low'} | Evidence: {meta['Reference Source']} — {meta['Evidence']}")

    if len(s):
        q1,q2,q3,q4=st.columns(4)
        q1.metric("Average",f"{s.mean():,.3f}")
        q2.metric("Minimum",f"{s.min():,.3f}")
        q3.metric("Maximum",f"{s.max():,.3f}")
        q4.metric("Samples",f"{len(s):,}")
        st.line_chart(d.set_index("ArchiveTime")[tag],height=450)
    else:
        st.warning("No valid data for selected period.")

elif page=="Data Import":
    st.subheader("Daily PLC Excel Import — Validation")
    uploaded=st.file_uploader("Upload daily PLC export (.xlsx)",type=["xlsx"])
    if uploaded:
        incoming=pd.read_excel(uploaded)
        if "ArchiveTime" not in incoming.columns:
            st.error("ArchiveTime not found.")
        else:
            incoming["ArchiveTime"]=pd.to_datetime(incoming["ArchiveTime"],errors="coerce")
            known=set(df["ArchiveTime"])
            q1,q2,q3=st.columns(3)
            q1.metric("Rows",f"{len(incoming):,}")
            q2.metric("New timestamps",f"{(~incoming['ArchiveTime'].isin(known)).sum():,}")
            q3.metric("Invalid timestamps",f"{incoming['ArchiveTime'].isna().sum():,}")
            st.dataframe(incoming.head(20),use_container_width=True)
            st.info("Permanent database append will be implemented after mapping validation.")
