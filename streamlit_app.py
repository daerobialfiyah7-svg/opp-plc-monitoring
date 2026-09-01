
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(page_title="OPP Engineering Monitoring", page_icon="⚙️", layout="wide")
ROOT=Path(__file__).resolve().parent
DATA_DIR=ROOT/"data"
MASTER_PATH=ROOT/"config"/"tag_master.csv"

@st.cache_data
def load_data():
    files=sorted(DATA_DIR.glob("*.csv.gz"))
    return pd.concat([pd.read_csv(f,parse_dates=["ArchiveTime"]) for f in files],ignore_index=True).sort_values("ArchiveTime")

@st.cache_data
def load_master():
    return pd.read_csv(MASTER_PATH)

df=load_data()
master=load_master()
params=[c for c in df.columns if c!="ArchiveTime"]

st.markdown("""
<style>
.block-container {padding-top:2rem; padding-bottom:3rem;}
[data-testid="stMetricValue"] {font-size:1.75rem;}
</style>
""",unsafe_allow_html=True)

st.title("⚙️ OPP Engineering Monitoring")
st.caption("Phase 2.1 — PLC Tag Master enriched with Equipment List & Instrument List")

c1,c2,c3,c4,c5=st.columns(5)
c1.metric("Historical Records",f"{len(df):,}")
c2.metric("PLC Tags",f"{len(params):,}")
c3.metric("High Confidence",f"{(master['Confidence']=='High').sum():,}")
c4.metric("Medium Confidence",f"{(master['Confidence']=='Medium').sum():,}")
c5.metric("Needs Engineering Review",f"{(master['Confidence']=='Low').sum():,}")

st.divider()
page=st.sidebar.radio("Navigation",["Dashboard","Tag Master","Engineering Trend","Data Import"])

if page=="Dashboard":
    st.subheader("Reference-Based Process Overview")
    area_counts=master[master["Area"].fillna("")!=""]["Area"].value_counts().sort_index()
    cols=st.columns(4)
    for i,(area,n) in enumerate(area_counts.items()):
        cols[i%4].metric(area,f"{n} tags")

    st.markdown("### Mapping Evidence")
    e1,e2,e3=st.columns(3)
    e1.metric("Exact Instrument List",f"{(master['Confidence']=='High').sum():,}")
    e2.metric("Equipment Code Pattern",f"{(master['Confidence']=='Medium').sum():,}")
    e3.metric("No Direct Reference",f"{(master['Confidence']=='Low').sum():,}")
    st.info("High confidence means the PLC tag was found exactly in the Instrument List. Medium means the PLC tag contains an equipment-code pattern found in the OPP Equipment List. Low means no direct reference was found in the supplied reference documents. All remain 'Needs Review' until engineering approval.")

elif page=="Tag Master":
    st.subheader("Reference-Enriched PLC Tag Master")
    st.caption("Suggested fields are evidence-based. Do not treat them as final engineering approval until validated.")

    search=st.text_input("Search tag / equipment / description")
    area=st.selectbox("Area",["All"]+sorted(master.loc[master["Area"].notna() & (master["Area"]!=""),"Area"].unique()))
    conf=st.selectbox("Confidence",["All","High","Medium","Low"])

    view=master.copy()
    if search:
        m=view.astype(str).apply(lambda col: col.str.contains(search,case=False,na=False)).any(axis=1)
        view=view[m]
    if area!="All": view=view[view["Area"]==area]
    if conf!="All": view=view[view["Confidence"]==conf]

    st.dataframe(view,use_container_width=True,height=620)
    st.download_button("Download Reference-Enriched Tag Master",
                       master.to_csv(index=False).encode("utf-8"),
                       "OPP_Tag_Master_Reference_Mapping.csv","text/csv")

elif page=="Engineering Trend":
    st.subheader("Engineering Trend")
    area=st.selectbox("Area",["All"]+sorted(master.loc[master["Area"].notna() & (master["Area"]!=""),"Area"].unique()))
    candidates=master if area=="All" else master[master["Area"]==area]
    tag=st.selectbox("PLC Tag",candidates["PLC Tag"].tolist())
    r=master[master["PLC Tag"]==tag].iloc[0]

    min_date=df["ArchiveTime"].min().date()
    max_date=df["ArchiveTime"].max().date()
    start=st.date_input("Start Date",min_date,min_value=min_date,max_value=max_date)
    end=st.date_input("End Date",max_date,min_value=min_date,max_value=max_date)

    d=df[(df["ArchiveTime"].dt.date>=start)&(df["ArchiveTime"].dt.date<=end)][["ArchiveTime",tag]]
    s=d[tag].dropna()

    st.markdown(f"**{r['PLC Tag']}**")
    st.caption(f"Area: {r['Area'] or 'Unassigned'} | Equipment: {r['Suggested Equipment'] or 'Unassigned'} | Parameter: {r['Suggested Parameter']} | Unit: {r['Suggested Unit'] or 'Not configured'}")
    if r["Reference Description"]:
        st.info(f"Reference: {r['Reference Description']}  |  Source: {r['Reference Source']}  |  Confidence: {r['Confidence']}")

    if len(s):
        a,b,c,d1=st.columns(4)
        a.metric("Average",f"{s.mean():,.3f}")
        b.metric("Minimum",f"{s.min():,.3f}")
        c.metric("Maximum",f"{s.max():,.3f}")
        d1.metric("Samples",f"{len(s):,}")
        st.line_chart(d.set_index("ArchiveTime")[tag],height=450)
    else:
        st.warning("No valid data in selected period.")

elif page=="Data Import":
    st.subheader("Daily PLC Excel Import")
    uploaded=st.file_uploader("Upload daily PLC export (.xlsx)",type=["xlsx"])
    if uploaded:
        try:
            incoming=pd.read_excel(uploaded)
            if "ArchiveTime" not in incoming.columns:
                st.error("ArchiveTime tidak ditemukan.")
            else:
                incoming["ArchiveTime"]=pd.to_datetime(incoming["ArchiveTime"],errors="coerce")
                known=set(df["ArchiveTime"])
                a,b,c=st.columns(3)
                a.metric("Rows",f"{len(incoming):,}")
                b.metric("New timestamps",f"{(~incoming['ArchiveTime'].isin(known)).sum():,}")
                c.metric("Invalid timestamps",f"{incoming['ArchiveTime'].isna().sum():,}")
                st.dataframe(incoming.head(20),use_container_width=True)
                st.info("Validation aktif. Permanent database append menjadi tahap berikutnya.")
        except Exception as e:
            st.error(str(e))
