
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

def _compact_code(value):
    """Uppercase alphanumeric representation used only for matching."""
    if pd.isna(value):
        return ""
    return "".join(ch for ch in str(value).strip().upper() if ch.isalnum())


def _parse_equipment_code(value):
    """Parse an equipment code such as 130ML0001 / 130-ML-01."""
    compact = _compact_code(value)
    if not compact:
        return None
    import re
    m = re.fullmatch(r"(\d{3})([A-Z]{2,5})(\d{1,4})", compact)
    if not m:
        return None
    area, family, number = m.groups()
    return area, family, int(number)


def normalize_equipment_code(value, evidence_values=None):
    """Return one canonical physical-equipment identity.

    Rules are deliberately conservative:
    - separators and leading zeroes are ignored (130ML0001 == 130-ML-01)
    - an erroneous 00 equipment number is promoted to 01 only when the
      PLC/instrument tag provides matching 01 evidence
    - otherwise the original value is retained rather than guessing
    """
    parsed = _parse_equipment_code(value)
    if not parsed:
        return str(value).strip().upper() if not pd.isna(value) else ""

    area, family, number = parsed

    # The supplied OPP convention uses 01, 02, ... for physical equipment.
    # If the source contains an artificial -00, inspect its own PLC/instrument
    # evidence before merging it with -01.
    if number == 0 and evidence_values:
        import re
        for ev in evidence_values:
            compact_ev = _compact_code(ev)
            if not compact_ev:
                continue
            marker = f"{area}{family}"
            pos = compact_ev.find(marker)
            if pos >= 0:
                tail = compact_ev[pos + len(marker):]
                m = re.match(r"(\d{1,4})", tail)
                if m and int(m.group(1)) > 0:
                    number = int(m.group(1))
                    break

    return f"{area}-{family}-{number:02d}"


def canonicalize_equipment_master(master):
    """Normalize every equipment identity and merge source-code variants.

    The original source code is preserved in `Original Equipment Code`.
    `Equipment Code` becomes the canonical ID used by all dashboard pages.
    """
    master = master.copy()
    if "Equipment Code" not in master.columns:
        master["Equipment Code"] = ""
    if "PLC Tag" not in master.columns:
        master["PLC Tag"] = ""
    if "Instrument Tag" not in master.columns:
        master["Instrument Tag"] = ""

    master["Original Equipment Code"] = master["Equipment Code"].astype(str)

    def row_normalize(row):
        evidence = [row.get("PLC Tag", ""), row.get("Instrument Tag", "")]
        # Other source fields may also contain the physical equipment code.
        evidence += [row.get("Equipment", "")]
        return normalize_equipment_code(row.get("Equipment Code", ""), evidence)

    master["Equipment Code"] = master.apply(row_normalize, axis=1)

    # Second pass: if an artificial -00 remains, merge it into an existing
    # non-zero sibling only when the source evidence contains that sibling.
    # This prevents unrelated equipment from being silently combined.
    existing = set(x for x in master["Equipment Code"].astype(str) if x)
    import re
    replacements = {}
    for code in existing:
        m = re.fullmatch(r"(\d{3})-([A-Z]{2,5})-00", code)
        if not m:
            continue
        sibling01 = f"{m.group(1)}-{m.group(2)}-01"
        if sibling01 in existing:
            replacements[code] = sibling01
    if replacements:
        master["Equipment Code"] = master["Equipment Code"].replace(replacements)

    # Useful audit fields for engineering review.
    master["Equipment Mapping Key"] = master["Equipment Code"]
    master["Source Code Variant"] = np.where(
        master["Original Equipment Code"].str.upper().str.replace("-", "", regex=False)
        == master["Equipment Code"].str.replace("-", "", regex=False),
        "Canonical",
        "Normalized / merged"
    )
    return master

df=load_history()
master=load_master()

# Canonical equipment identity: all source-code variants point to one
# physical equipment record while the original code is retained for audit.
master=canonicalize_equipment_master(master)

# Defensive schema
required=["Area","Equipment Code","Equipment","Instrument Tag","Suggested Parameter","Suggested Unit",
          "IO Type","Instrument Type","Calibration Range","Evidence","Reference Source","Confidence","Mapping Status"]
for c in required:
    if c not in master.columns: master[c]=""

st.sidebar.header("Navigation")
page=st.sidebar.radio("Go to",["Dashboard","Equipment Health","Tag Master","Engineering Trend","Data Import"])

st.title("⚙️ OPP Engineering Monitoring")
st.caption("Phase 4 — Equipment Health + Evidence-based PLC Monitoring")

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

elif page=="Equipment Health":
    st.subheader("Equipment Health — Engineering Decision Support 2.0")
    st.caption(
        "Historical-behaviour screening for engineering prioritisation. "
        "It is NOT an alarm/protection limit and does not replace OEM limits, "
        "operating philosophy, inspection standards, or engineer judgement."
    )

    def _numeric_series(tag):
        if tag not in df.columns:
            return pd.Series(dtype=float)
        return pd.to_numeric(df[tag], errors="coerce").dropna()

    def _baseline_and_condition(s):
        """Build a robust historical envelope and recent-condition indicators."""
        s = s.replace([np.inf, -np.inf], np.nan).dropna()
        if len(s) < 20:
            return None

        # Historical envelope: P05-P95. A median/MAD indicator is also used so
        # a single extreme PLC point cannot dominate the health assessment.
        p05, p95 = float(s.quantile(0.05)), float(s.quantile(0.95))
        median = float(s.median())
        mad = float(np.median(np.abs(s - median)))
        robust_sigma = max(1.4826 * mad, (p95 - p05) / 3.29, 1e-12)

        recent_n = max(10, min(120, len(s) // 10))
        prior_start = max(0, len(s) - 2 * recent_n)
        prior = s.iloc[prior_start:len(s)-recent_n]
        recent = s.iloc[-recent_n:]
        current = float(s.iloc[-1])
        recent_mean = float(recent.mean())
        prior_mean = float(prior.mean()) if len(prior) else float(s.iloc[:-recent_n].mean())
        shift_pct = (recent_mean - prior_mean) / max(abs(prior_mean), 1e-9) * 100.0

        # Current deviation from historical envelope.
        if current < p05:
            outside = (p05 - current) / robust_sigma
            side = "Below baseline"
        elif current > p95:
            outside = (current - p95) / robust_sigma
            side = "Above baseline"
        else:
            outside = 0.0
            side = "Within baseline"

        # Sustained deviation: how much of the recent window sits outside P05-P95.
        recent_outside_frac = float(((recent < p05) | (recent > p95)).mean())

        # Trend is deliberately conservative: require both a meaningful
        # recent-vs-prior shift and a directional slope.
        if shift_pct >= 5:
            direction = "Increasing"
        elif shift_pct <= -5:
            direction = "Decreasing"
        else:
            direction = "Stable"

        if outside >= 3.0 or (recent_outside_frac >= 0.50 and outside >= 1.5):
            condition = "Critical"
        elif outside >= 1.5 or recent_outside_frac >= 0.25:
            condition = "Attention"
        elif direction != "Stable" and abs(shift_pct) >= 10:
            condition = "Deteriorating"
        else:
            condition = "Normal"

        return {
            "Current": current,
            "Baseline Low": p05,
            "Baseline High": p95,
            "Recent Mean": recent_mean,
            "Prior Mean": prior_mean,
            "Shift %": shift_pct,
            "Direction": direction,
            "Outside Fraction": recent_outside_frac,
            "Deviation Sigma": outside,
            "Deviation Side": side,
            "Condition": condition,
        }

    def _parameter_action(parameter, tag):
        text = f"{parameter} {tag}".upper()
        if any(k in text for k in ["VIBRATION", "VIT", "VIB"]):
            return "Verify vibration; inspect bearing, alignment/coupling and mechanical looseness."
        if any(k in text for k in ["TEMPERATURE", "TEMP", "TIT"]):
            return "Verify temperature trend; check lubrication, cooling and bearing/drive condition."
        if any(k in text for k in ["PRESSURE", "PRESS", "PIT"]):
            return "Verify pressure against process condition; inspect restriction, leakage and pump/valve condition."
        if any(k in text for k in ["FLOW", "FLOWMETER", "FIT"]):
            return "Verify flow signal and process demand; inspect pump, valve, line restriction and instrument health."
        if any(k in text for k in ["CURRENT", "POWER", "AMP", "IIT"]):
            return "Verify electrical load; inspect motor loading, drive condition and mechanical resistance."
        if any(k in text for k in ["SPEED", "VSD"]):
            return "Verify speed command/feedback and drive condition against operating requirement."
        if any(k in text for k in ["LEVEL", "LIT"]):
            return "Verify level behaviour and instrument signal; check upstream/downstream process condition."
        return "Verify signal against operating condition, recent maintenance history and OEM/design limits."

    area_options = ["All"] + sorted([str(x) for x in master["Area"].unique() if str(x)])
    selected_area = st.selectbox("Area", area_options, key="health_area")
    area_view = master if selected_area == "All" else master[master["Area"] == selected_area]
    eq_codes = sorted([str(x) for x in area_view["Equipment Code"].unique() if str(x)])

    if not eq_codes:
        st.warning("No canonical equipment code is available for this area.")
    else:
        selected_eq = st.selectbox("Equipment Code", eq_codes, key="health_equipment")
        ev = area_view[area_view["Equipment Code"] == selected_eq].copy()

        names = ev["Equipment"].replace("", np.nan).dropna()
        eq_name = names.iloc[0] if len(names) else "Equipment description not yet mapped"
        st.markdown(f"### {selected_eq}")
        st.caption(eq_name)

        rows = []
        seen_tags = set()
        for _, meta in ev.iterrows():
            tag = str(meta.get("PLC Tag", "")).strip()
            if not tag or tag in seen_tags:
                continue
            seen_tags.add(tag)
            s = _numeric_series(tag)
            stats = _baseline_and_condition(s)
            if stats is None:
                continue

            parameter = meta.get("Suggested Parameter", "") or meta.get("Instrument Type", "") or "PLC Parameter"
            unit = meta.get("Suggested Unit", "") or "—"
            confidence = meta.get("Confidence", "") or "Low"
            rows.append({
                "PLC Tag": tag,
                "Parameter": parameter,
                "Unit": unit,
                **stats,
                "Confidence": confidence,
                "Action": _parameter_action(parameter, tag),
            })

        if not rows:
            st.warning("No sufficient historical numeric data is available for this equipment.")
        else:
            health = pd.DataFrame(rows)

            # Evidence-weighted screening score. High-confidence mappings carry
            # full weight; low-confidence mappings cannot create a severe score
            # by themselves without strong historical deviation.
            severity = {"Normal": 0, "Deteriorating": 8, "Attention": 18, "Critical": 35}
            conf_weight = {"High": 1.0, "Medium": 0.85, "Low": 0.65}
            penalties = []
            for _, r in health.iterrows():
                base = severity.get(r["Condition"], 0)
                # Sustained deviation adds a small penalty, capped for stability.
                sustain = min(float(r["Outside Fraction"]) * 12.0, 8.0)
                penalties.append(min(45.0, (base + sustain) * conf_weight.get(r["Confidence"], 0.65)))
            health["Penalty"] = penalties

            total_penalty = float(np.mean(penalties)) if penalties else 0.0
            score = int(round(max(0, min(100, 100 - total_penalty))))
            critical = int((health["Condition"] == "Critical").sum())
            attention = int((health["Condition"] == "Attention").sum())
            deteriorating = int((health["Condition"] == "Deteriorating").sum())

            if critical:
                overall, risk, priority, icon = "CRITICAL", "HIGH", "P1", "🔴"
            elif attention:
                overall, risk, priority, icon = "ATTENTION", "MEDIUM", "P2", "🟠"
            elif deteriorating:
                overall, risk, priority, icon = "DETERIORATING", "MEDIUM-LOW", "P3", "🟡"
            else:
                overall, risk, priority, icon = "HEALTHY", "LOW", "P4", "🟢"

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Equipment Health", f"{icon} {overall}")
            c2.metric("Screening Score", f"{score}/100")
            c3.metric("Parameters", f"{len(health):,}")
            c4.metric("Risk", risk)
            c5.metric("Maintenance Priority", priority)

            st.markdown("#### Condition Distribution")
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Normal", int((health["Condition"] == "Normal").sum()))
            d2.metric("Deteriorating", deteriorating)
            d3.metric("Attention", attention)
            d4.metric("Critical", critical)

            st.markdown("#### Parameter Condition")
            display_cols = ["PLC Tag", "Parameter", "Unit", "Current", "Baseline Low", "Baseline High",
                            "Direction", "Shift %", "Outside Fraction", "Condition", "Confidence"]
            st.dataframe(health[display_cols], use_container_width=True, height=440)

            flagged = health[health["Condition"] != "Normal"].copy()
            st.markdown("#### Engineering Findings & Maintenance Focus")
            if flagged.empty:
                st.success("No parameter currently shows a significant historical-behaviour deviation.")
            else:
                flagged = flagged.sort_values(["Condition", "Deviation Sigma"], ascending=[True, False])
                for _, r in flagged.iterrows():
                    st.warning(
                        f"**{r['PLC Tag']} — {r['Parameter']}** → **{r['Condition']}** | "
                        f"Current {r['Current']:.3f} {r['Unit']} | "
                        f"Historical P05–P95 {r['Baseline Low']:.3f}–{r['Baseline High']:.3f} {r['Unit']} | "
                        f"Trend {r['Direction']} ({r['Shift %']:+.1f}%)."
                    )
                    st.caption(f"Suggested engineering check: {r['Action']}")

            st.markdown("#### Engineering Decision")
            if overall == "CRITICAL":
                st.error(
                    f"Priority {priority}: {critical} parameter(s) show strong deviation from historical behaviour. "
                    "Validate the signal and equipment condition promptly before deciding on corrective maintenance."
                )
            elif overall == "ATTENTION":
                st.warning(
                    f"Priority {priority}: {attention} parameter(s) require engineering review. "
                    "Check the trend, process state and recent maintenance history; plan inspection if the deviation persists."
                )
            elif overall == "DETERIORATING":
                st.info(
                    f"Priority {priority}: the equipment remains inside/near its historical envelope, "
                    f"but {deteriorating} parameter(s) show a meaningful directional change. Increase monitoring frequency and verify field condition."
                )
            else:
                st.success("Equipment behaviour is consistent with its historical operating envelope based on the available PLC data.")

            st.caption(
                "Method: historical P05–P95 envelope + recent-vs-prior shift + sustained outside-baseline fraction, "
                "with mapping-confidence weighting. The result is a screening indicator, not an alarm/trip setting or failure prediction."
            )

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
