
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
    st.subheader("Engineering Trend — Equipment View")
    st.caption("Select an equipment code to display all mapped PLC parameters together. Each parameter keeps its own trend and engineering unit.")

    area_options=["All"]+sorted([x for x in master["Area"].unique() if x])
    selected_area=st.selectbox("Area",area_options,key="trend_area")

    area_view=master if selected_area=="All" else master[master["Area"]==selected_area]
    eq_codes=sorted([x for x in area_view["Equipment Code"].unique() if x])
    if not eq_codes:
        st.warning("No equipment code is mapped for this selection yet.")
    else:
        selected_eq=st.selectbox("Equipment Code",eq_codes,key="trend_equipment")
        eq_view=area_view[area_view["Equipment Code"]==selected_eq].copy()

        eq_name=eq_view["Equipment"].replace("",np.nan).dropna().iloc[0] if (eq_view["Equipment"].replace("",np.nan).notna().any()) else "Equipment description not yet mapped"
        st.markdown(f"### {selected_eq}")
        st.caption(f"{eq_name} • {len(eq_view)} associated PLC tags")

        # Date range
        min_d,max_d=df["ArchiveTime"].min().date(),df["ArchiveTime"].max().date()
        c1,c2,c3=st.columns([1,1,2])
        start=c1.date_input("Start Date",min_d,min_value=min_d,max_value=max_d,key="trend_start")
        end=c2.date_input("End Date",max_d,min_value=min_d,max_value=max_d,key="trend_end")
        if start>end:
            st.error("Start Date cannot be later than End Date.")
        else:
            # Only tags actually present in historical data
            eq_tags=[t for t in eq_view["PLC Tag"].tolist() if t in df.columns]
            if not eq_tags:
                st.warning("No historical PLC data found for the mapped tags of this equipment.")
            else:
                # Parameter grouping: prefer suggested parameter, otherwise instrument type/tag prefix.
                rows=[]
                for _,meta in eq_view.iterrows():
                    tag=meta["PLC Tag"]
                    if tag not in df.columns: continue
                    d=df[(df["ArchiveTime"].dt.date>=start)&(df["ArchiveTime"].dt.date<=end)][["ArchiveTime",tag]].copy()
                    d[tag]=pd.to_numeric(d[tag],errors="coerce")
                    s=d[tag].dropna()
                    if len(s)==0: continue
                    rows.append((meta, d, s))

                st.markdown("#### Equipment Parameter Summary")
                summary=[]
                for meta,d,s in rows:
                    summary.append({
                        "PLC Tag":meta["PLC Tag"],
                        "Parameter":meta["Suggested Parameter"] or meta["Instrument Type"] or "PLC Parameter",
                        "Unit":meta["Suggested Unit"] or "—",
                        "Current":s.iloc[-1],
                        "Average":s.mean(),
                        "Min":s.min(),
                        "Max":s.max(),
                        "Confidence":meta["Confidence"] or "Low"
                    })
                if summary:
                    st.dataframe(pd.DataFrame(summary),use_container_width=True,height=260)

                st.markdown("#### Parameter Trends")
                # Render one chart per parameter/tag, keeping unlike units separate.
                for meta,d,s in rows:
                    tag=meta["PLC Tag"]
                    label=meta["Suggested Parameter"] or meta["Instrument Type"] or tag
                    unit=meta["Suggested Unit"] or ""
                    st.markdown(f"**{tag} — {label}**")
                    st.caption(
                        f"Unit: {unit or 'Not configured'} | "
                        f"Confidence: {meta['Confidence'] or 'Low'} | "
                        f"Reference: {meta['Reference Source'] or 'Not available'}"
                    )
                    chart=d.set_index("ArchiveTime")[tag].dropna()
                    if len(chart):
                        st.line_chart(chart,height=230)
                    else:
                        st.info("No valid data in selected date range.")

                st.info("Trend panels are intentionally separated by parameter/unit. Do not combine flow, temperature, pressure and vibration on one Y-axis.")

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
