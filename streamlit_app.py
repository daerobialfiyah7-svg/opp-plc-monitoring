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

@st.cache_data
def load_equipment_reference():
    path = ROOT / "config" / "equipment_reference.csv"
    if not path.exists():
        return pd.DataFrame(columns=["Equipment Code", "Area", "Equipment", "Criticality"])
    ref = pd.read_csv(path).fillna("")
    for c in ["Equipment Code", "Area", "Equipment", "Criticality"]:
        if c not in ref.columns:
            ref[c] = ""
    ref["Equipment Code"] = ref["Equipment Code"].apply(normalize_equipment_code)
    return ref


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


def canonicalize_equipment_master(master, equipment_reference=None):
    master = master.copy()
    for c in ["Equipment Code", "PLC Tag", "Instrument Tag", "Equipment"]:
        if c not in master.columns:
            master[c] = ""
    master["Original Equipment Code"] = master["Equipment Code"].astype(str)

    def row_normalize(row):
        evidence = [row.get("PLC Tag", ""), row.get("Instrument Tag", ""), row.get("Equipment", "")]
        return normalize_equipment_code(row.get("Equipment Code", ""), evidence)

    master["Equipment Code"] = master.apply(row_normalize, axis=1)

    # If the reference master contains the canonical code, use it as the
    # authoritative equipment identity. This also makes PLC variants such as
    # 130ML0001 / 130ML001 / 130-ML-01 resolve to the same equipment.
    ref = equipment_reference.copy() if equipment_reference is not None else pd.DataFrame()
    if not ref.empty:
        ref["Equipment Code"] = ref["Equipment Code"].apply(normalize_equipment_code)
        ref = ref.drop_duplicates("Equipment Code", keep="first")

        ref_name = dict(zip(ref["Equipment Code"], ref["Equipment"]))
        ref_area = dict(zip(ref["Equipment Code"], ref["Area"]))
        ref_crit = dict(zip(ref["Equipment Code"], ref["Criticality"]))

        master["Equipment"] = master["Equipment Code"].map(ref_name).fillna(master["Equipment"])
        master["Area"] = master["Equipment Code"].map(ref_area).fillna(master.get("Area", ""))
        master["Reference Criticality"] = master["Equipment Code"].map(ref_crit).fillna("")

    # Merge artificial -00 only when the reference or current master confirms
    # that the corresponding -01 equipment exists.
    existing = set(x for x in master["Equipment Code"].astype(str) if x)
    if not ref.empty:
        existing |= set(ref["Equipment Code"].astype(str))

    replacements = {}
    for code in existing:
        m = re.fullmatch(r"(\d{3})-([A-Z]{2,5})-00", code)
        if m:
            sibling01 = f"{m.group(1)}-{m.group(2)}-01"
            if sibling01 in existing:
                replacements[code] = sibling01

    if replacements:
        master["Equipment Code"] = master["Equipment Code"].replace(replacements)
        if not ref.empty:
            master["Equipment"] = master["Equipment Code"].map(ref_name).fillna(master["Equipment"])
            master["Area"] = master["Equipment Code"].map(ref_area).fillna(master.get("Area", ""))
            master["Reference Criticality"] = master["Equipment Code"].map(ref_crit).fillna("")

    master["Equipment Mapping Key"] = master["Equipment Code"]
    original_compact = master["Original Equipment Code"].str.upper().str.replace("-", "", regex=False)
    canonical_compact = master["Equipment Code"].str.replace("-", "", regex=False)
    master["Source Code Variant"] = np.where(
        original_compact == canonical_compact,
        "Canonical",
        "Normalized / merged"
    )
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



# --- Phase 6: maintenance decision engine -----------------------------------------
def _criticality_rank(value):
    """Return an engineering-approved criticality rank only when explicitly supplied."""
    v = str(value or "").strip().upper()
    mapping = {
        "CRITICAL": 4, "VERY HIGH": 4,
        "HIGH": 3,
        "MEDIUM": 2, "MODERATE": 2,
        "LOW": 1,
    }
    return mapping.get(v, 0)


def _maintenance_decision(condition, criticality, health):
    """Combine observed PLC condition with validated criticality.

    Criticality is never inferred from equipment type. If it is not supplied,
    the result remains a condition-based screening priority.
    """
    c = str(condition or "").upper()
    cr = _criticality_rank(criticality)

    # Condition severity from historical PLC behaviour.
    cond_rank = {"CRITICAL": 4, "ATTENTION": 3, "DETERIORATING": 2, "HEALTHY": 1}.get(c, 1)

    # If validated criticality exists, use a conservative risk matrix.
    if cr:
        risk_index = max(cond_rank, cr) + min(cond_rank, cr) - 1
        if c == "CRITICAL" or (cr >= 4 and c in {"ATTENTION", "DETERIORATING"}):
            return "P1", "HIGH", "Immediate engineering review / condition verification"
        if risk_index >= 5:
            return "P2", "MEDIUM-HIGH", "Plan inspection and verify trend / field condition"
        if risk_index >= 4:
            return "P3", "MEDIUM", "Increase monitoring and include in maintenance planning"
        return "P4", "LOW", "Routine monitoring"

    # No criticality: do not manufacture a formal risk rating.
    if c == "CRITICAL" or health < 70:
        return "P1", "REVIEW REQUIRED", "Prompt engineering review; validate signal and field condition"
    if c == "ATTENTION" or health < 85:
        return "P2", "REVIEW REQUIRED", "Review trend, process state and recent maintenance history"
    if c == "DETERIORATING" or health < 95:
        return "P3", "REVIEW REQUIRED", "Increase monitoring and verify whether deterioration persists"
    return "P4", "REVIEW REQUIRED", "Routine monitoring"


def _health_score(h):
    """Calculate a differentiated screening score from parameter evidence.

    The score is not a probability of failure and is not an alarm/trip limit.
    It emphasizes the worst observed parameter while accounting for the
    breadth of abnormal behaviour and mapping confidence.
    """
    if h.empty:
        return 100

    conf_weight = {"High": 1.0, "Medium": 0.85, "Low": 0.65}
    severity = {"Normal": 0.0, "Deteriorating": 12.0, "Attention": 25.0, "Critical": 50.0}

    penalties = []
    for _, r in h.iterrows():
        base = severity.get(str(r["Condition"]), 0.0)
        outside = min(float(r["Outside Fraction"]) * 12.0, 8.0)
        confidence = conf_weight.get(str(r["Confidence"]), 0.65)
        penalties.append((base + outside) * confidence)

    penalties = np.asarray(penalties, dtype=float)
    worst = float(np.max(penalties))
    secondary = float(np.mean(np.sort(penalties)[-min(3, len(penalties)):]))
    abnormal_fraction = float((h["Condition"] != "Normal").mean())

    score = 100.0 - (0.72 * worst + 0.20 * secondary + 12.0 * abnormal_fraction)
    return int(round(max(0, min(100, score))))


def build_equipment_screening(master, df, criticality_df=None):
    """Aggregate PLC evidence into one canonical equipment screening record."""
    records = []

    crit_map = {}
    # Use the supplied equipment reference as the default source of criticality.
    # A separately uploaded validated criticality file overrides it.
    if "Reference Criticality" in master.columns:
        crit_map.update({
            str(row["Equipment Code"]).strip().upper(): str(row["Reference Criticality"]).strip()
            for _, row in master[["Equipment Code", "Reference Criticality"]].drop_duplicates().iterrows()
            if str(row["Equipment Code"]).strip() and str(row["Reference Criticality"]).strip()
        })
    if criticality_df is not None and not criticality_df.empty:
        c = criticality_df.copy().fillna("")
        if {"Equipment Code", "Criticality"}.issubset(c.columns):
            crit_map.update({
                str(row["Equipment Code"]).strip().upper(): str(row["Criticality"]).strip()
                for _, row in c.iterrows()
                if str(row["Equipment Code"]).strip() and str(row["Criticality"]).strip()
            })

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

            parameter, unit, source = infer_parameter(
                tag,
                meta.get("Suggested Parameter", ""),
                meta.get("Suggested Unit", ""),
                meta.get("Instrument Type", "")
            )
            conf = str(meta.get("Confidence", "") or "Low")
            params.append({
                "PLC Tag": tag,
                "Parameter": parameter,
                "Unit": unit,
                "Confidence": conf,
                "Action": parameter_action(parameter, tag),
                **stats
            })

        if not params:
            continue

        h = pd.DataFrame(params)
        counts = h["Condition"].value_counts()
        critical = int(counts.get("Critical", 0))
        attention = int(counts.get("Attention", 0))
        deteriorating = int(counts.get("Deteriorating", 0))

        if critical:
            condition = "CRITICAL"
        elif attention:
            condition = "ATTENTION"
        elif deteriorating:
            condition = "DETERIORATING"
        else:
            condition = "HEALTHY"

        health = _health_score(h)

        eq_key = str(eq).strip().upper()
        criticality = crit_map.get(eq_key, "Not configured")
        priority, risk, decision = _maintenance_decision(condition, criticality, health)

        flagged = h[h["Condition"] != "Normal"].copy()
        if len(flagged):
            # Critical > Attention > Deteriorating, then strongest deviation.
            order = {"Critical": 0, "Attention": 1, "Deteriorating": 2}
            flagged["_order"] = flagged["Condition"].map(order)
            top = flagged.sort_values(["_order", "Deviation Sigma"], ascending=[True, False]).iloc[0]
        else:
            top = None

        names = ev["Equipment"].replace("", np.nan).dropna()
        name = names.iloc[0] if len(names) else "Equipment description not yet mapped"

        records.append({
            "Equipment Code": eq,
            "Equipment": name,
            "Health": health,
            "Condition": condition,
            "Screening Priority": priority,
            "Risk": risk,
            "Criticality": criticality,
            "Parameters": len(h),
            "Normal": int(counts.get("Normal", 0)),
            "Deteriorating": deteriorating,
            "Attention": attention,
            "Critical": critical,
            "Top Parameter": top["Parameter"] if top is not None else "—",
            "Top Tag": top["PLC Tag"] if top is not None else "—",
            "Top Finding": top["Condition"] if top is not None else "—",
            "Top Trend": top["Direction"] if top is not None else "—",
            "Top Shift %": float(top["Shift %"]) if top is not None else 0.0,
            "Top Action": top["Action"] if top is not None else "No abnormal parameter identified.",
            "Maintenance Decision": decision,
        })

    return pd.DataFrame(records)


# --- Phase 8: Engineering Action Center --------------------------------------------
ACTION_STATUSES = ["OPEN", "INVESTIGATION", "ACTION", "VERIFICATION", "CLOSED"]
ACTION_PRIORITIES = ["P1", "P2", "P3", "P4"]


def _finding_id(eq, tag, condition, direction):
    raw = f"{eq}|{tag}|{condition}|{direction}"
    return re.sub(r"[^A-Z0-9|+.-]", "", raw.upper())


def _action_defaults(finding):
    return {
        "Finding ID": finding["Finding ID"], "Equipment Code": finding["Equipment Code"],
        "Equipment": finding["Equipment"], "Area": finding["Area"], "PLC Tag": finding["PLC Tag"],
        "Parameter": finding["Parameter"], "Condition": finding["Condition"], "Priority": finding["Priority"],
        "Risk": finding["Risk"], "Current": finding["Current"], "Unit": finding["Unit"],
        "Baseline Low": finding["Baseline Low"], "Baseline High": finding["Baseline High"],
        "Trend": finding["Direction"], "Shift %": finding["Shift %"], "Outside Fraction": finding["Outside Fraction"],
        "Evidence": "Historical PLC behaviour screening", "Recommendation": finding["Action"],
        "Status": "OPEN", "PIC": "", "Target Date": "", "Investigation Result": "", "Root Cause": "",
        "Action Taken": "", "Verification Result": "", "Engineer Notes": "",
    }


def build_action_findings(master, df, criticality_df=None):
    """Create one actionable finding per abnormal PLC parameter."""
    findings = []
    crit_map = {}
    if "Reference Criticality" in master.columns:
        for _, r in master[["Equipment Code", "Reference Criticality"]].drop_duplicates().iterrows():
            code, crit = str(r["Equipment Code"]).strip().upper(), str(r["Reference Criticality"]).strip()
            if code and crit: crit_map[code] = crit
    if criticality_df is not None and not criticality_df.empty and {"Equipment Code", "Criticality"}.issubset(criticality_df.columns):
        for _, r in criticality_df.iterrows():
            code, crit = normalize_equipment_code(r["Equipment Code"]), str(r["Criticality"]).strip()
            if code and crit: crit_map[code.upper()] = crit

    for eq, ev in master[master["Equipment Code"].astype(str).str.strip() != ""].groupby("Equipment Code"):
        eq = str(eq).strip()
        names = ev["Equipment"].replace("", np.nan).dropna()
        eq_name = names.iloc[0] if len(names) else "Equipment description not yet mapped"
        area = str(ev["Area"].iloc[0]) if len(ev) else ""
        criticality = crit_map.get(eq.upper(), "Not configured")
        seen = set()
        for _, meta in ev.iterrows():
            tag = str(meta.get("PLC Tag", "")).strip()
            if not tag or tag in seen: continue
            seen.add(tag)
            stats = baseline_condition(_numeric_series(df, tag))
            if stats is None or stats["Condition"] == "Normal": continue
            parameter, unit, source = infer_parameter(tag, meta.get("Suggested Parameter", ""), meta.get("Suggested Unit", ""), meta.get("Instrument Type", ""))
            condition = str(stats["Condition"]).upper()
            health_proxy = max(0, int(round(100 - {"Critical": 50, "Attention": 25, "Deteriorating": 12}.get(stats["Condition"], 0))))
            priority, risk, _ = _maintenance_decision(condition, criticality, health_proxy)
            findings.append({
                "Finding ID": _finding_id(eq, tag, condition, stats["Direction"]), "Area": area,
                "Equipment Code": eq, "Equipment": str(eq_name), "PLC Tag": tag, "Parameter": parameter,
                "Unit": unit, "Condition": condition, "Priority": priority, "Risk": risk,
                "Criticality": criticality, "Current": float(stats["Current"]),
                "Baseline Low": float(stats["Baseline Low"]), "Baseline High": float(stats["Baseline High"]),
                "Direction": stats["Direction"], "Shift %": float(stats["Shift %"]),
                "Outside Fraction": float(stats["Outside Fraction"]), "Deviation Sigma": float(stats["Deviation Sigma"]),
                "Confidence": str(meta.get("Confidence", "") or "Low"), "Parameter Source": source,
                "Action": parameter_action(parameter, tag),
            })
    if not findings: return pd.DataFrame()
    out = pd.DataFrame(findings)
    out["_priority"] = out["Priority"].map({"P1":1,"P2":2,"P3":3,"P4":4}).fillna(9)
    return out.sort_values(["_priority", "Deviation Sigma"], ascending=[True, False]).drop(columns="_priority").reset_index(drop=True)


def ensure_action_store(findings):
    if "engineering_actions" not in st.session_state: st.session_state["engineering_actions"] = {}
    store = st.session_state["engineering_actions"]
    if isinstance(store, pd.DataFrame): store = {str(r["Finding ID"]): r.to_dict() for _, r in store.iterrows()}
    for _, finding in findings.iterrows():
        fid = str(finding["Finding ID"])
        if fid not in store:
            store[fid] = _action_defaults(finding)
        else:
            existing = store[fid]
            for key in ["Equipment Code","Equipment","Area","PLC Tag","Parameter","Condition","Priority","Risk","Current","Unit","Baseline Low","Baseline High","Trend","Shift %","Outside Fraction","Recommendation"]:
                source_key = "Direction" if key == "Trend" else ("Action" if key == "Recommendation" else key)
                if source_key in finding: existing[key] = finding[source_key]
    st.session_state["engineering_actions"] = store
    return store


def actions_dataframe(store):
    if not store: return pd.DataFrame()
    df_actions = pd.DataFrame(list(store.values()))
    desired = ["Finding ID","Area","Equipment Code","Equipment","PLC Tag","Parameter","Condition","Priority","Status","PIC","Target Date","Shift %","Root Cause","Action Taken","Verification Result"]
    return df_actions[[c for c in desired if c in df_actions.columns]]


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
equipment_reference = load_equipment_reference()
master = canonicalize_equipment_master(load_master(), equipment_reference)
required = ["Area", "Equipment Code", "Equipment", "Instrument Tag", "Suggested Parameter", "Suggested Unit",
            "IO Type", "Instrument Type", "Calibration Range", "Evidence", "Reference Source", "Confidence", "Mapping Status"]
for col in required:
    if col not in master.columns:
        master[col] = ""

st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Equipment Health", "Maintenance Priority", "Action Center", "Tag Master", "Engineering Trend", "Data Import"])

st.title("⚙️ OPP Engineering Monitoring")
st.caption("Phase 8 — Equipment Health + Maintenance Decision + Engineering Action Center")

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
    findings = build_action_findings(master, df)
    if not findings.empty:
        store = ensure_action_store(findings)
        action_df = actions_dataframe(store)
        open_count = int((action_df["Status"] != "CLOSED").sum()) if not action_df.empty else 0
        st.caption(f"Engineering Action Center: {open_count} open finding(s) from current historical screening.")
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
    # Normalize Area before sorting to prevent mixed-type pandas errors
    area_series = (
        master["Area"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    ac = (
        area_series[area_series != ""]
        .value_counts()
        .sort_index()
    )
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
    st.subheader("OPP Maintenance Control Center")
    st.caption(
        "Engineering decision support: PLC historical behaviour + validated equipment criticality. "
        "Screening priority is not an alarm, trip setting, failure prediction or automatic work order."
    )

    # Session-only validated criticality master.
    if "validated_criticality" not in st.session_state:
        st.session_state["validated_criticality"] = pd.DataFrame()

    uploaded_crit = st.file_uploader(
        "Optional: upload validated Equipment Criticality Master (.csv)",
        type=["csv"],
        key="criticality_upload"
    )
    if uploaded_crit is not None:
        crit = pd.read_csv(uploaded_crit).fillna("")
        if not {"Equipment Code", "Criticality"}.issubset(crit.columns):
            st.error("Criticality file must contain at least: Equipment Code, Criticality")
        else:
            crit["Equipment Code"] = crit["Equipment Code"].apply(normalize_equipment_code)
            allowed = {"CRITICAL", "VERY HIGH", "HIGH", "MEDIUM", "MODERATE", "LOW"}
            bad = sorted(set(str(x).strip().upper() for x in crit["Criticality"]) - allowed - {""})
            if bad:
                st.warning(f"Unrecognized criticality values: {', '.join(bad)}. They will remain unvalidated.")
            st.session_state["validated_criticality"] = crit
            st.success("Validated criticality loaded for this session.")

    criticality_df = st.session_state.get("validated_criticality", pd.DataFrame())
    screening = build_equipment_screening(master, df, criticality_df)

    if screening.empty:
        st.warning("No equipment has sufficient historical numeric data for screening.")
    else:
        # KPI strip
        p1n = int((screening["Screening Priority"] == "P1").sum())
        p2n = int((screening["Screening Priority"] == "P2").sum())
        p3n = int((screening["Screening Priority"] == "P3").sum())
        p4n = int((screening["Screening Priority"] == "P4").sum())
        abnormal = int((screening["Condition"] != "HEALTHY").sum())

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("P1 — Immediate Review", p1n)
        k2.metric("P2 — Plan Inspection", p2n)
        k3.metric("P3 — Monitor", p3n)
        k4.metric("P4 — Routine", p4n)
        k5.metric("Equipment Requiring Attention", abnormal)

        st.markdown("#### Maintenance Screening Ranking")

        f1, f2, f3 = st.columns(3)
        area_filter = f1.selectbox(
            "Area",
            ["All"] + sorted([str(x) for x in master["Area"].unique() if str(x)]),
            key="priority_area"
        )
        priority_filter = f2.selectbox(
            "Screening Priority",
            ["All", "P1", "P2", "P3", "P4"],
            key="priority_level"
        )
        condition_filter = f3.selectbox(
            "Condition",
            ["All", "CRITICAL", "ATTENTION", "DETERIORATING", "HEALTHY"],
            key="priority_condition"
        )

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
        view = view.sort_values(
            ["_order", "Health", "Top Shift %"],
            ascending=[True, True, False]
        ).drop(columns="_order")

        table_cols = [
            "Equipment Code", "Equipment", "Health", "Condition",
            "Screening Priority", "Risk", "Criticality", "Parameters",
            "Deteriorating", "Attention", "Critical",
            "Top Parameter", "Top Finding", "Top Trend", "Top Shift %"
        ]
        st.dataframe(
            view[table_cols],
            use_container_width=True,
            hide_index=True,
            height=470
        )

        st.markdown("#### Selected Equipment")
        choices = view["Equipment Code"].tolist()

        if choices:
            selected = st.selectbox(
                "Equipment Code",
                choices,
                key="priority_equipment"
            )
            r = view[view["Equipment Code"] == selected].iloc[0]

            st.markdown(f"### {r['Equipment Code']} — {r['Equipment']}")

            a, b, c, d, e = st.columns(5)
            a.metric("Equipment Health", f"{r['Health']}/100")
            b.metric("Condition", r["Condition"])
            c.metric("Priority", r["Screening Priority"])
            d.metric("Criticality", r["Criticality"])
            e.metric("Risk", r["Risk"])

            if r["Screening Priority"] == "P1":
                st.error(
                    f"**PRIMARY FINDING:** {r['Top Tag']} — {r['Top Parameter']} → "
                    f"{r['Top Finding']} | Trend {r['Top Trend']} ({r['Top Shift %']:+.1f}%)."
                )
            elif r["Screening Priority"] == "P2":
                st.warning(
                    f"**PRIMARY FINDING:** {r['Top Tag']} — {r['Top Parameter']} → "
                    f"{r['Top Finding']} | Trend {r['Top Trend']} ({r['Top Shift %']:+.1f}%)."
                )
            elif r["Screening Priority"] == "P3":
                st.info(
                    f"**PRIMARY FINDING:** {r['Top Tag']} — {r['Top Parameter']} → "
                    f"{r['Top Finding']} | Trend {r['Top Trend']} ({r['Top Shift %']:+.1f}%)."
                )
            else:
                st.success("No abnormal parameter currently identified by the historical screening engine.")

            st.markdown("#### Engineering Maintenance Decision")
            st.info(f"**Recommended decision:** {r['Maintenance Decision']}")

            if r["Screening Priority"] != "P4":
                st.markdown("**Suggested engineering check**")
                st.write(r["Top Action"])

                # Direct navigation target for the engineer.
                b1, b2 = st.columns(2)
                if b1.button(
                    f"Open Engineering Trend — {r['Top Tag']}",
                    key=f"priority_open_trend_{selected}"
                ):
                    st.session_state["trend_equipment_from_priority"] = selected
                    st.session_state["trend_tag_from_priority"] = r["Top Tag"]
                    st.info("Open **Engineering Trend** from the navigation panel. The selected equipment/tag has been retained for the next engineering review.")
                if b2.button(
                    "Open Engineering Action Center",
                    key=f"priority_open_action_{selected}"
                ):
                    fdf = build_action_findings(master[master["Equipment Code"] == selected], df, criticality_df)
                    if not fdf.empty:
                        st.session_state["action_selected_finding"] = str(fdf.iloc[0]["Finding ID"])
                        st.info("Finding transferred to Engineering Action Center. Use the navigation panel to continue the workflow.")
                    else:
                        st.info("No abnormal finding is currently available for this equipment.")

            st.caption(
                "Decision logic uses historical P05–P95 behaviour, recent-vs-prior shift, "
                "sustained outside-baseline fraction, mapping confidence and—when supplied—"
                "validated equipment criticality."
            )

        st.markdown("#### Equipment Criticality Master")
        st.write(
            "Download the template, fill criticality from the approved engineering/reliability assessment, "
            "then upload it above. The application will not infer criticality from equipment type."
        )
        template = criticality_template(master)
        st.download_button(
            "Download Criticality Master Template",
            template.to_csv(index=False).encode("utf-8"),
            "equipment_criticality_master_template.csv",
            "text/csv"
        )

elif page == "Action Center":
    st.subheader("OPP Engineering Action Center")
    st.caption("Finding management for engineering follow-up. PLC screening provides evidence; field verification, engineering judgement and approved maintenance processes remain mandatory.")

    criticality_df = st.session_state.get("validated_criticality", pd.DataFrame())
    findings = build_action_findings(master, df, criticality_df)
    if findings.empty:
        st.success("No abnormal PLC finding is currently generated by the historical screening engine.")
    else:
        store = ensure_action_store(findings)
        action_df = actions_dataframe(store)
        k1,k2,k3,k4,k5 = st.columns(5)
        for col,status in zip([k1,k2,k3,k4,k5], ACTION_STATUSES):
            col.metric(status, int((action_df["Status"] == status).sum()) if not action_df.empty else 0)
        st.markdown("### Engineering Finding Queue")
        f1,f2,f3,f4 = st.columns(4)
        area_f=f1.selectbox("Area", ["All"]+sorted([str(x) for x in findings["Area"].dropna().unique() if str(x).strip()]), key="action_area")
        priority_f=f2.selectbox("Priority", ["All"]+ACTION_PRIORITIES, key="action_priority")
        status_f=f3.selectbox("Status", ["All"]+ACTION_STATUSES, key="action_status")
        search_f=f4.text_input("Search equipment / tag", key="action_search")
        q=action_df.copy()
        if area_f!="All": q=q[q["Area"].astype(str)==area_f]
        if priority_f!="All": q=q[q["Priority"].astype(str)==priority_f]
        if status_f!="All": q=q[q["Status"].astype(str)==status_f]
        if search_f.strip(): q=q[q.astype(str).apply(lambda s:s.str.contains(search_f.strip(),case=False,na=False)).any(axis=1)]
        q["_p"]=q["Priority"].map({"P1":1,"P2":2,"P3":3,"P4":4}).fillna(9)
        q["_s"]=q["Status"].map({"OPEN":1,"INVESTIGATION":2,"ACTION":3,"VERIFICATION":4,"CLOSED":5}).fillna(9)
        q=q.sort_values(["_p","_s","Shift %"],ascending=[True,True,False]).drop(columns=["_p","_s"])
        if q.empty:
            st.info("No finding matches the selected filters.")
        else:
            st.dataframe(q[["Equipment Code","Equipment","PLC Tag","Parameter","Condition","Priority","Status","PIC","Target Date","Shift %"]],use_container_width=True,hide_index=True,height=360)
            choices=q["Finding ID"].tolist()
            labels={fid: (lambda rr:f"{rr['Equipment Code']} • {rr['PLC Tag']} • {rr['Parameter']} • {rr['Status']}")(q[q["Finding ID"]==fid].iloc[0]) for fid in choices}
            selected_default=st.session_state.get("action_selected_finding")
            if selected_default not in choices: selected_default=choices[0]
            selected_finding=st.selectbox("Select finding to work on",choices,index=choices.index(selected_default),format_func=lambda x:labels.get(x,x),key="action_finding_select")
            st.session_state["action_selected_finding"]=selected_finding
            record=store[selected_finding]
            st.markdown("### Selected Finding")
            a,b,c,d=st.columns(4); a.metric("Equipment",record["Equipment Code"]); b.metric("Health Signal",record["Condition"]); c.metric("Priority",record["Priority"]); d.metric("Workflow",record["Status"])
            st.warning(f"**{record['PLC Tag']} — {record['Parameter']}** | Current {float(record['Current']):.3f} {record['Unit']} | Historical P05–P95 {float(record['Baseline Low']):.3f}–{float(record['Baseline High']):.3f} {record['Unit']} | Trend {record['Trend']} ({float(record['Shift %']):+.1f}%).")
            st.info(f"**Recommended engineering check:** {record['Recommendation']}")
            with st.expander("Evidence & Screening Context",expanded=True):
                e1,e2,e3=st.columns(3); e1.metric("Outside Recent Fraction",f"{float(record['Outside Fraction'])*100:.1f}%"); e2.metric("Risk",record["Risk"]); e3.metric("Criticality",record.get("Criticality","Not configured"))
                st.write("This finding is generated from historical PLC behaviour using a P05–P95 baseline, recent-vs-prior shift and sustained outside-baseline behaviour. It is not a failure prediction, alarm, trip setting or automatic work order.")
            st.markdown("### Engineering Workflow")
            with st.form(f"action_form_{selected_finding}"):
                c1,c2,c3=st.columns(3); status=c1.selectbox("Status",ACTION_STATUSES,index=ACTION_STATUSES.index(record.get("Status","OPEN"))); pic=c2.text_input("PIC",value=str(record.get("PIC",""))); target_date=c3.text_input("Target Date (YYYY-MM-DD)",value=str(record.get("Target Date","")))
                inv=st.text_area("Investigation Result",value=str(record.get("Investigation Result","")),placeholder="What did the field / instrument / process verification show?")
                root=st.text_area("Root Cause",value=str(record.get("Root Cause","")),placeholder="Engineering-confirmed cause; do not infer from PLC screening alone.")
                action_taken=st.text_area("Action Taken",value=str(record.get("Action Taken","")),placeholder="Inspection, adjustment, repair, calibration, cleaning, alignment, etc.")
                verification=st.text_area("Verification Result",value=str(record.get("Verification Result","")),placeholder="Post-action evidence: PLC trend, field inspection, test result, or other approved verification.")
                notes=st.text_area("Engineer Notes",value=str(record.get("Engineer Notes","")))
                submitted=st.form_submit_button("Save Engineering Action")
            if submitted:
                record.update({"Status":status,"PIC":pic.strip(),"Target Date":target_date.strip(),"Investigation Result":inv.strip(),"Root Cause":root.strip(),"Action Taken":action_taken.strip(),"Verification Result":verification.strip(),"Engineer Notes":notes.strip()})
                store[selected_finding]=record; st.session_state["engineering_actions"]=store; st.success("Engineering action saved in this session."); st.rerun()
            st.markdown("### Workflow Guidance")
            st.write("**OPEN → INVESTIGATION → ACTION → VERIFICATION → CLOSED**. Do not move to CLOSED until the engineering verification is documented and the condition is acceptable.")
            d1,d2=st.columns(2); export_df=actions_dataframe(store)
            d1.download_button("Download Engineering Action Log (.csv)",export_df.to_csv(index=False).encode("utf-8"),"OPP_engineering_action_log.csv","text/csv",use_container_width=True)
            uploaded_actions=d2.file_uploader("Restore Action Log (.csv)",type=["csv"],key="action_restore")
            if uploaded_actions is not None:
                restored=pd.read_csv(uploaded_actions).fillna("")
                if "Finding ID" not in restored.columns: st.error("Action Log must contain the Finding ID column.")
                else:
                    for _,rr in restored.iterrows(): store[str(rr["Finding ID"])]=rr.to_dict()
                    st.session_state["engineering_actions"]=store; st.success(f"Restored {len(restored):,} engineering action record(s).")

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
        default_trend_eq = st.session_state.get("trend_equipment_from_priority", "")
        default_index = eq_codes.index(default_trend_eq) if default_trend_eq in eq_codes else 0
        selected_eq = st.selectbox("Equipment Code", eq_codes, index=default_index, key="trend_equipment")
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
