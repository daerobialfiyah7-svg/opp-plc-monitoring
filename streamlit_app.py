import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import re

st.set_page_config(page_title="OPP Engineering Monitoring", page_icon="⚙️", layout="wide")
ROOT = Path(__file__).resolve().parent

@st.cache_data

def load_history():
    fs = sorted((ROOT / "data").glob("*.csv.gz"))
    if not fs:
        return pd.DataFrame(columns=["ArchiveTime"])
    frames = [pd.read_csv(f, parse_dates=["ArchiveTime"]) for f in fs]
    return pd.concat(frames, ignore_index=True).sort_values("ArchiveTime")

@st.cache_data

def load_master():
    return pd.read_csv(ROOT / "config" / "tag_master.csv").fillna("")


def _compact_code(value):
    if pd.isna(value):
        return ""
    return "".join(ch for ch in str(value).strip().upper() if ch.isalnum())


def _parse_equipment_code(value):
    compact = _compact_code(value)
    if not compact:
        return None
    m = re.fullmatch(r"(\d{3})([A-Z]{2,5})(\d{1,4})", compact)
    if not m:
        return None
    area, family, number = m.groups()
    return area, family, int(number)


def normalize_equipment_code(value, evidence_values=None):
    parsed = _parse_equipment_code(value)
    if not parsed:
        return str(value).strip().upper() if not pd.isna(value) else ""
    area, family, number = parsed
    if number == 0 and evidence_values:
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
    master = master.copy()
    for c in ["Equipment Code", "PLC Tag", "Instrument Tag", "Equipment"]:
        if c not in master.columns:
            master[c] = ""
    master["Original Equipment Code"] = master["Equipment Code"].astype(str)

    def row_normalize(row):
        evidence = [row.get("PLC Tag", ""), row.get("Instrument Tag", ""), row.get("Equipment", "")]
        return normalize_equipment_code(row.get("Equipment Code", ""), evidence)

    master["Equipment Code"] = master.apply(row_normalize, axis=1)

    # Merge artificial -00 only when a corresponding -01 exists.
    existing = set(x for x in master["Equipment Code"].astype(str) if x)
    replacements = {}
    for code in existing:
        m = re.fullmatch(r"(\d{3})-([A-Z]{2,5})-00", code)
        if m:
            sibling01 = f"{m.group(1)}-{m.group(2)}-01"
            if sibling01 in existing:
                replacements[code] = sibling01
    if replacements:
        master["Equipment Code"] = master["Equipment Code"].replace(replacements)

    master["Equipment Mapping Key"] = master["Equipment Code"]
    original_compact = master["Original Equipment Code"].str.upper().str.replace("-", "", regex=False)
    canonical_compact = master["Equipment Code"].str.replace("-", "", regex=False)
    master["Source Code Variant"] = np.where(original_compact == canonical_compact, "Canonical", "Normalized / merged")
    return master


# --- Derived parameter vocabulary -------------------------------------------------
PARAM_RULES = [
    (r"^(FI|FIT|FQI|FT|FTQ)", "Flow", "Flow", "m³/h"),
    (r"^(TI|TIT|TE|TT)", "Temperature", "Temperature", "°C"),
    (r"^(PI|PIT|PT)", "Pressure", "Pressure", "bar"),
    (r"^(VI|VIT|VT)", "Vibration", "Vibration", "mm/s"),
    (r"^(II|IIT|AI|AIT)", "Current", "Current", "A"),
    (r"^(PWR|PW|W|WI|WIT)", "Power", "Power", "kW"),
    (r"^(SI|SIT|ST|VSD)", "Speed", "Speed", "rpm"),
    (r"^(LI|LIT|LT)", "Level", "Level", "%"),
]


def infer_parameter(tag, source_parameter="", source_unit="", instrument_type=""):
    """Display helper only. Source mapping is never overwritten.

    If the supplied engineering mapping has a parameter/unit, it wins. If it
    is blank, a conservative PLC-prefix inference is shown and explicitly
    labelled as inferred.
    """
    p = str(source_parameter or "").strip()
    u = str(source_unit or "").strip()
    if p:
        return p, u or "—", "Source mapping"
    tag = str(tag or "").upper().strip()
    for pattern, _, label, default_unit in PARAM_RULES:
        if re.match(pattern, tag):
            return label, u or default_unit, "Inferred from PLC tag prefix"
    it = str(instrument_type or "").strip()
    if it:
        return it, u or "—", "Instrument type"
    return "PLC Parameter", u or "—", "Unclassified"


def _numeric_series(df, tag):
    if tag not in df.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[tag], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()


def baseline_condition(s):
    s = s.replace([np.inf, -np.inf], np.nan).dropna()
    if len(s) < 20:
        return None
    p05, p95 = float(s.quantile(.05)), float(s.quantile(.95))
    median = float(s.median())
    mad = float(np.median(np.abs(s - median)))
    robust_sigma = max(1.4826 * mad, (p95 - p05) / 3.29, 1e-12)
    recent_n = max(10, min(120, len(s) // 10))
    recent = s.iloc[-recent_n:]
    prior = s.iloc[max(0, len(s) - 2 * recent_n):len(s) - recent_n]
    if len(prior) == 0:
        prior = s.iloc[:-recent_n]
    current = float(s.iloc[-1])
    recent_mean = float(recent.mean())
    prior_mean = float(prior.mean()) if len(prior) else recent_mean
    shift_pct = (recent_mean - prior_mean) / max(abs(prior_mean), 1e-9) * 100

    if current < p05:
        deviation = (p05 - current) / robust_sigma
        side = "Below baseline"
    elif current > p95:
        deviation = (current - p95) / robust_sigma
        side = "Above baseline"
    else:
        deviation = 0.0
        side = "Within baseline"
    outside_fraction = float(((recent < p05) | (recent > p95)).mean())
    direction = "Increasing" if shift_pct >= 5 else "Decreasing" if shift_pct <= -5 else "Stable"

    if deviation >= 3.0 or (outside_fraction >= .50 and deviation >= 1.5):
        condition = "Critical"
    elif deviation >= 1.5 or outside_fraction >= .25:
        condition = "Attention"
    elif direction != "Stable" and abs(shift_pct) >= 10:
        condition = "Deteriorating"
    else:
        condition = "Normal"
    return {
        "Current": current, "Baseline Low": p05, "Baseline High": p95,
        "Recent Mean": recent_mean, "Prior Mean": prior_mean, "Shift %": shift_pct,
        "Direction": direction, "Outside Fraction": outside_fraction,
        "Deviation Sigma": deviation, "Deviation Side": side, "Condition": condition,
    }


def parameter_action(parameter, tag):
    text = f"{parameter} {tag}".upper()
    if any(k in text for k in ["VIBRATION", "VIT", "VIB"]):
        return "Verify vibration; inspect bearing, alignment/coupling and mechanical looseness."
    if any(k in text for k in ["TEMPERATURE", "TEMP", "TIT"]):
        return "Verify temperature trend; check lubrication, cooling and bearing/drive condition."
    if any(k in text for k in ["PRESSURE", "PRESS", "PIT"]):
        return "Verify pressure against process condition; inspect restriction, leakage and pump/valve condition."
    if any(k in text for k in ["FLOW", "FLOWMETER", "FIT", "FQI"]):
        return "Verify flow signal and process demand; inspect pump, valve, line restriction and instrument health."
    if any(k in text for k in ["CURRENT", "POWER", "AMP", "IIT", "PWR"]):
        return "Verify electrical load; inspect motor loading, drive condition and mechanical resistance."
    if any(k in text for k in ["SPEED", "VSD"]):
        return "Verify speed command/feedback and drive condition against operating requirement."
    if any(k in text for k in ["LEVEL", "LIT"]):
        return "Verify level behaviour and instrument signal; check upstream/downstream process condition."
    return "Verify signal against operating condition, recent maintenance history and OEM/design limits."



# --- Phase 5: risk / maintenance screening ---------------------------------------
def build_equipment_screening(master, df):
    """Aggregate parameter-condition evidence to one canonical equipment.

    Criticality is deliberately NOT inferred. Until an engineering criticality
    master is supplied, risk remains "Review Required" and the P1-P4 value is a
    condition-based maintenance screening priority only.
    """
    records = []
    for eq, ev in master[master["Equipment Code"].astype(str).str.strip() != ""].groupby("Equipment Code"):
        params = []
        seen = set()
        for _, meta in ev.iterrows():
            tag = str(meta.get("PLC Tag", "")).strip()
            if not tag or tag in seen:
                continue
            seen.add(tag)
            stats = baseline_condition(_numeric_series(df, tag))
            if stats is None:
                continue
            parameter, unit, source = infer_parameter(tag, meta.get("Suggested Parameter", ""), meta.get("Suggested Unit", ""), meta.get("Instrument Type", ""))
            conf = str(meta.get("Confidence", "") or "Low")
            params.append({"PLC Tag": tag, "Parameter": parameter, "Unit": unit, "Confidence": conf, "Action": parameter_action(parameter, tag), **stats})
        if not params:
            continue
        h = pd.DataFrame(params)
        counts = h["Condition"].value_counts()
        critical = int(counts.get("Critical", 0)); attention = int(counts.get("Attention", 0)); deteriorating = int(counts.get("Deteriorating", 0))
        severity = {"Normal": 0, "Deteriorating": 12, "Attention": 25, "Critical": 50}
        weights = {"High": 1.0, "Medium": .85, "Low": .65}
        h["Penalty"] = [(severity.get(r.Condition, 0) + min(r["Outside Fraction"] * 12, 8)) * weights.get(r["Confidence"], .65) for _, r in h.iterrows()]
        raw = 100 - float(h["Penalty"].mean())
        if critical:
            condition, screening_priority, icon = "CRITICAL", "P1", "🔴"
        elif attention:
            condition, screening_priority, icon = "ATTENTION", "P2", "🟠"
        elif deteriorating:
            condition, screening_priority, icon = "DETERIORATING", "P3", "🟡"
        else:
            condition, screening_priority, icon = "HEALTHY", "P4", "🟢"
        cap = {"P1":69, "P2":89, "P3":94, "P4":100}[screening_priority]
        score = int(round(max(0, min(cap, raw))))
        flagged = h[h["Condition"] != "Normal"].copy().sort_values("Deviation Sigma", ascending=False)
        top = flagged.iloc[0] if len(flagged) else None
        names = ev["Equipment"].replace("", np.nan).dropna()
        name = names.iloc[0] if len(names) else "Equipment description not yet mapped"
        records.append({
            "Equipment Code": eq, "Equipment": name, "Health": score, "Condition": condition,
            "Screening Priority": screening_priority, "Risk": "REVIEW REQUIRED",
            "Criticality": "Not configured", "Parameters": len(h), "Normal": int(counts.get("Normal",0)),
            "Deteriorating": deteriorating, "Attention": attention, "Critical": critical,
            "Top Parameter": top["Parameter"] if top is not None else "—",
            "Top Tag": top["PLC Tag"] if top is not None else "—",
            "Top Finding": top["Condition"] if top is not None else "—",
            "Top Trend": top["Direction"] if top is not None else "—",
            "Top Shift %": float(top["Shift %"]) if top is not None else 0.0,
            "Top Action": top["Action"] if top is not None else "No abnormal parameter identified."
        })
    return pd.DataFrame(records)


def criticality_template(master):
    eqs = sorted([x for x in master["Equipment Code"].astype(str).unique() if x])
    return pd.DataFrame({
        "Equipment Code": eqs,
        "Criticality": ["" for _ in eqs],
        "Criticality Basis": ["" for _ in eqs],
        "Process Function": ["" for _ in eqs],
        "Production Impact": ["" for _ in eqs],
        "Safety / Environment Impact": ["" for _ in eqs],
    })

# --- Data -------------------------------------------------------------------------
df = load_history()
master = canonicalize_equipment_master(load_master())
required = ["Area", "Equipment Code", "Equipment", "Instrument Tag", "Suggested Parameter", "Suggested Unit",
            "IO Type", "Instrument Type", "Calibration Range", "Evidence", "Reference Source", "Confidence", "Mapping Status"]
for col in required:
    if col not in master.columns:
        master[col] = ""

st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Equipment Health", "Maintenance Priority", "Tag Master", "Engineering Trend", "Data Import"])

st.title("⚙️ OPP Engineering Monitoring")
st.caption("Phase 4.1 — Equipment Health + Engineering Decision Support")

high = int((master["Confidence"] == "High").sum())
medium = int((master["Confidence"] == "Medium").sum())
low = int((master["Confidence"] == "Low").sum())

a, b, c, d, e = st.columns(5)
a.metric("Historical Records", f"{len(df):,}")
b.metric("PLC Tags", f"{len(master):,}")
c.metric("High Confidence", f"{high:,}")
d.metric("Medium Confidence", f"{medium:,}")
e.metric("Low Confidence", f"{low:,}")
st.divider()

if page == "Dashboard":
    st.subheader("OPP Engineering Overview")
    st.write("Dashboard diarahkan sebagai decision-support untuk monitoring proses, kesehatan equipment, identifikasi penyimpangan dan prioritas pemeriksaan.")
    x, y, z = st.columns(3)
    x.metric("High", f"{high:,}", "Exact / strong evidence")
    y.metric("Medium", f"{medium:,}", "Equipment / family evidence")
    z.metric("Low", f"{low:,}", "Pattern / limited evidence")
    screening = build_equipment_screening(master, df)
    if not screening.empty:
        st.subheader("Maintenance Screening")
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("P1 — Critical", int((screening["Screening Priority"] == "P1").sum()))
        p2.metric("P2 — Attention", int((screening["Screening Priority"] == "P2").sum()))
        p3.metric("P3 — Deteriorating", int((screening["Screening Priority"] == "P3").sum()))
        p4.metric("P4 — Healthy", int((screening["Screening Priority"] == "P4").sum()))
        st.caption("P1–P4 are condition-based screening priorities. Equipment criticality is not inferred and remains Engineering Review Required until validated.")
        top = screening[screening["Screening Priority"] != "P4"].sort_values(["Screening Priority", "Health"], ascending=[True, True]).head(8)
        if not top.empty:
            st.dataframe(top[["Equipment Code", "Equipment", "Health", "Condition", "Screening Priority", "Risk", "Top Parameter", "Top Finding", "Top Trend", "Top Shift %"]], use_container_width=True, hide_index=True)
    st.subheader("Area Coverage")
    ac = master[master["Area"] != ""]["Area"].value_counts().sort_index()
    cols = st.columns(4)
    for i, (area, n) in enumerate(ac.items()):
        cols[i % 4].metric(str(area), f"{n} tags")

elif page == "Equipment Health":
    st.subheader("Equipment Health — Engineering Decision Support 2.0")
    st.caption("Historical-behaviour screening. NOT an alarm/protection limit and does not replace OEM limits, operating philosophy, inspection standards, or engineer judgement.")

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
        seen = set()
        for _, meta in ev.iterrows():
            tag = str(meta.get("PLC Tag", "")).strip()
            if not tag or tag in seen:
                continue
            seen.add(tag)
            stats = baseline_condition(_numeric_series(df, tag))
            if stats is None:
                continue
            parameter, unit, parameter_source = infer_parameter(tag, meta.get("Suggested Parameter", ""), meta.get("Suggested Unit", ""), meta.get("Instrument Type", ""))
            confidence = str(meta.get("Confidence", "") or "Low")
            rows.append({"PLC Tag": tag, "Parameter": parameter, "Unit": unit, "Parameter Source": parameter_source,
                         **stats, "Confidence": confidence, "Action": parameter_action(parameter, tag)})

        if not rows:
            st.warning("No sufficient historical numeric data is available for this equipment.")
        else:
            health = pd.DataFrame(rows)
            severity = {"Normal": 0, "Deteriorating": 12, "Attention": 25, "Critical": 50}
            conf_weight = {"High": 1.0, "Medium": .85, "Low": .65}
            health["Penalty"] = [min(60, (severity.get(r.Condition, 0) + min(r["Outside Fraction"] * 12, 8)) * conf_weight.get(r.Confidence, .65)) for _, r in health.iterrows()]
            raw_score = 100 - float(health["Penalty"].mean())
            critical = int((health.Condition == "Critical").sum())
            attention = int((health.Condition == "Attention").sum())
            deteriorating = int((health.Condition == "Deteriorating").sum())
            # Keep the numerical score consistent with the qualitative status.
            if critical:
                overall, risk, priority, icon, cap = "CRITICAL", "HIGH", "P1", "🔴", 69
            elif attention:
                overall, risk, priority, icon, cap = "ATTENTION", "MEDIUM", "P2", "🟠", 89
            elif deteriorating:
                overall, risk, priority, icon, cap = "DETERIORATING", "MEDIUM-LOW", "P3", "🟡", 94
            else:
                overall, risk, priority, icon, cap = "HEALTHY", "LOW", "P4", "🟢", 100
            score = int(round(max(0, min(cap, raw_score))))

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Equipment Health", f"{icon} {overall}")
            c2.metric("Screening Score", f"{score}/100")
            c3.metric("Parameters", f"{len(health):,}")
            c4.metric("Risk", risk)
            c5.metric("Maintenance Priority", priority)

            st.markdown("#### Condition Distribution")
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Normal", int((health.Condition == "Normal").sum()))
            d2.metric("Deteriorating", deteriorating)
            d3.metric("Attention", attention)
            d4.metric("Critical", critical)

            st.markdown("#### Parameter Condition")
            display_cols = ["PLC Tag", "Parameter", "Unit", "Current", "Baseline Low", "Baseline High", "Direction", "Shift %", "Outside Fraction", "Condition", "Confidence"]
            st.dataframe(health[display_cols], use_container_width=True, height=440)

            flagged = health[health.Condition != "Normal"].copy()
            st.markdown("#### Engineering Findings & Maintenance Focus")
            if flagged.empty:
                st.success("No parameter currently shows a significant historical-behaviour deviation.")
            else:
                order = {"Critical": 0, "Attention": 1, "Deteriorating": 2}
                flagged["_order"] = flagged.Condition.map(order)
                flagged = flagged.sort_values(["_order", "Deviation Sigma"], ascending=[True, False])
                for idx, r in flagged.iterrows():
                    st.warning(f"**{r['PLC Tag']} — {r['Parameter']}** → **{r['Condition']}** | Current {r['Current']:.3f} {r['Unit']} | Historical P05–P95 {r['Baseline Low']:.3f}–{r['Baseline High']:.3f} {r['Unit']} | Trend {r['Direction']} ({r['Shift %']:+.1f}%).")
                    st.caption(f"Parameter identification: {r['Parameter Source']} • Suggested engineering check: {r['Action']}")
                    if st.button(f"Open Engineering Trend — {r['PLC Tag']}", key=f"open_trend_{selected_eq}_{r['PLC Tag']}"):
                        st.session_state["health_open_tag"] = r["PLC Tag"]

            open_tag = st.session_state.get("health_open_tag")
            if open_tag and open_tag in health["PLC Tag"].values:
                r = health[health["PLC Tag"] == open_tag].iloc[0]
                st.markdown("#### Selected Finding — Engineering Trend")
                st.markdown(f"**{open_tag} — {r['Parameter']}** | {r['Condition']} | {r['Direction']} ({r['Shift %']:+.1f}%)")
                trend = df[["ArchiveTime", open_tag]].copy() if open_tag in df.columns else pd.DataFrame()
                if not trend.empty:
                    trend[open_tag] = pd.to_numeric(trend[open_tag], errors="coerce")
                    trend = trend.dropna().set_index("ArchiveTime")[open_tag]
                    if len(trend):
                        st.line_chart(trend, height=300)
                        t1, t2, t3 = st.columns(3)
                        t1.metric("Current", f"{r['Current']:.3f} {r['Unit']}")
                        t2.metric("Historical P05–P95", f"{r['Baseline Low']:.3f}–{r['Baseline High']:.3f}")
                        t3.metric("Recent Shift", f"{r['Shift %']:+.1f}%")
                        st.info(f"Engineering interpretation: {r['Condition']} condition based on historical behaviour. {r['Action']}")

            st.markdown("#### Engineering Decision")
            if overall == "CRITICAL":
                st.error(f"Priority {priority}: {critical} parameter(s) show strong deviation. Validate the signal and field condition promptly before deciding on corrective maintenance.")
            elif overall == "ATTENTION":
                st.warning(f"Priority {priority}: {attention} parameter(s) require engineering review. Check trend, process state and recent maintenance history; plan inspection if deviation persists.")
            elif overall == "DETERIORATING":
                st.info(f"Priority {priority}: {deteriorating} parameter(s) show a meaningful directional change. Increase monitoring frequency and verify field condition.")
            else:
                st.success("Equipment behaviour is consistent with its historical operating envelope based on available PLC data.")
            st.caption("Method: historical P05–P95 envelope + recent-vs-prior shift + sustained outside-baseline fraction + mapping-confidence weighting. Score is a screening indicator, not an alarm/trip setting or failure prediction.")

elif page == "Maintenance Priority":
    st.subheader("Maintenance Priority Center")
    st.caption("Condition-based engineering screening across canonical equipment. Criticality is intentionally not guessed; validate it before converting screening priority into formal risk priority.")
    screening = build_equipment_screening(master, df)
    if screening.empty:
        st.warning("No equipment has sufficient historical numeric data for screening.")
    else:
        f1, f2, f3 = st.columns(3)
        area_filter = f1.selectbox("Area", ["All"] + sorted([str(x) for x in master["Area"].unique() if str(x)]), key="priority_area")
        priority_filter = f2.selectbox("Screening Priority", ["All", "P1", "P2", "P3", "P4"], key="priority_level")
        condition_filter = f3.selectbox("Condition", ["All", "CRITICAL", "ATTENTION", "DETERIORATING", "HEALTHY"], key="priority_condition")
        view = screening.copy()
        if area_filter != "All":
            area_eq = set(master.loc[master["Area"] == area_filter, "Equipment Code"].astype(str))
            view = view[view["Equipment Code"].isin(area_eq)]
        if priority_filter != "All":
            view = view[view["Screening Priority"] == priority_filter]
        if condition_filter != "All":
            view = view[view["Condition"] == condition_filter]
        order = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}
        view["_order"] = view["Screening Priority"].map(order)
        view = view.sort_values(["_order", "Health", "Top Shift %"], ascending=[True, True, False]).drop(columns="_order")
        st.markdown("#### OPP Maintenance Screening Ranking")
        st.dataframe(view[["Equipment Code", "Equipment", "Health", "Condition", "Screening Priority", "Risk", "Criticality", "Parameters", "Deteriorating", "Attention", "Critical", "Top Parameter", "Top Finding", "Top Trend", "Top Shift %"]], use_container_width=True, hide_index=True, height=520)
        st.markdown("#### Selected Equipment")
        choices = view["Equipment Code"].tolist()
        if choices:
            selected = st.selectbox("Equipment Code", choices, key="priority_equipment")
            r = view[view["Equipment Code"] == selected].iloc[0]
            st.markdown(f"### {r['Equipment Code']} — {r['Equipment']}")
            a,b,c,d = st.columns(4)
            a.metric("Health", f"{r['Health']}/100")
            b.metric("Screening Priority", r["Screening Priority"])
            c.metric("Risk", r["Risk"])
            d.metric("Criticality", r["Criticality"])
            st.warning(f"**Primary finding:** {r['Top Tag']} — {r['Top Parameter']} → {r['Top Finding']} | Trend {r['Top Trend']} ({r['Top Shift %']:+.1f}%).") if r["Screening Priority"] != "P4" else st.success("No abnormal parameter currently identified by the historical screening engine.")
            if r["Screening Priority"] != "P4":
                st.info(f"**Suggested engineering check:** {r['Top Action']}")
            st.caption("Risk remains REVIEW REQUIRED because equipment criticality has not been supplied. Do not treat P1/P2 as an alarm, trip, or automatic work order.")
        st.markdown("#### Equipment Criticality Master")
        st.write("Use this template to document criticality from approved engineering/reliability assessment. The application will not infer criticality from equipment type alone.")
        template = criticality_template(master)
        st.download_button("Download Criticality Master Template", template.to_csv(index=False).encode("utf-8"), "equipment_criticality_master_template.csv", "text/csv")
        uploaded_crit = st.file_uploader("Optional: upload validated criticality master (.csv)", type=["csv"], key="criticality_upload")
        if uploaded_crit is not None:
            crit = pd.read_csv(uploaded_crit).fillna("")
            needed = {"Equipment Code", "Criticality"}
            if not needed.issubset(crit.columns):
                st.error("Criticality file must contain at least: Equipment Code, Criticality")
            else:
                merged = screening.merge(crit[["Equipment Code", "Criticality"]], on="Equipment Code", how="left", suffixes=("", "_validated"))
                merged["Criticality"] = merged["Criticality_validated"].replace("", np.nan).fillna(merged["Criticality"])
                merged = merged.drop(columns=["Criticality_validated"])
                st.success("Validated criticality loaded for this session. It is not written back to the repository automatically.")
                st.dataframe(merged[["Equipment Code", "Criticality", "Screening Priority", "Health", "Condition", "Top Parameter"]], use_container_width=True, hide_index=True)

elif page == "Tag Master":
    st.subheader("PLC Tag Master")
    st.caption("Source engineering mapping is preserved. Derived parameter/unit labels are used only for display when the source mapping is blank.")
    q = st.text_input("Search tag / equipment / parameter")
    area = st.selectbox("Area", ["All"] + sorted([x for x in master["Area"].unique() if x]))
    conf = st.selectbox("Confidence", ["All", "High", "Medium", "Low"])
    view = master.copy()
    if q:
        mask = view.astype(str).apply(lambda s: s.str.contains(q, case=False, na=False)).any(axis=1)
        view = view[mask]
    if area != "All":
        view = view[view["Area"] == area]
    if conf != "All":
        view = view[view["Confidence"] == conf]
    st.dataframe(view, use_container_width=True, height=620)
    st.download_button("Download Tag Master CSV", master.to_csv(index=False).encode("utf-8"), "OPP_Tag_Master_Phase4_1.csv", "text/csv")

elif page == "Engineering Trend":
    st.subheader("Engineering Trend — Equipment View")
    st.caption("Select an equipment code to display all mapped PLC parameters together. Equipment identity is canonicalized so code variants are grouped under one physical equipment.")
    area_options = ["All"] + sorted([x for x in master["Area"].unique() if x])
    selected_area = st.selectbox("Area", area_options, key="trend_area")
    area_view = master if selected_area == "All" else master[master["Area"] == selected_area]
    eq_codes = sorted([x for x in area_view["Equipment Code"].unique() if x])
    if not eq_codes:
        st.warning("No equipment code is mapped for this selection yet.")
    else:
        selected_eq = st.selectbox("Equipment Code", eq_codes, key="trend_equipment")
        eq_view = area_view[area_view["Equipment Code"] == selected_eq].copy()
        names = eq_view["Equipment"].replace("", np.nan).dropna()
        eq_name = names.iloc[0] if len(names) else "Equipment description not yet mapped"
        st.markdown(f"### {selected_eq}")
        st.caption(f"{eq_name} • {len(eq_view)} associated PLC tags")
        if df.empty:
            st.warning("No historical data available.")
        else:
            min_d, max_d = df["ArchiveTime"].min().date(), df["ArchiveTime"].max().date()
            c1, c2 = st.columns(2)
            start = c1.date_input("Start Date", min_d, min_value=min_d, max_value=max_d, key="trend_start")
            end = c2.date_input("End Date", max_d, min_value=min_d, max_value=max_d, key="trend_end")
            if start > end:
                st.error("Start Date cannot be later than End Date.")
            else:
                rows = []
                for _, meta in eq_view.iterrows():
                    tag = str(meta.get("PLC Tag", "")).strip()
                    if tag not in df.columns:
                        continue
                    d = df[(df["ArchiveTime"].dt.date >= start) & (df["ArchiveTime"].dt.date <= end)][["ArchiveTime", tag]].copy()
                    d[tag] = pd.to_numeric(d[tag], errors="coerce")
                    s = d[tag].dropna()
                    if len(s):
                        parameter, unit, source = infer_parameter(tag, meta.get("Suggested Parameter", ""), meta.get("Suggested Unit", ""), meta.get("Instrument Type", ""))
                        rows.append((meta, d, s, parameter, unit, source))
                st.markdown("#### Equipment Parameter Summary")
                summary = [{"PLC Tag": m["PLC Tag"], "Parameter": p, "Unit": u, "Current": s.iloc[-1], "Average": s.mean(), "Min": s.min(), "Max": s.max(), "Confidence": m["Confidence"] or "Low", "Parameter Source": src} for m, _, s, p, u, src in rows]
                if summary:
                    st.dataframe(pd.DataFrame(summary), use_container_width=True, height=300)
                st.markdown("#### Parameter Trends")
                for meta, d, s, parameter, unit, source in rows:
                    tag = meta["PLC Tag"]
                    st.markdown(f"**{tag} — {parameter}**")
                    st.caption(f"Unit: {unit} | Identification: {source} | Confidence: {meta['Confidence'] or 'Low'} | Reference: {meta['Reference Source'] or 'Not available'}")
                    chart = d.set_index("ArchiveTime")[tag].dropna()
                    st.line_chart(chart, height=230)
                if not rows:
                    st.info("No valid historical data in selected date range.")
                st.info("Trend panels are intentionally separated by parameter/unit. Do not combine flow, temperature, pressure and vibration on one Y-axis.")

elif page == "Data Import":
    st.subheader("Daily PLC Excel Import — Validation")
    uploaded = st.file_uploader("Upload daily PLC export (.xlsx)", type=["xlsx"])
    if uploaded:
        incoming = pd.read_excel(uploaded)
        if "ArchiveTime" not in incoming.columns:
            st.error("ArchiveTime not found.")
        else:
            incoming["ArchiveTime"] = pd.to_datetime(incoming["ArchiveTime"], errors="coerce")
            known = set(df["ArchiveTime"]) if not df.empty else set()
            q1, q2, q3 = st.columns(3)
            q1.metric("Rows", f"{len(incoming):,}")
            q2.metric("New timestamps", f"{(~incoming['ArchiveTime'].isin(known)).sum():,}")
            q3.metric("Invalid timestamps", f"{incoming['ArchiveTime'].isna().sum():,}")
            st.dataframe(incoming.head(20), use_container_width=True)
            st.info("Permanent database append will be implemented after mapping validation.")
