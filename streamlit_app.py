import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="OPP Engineering Monitoring",
    page_icon="⚙️",
    layout="wide",
)

ROOT = Path(__file__).resolve().parent


# ============================================================
# FUTURISTIC UI / UX
# ============================================================
st.markdown("""
<style>
/* ============================================================
   LIGHT INDUSTRIAL / ENGINEERING UI
   ============================================================ */
:root {
    --opp-bg: #eef3f7;
    --opp-panel: rgba(255,255,255,.92);
    --opp-panel-2: #f7fafc;
    --opp-border: #d7e1ea;
    --opp-text: #203044;
    --opp-muted: #66788b;
    --opp-cyan: #008eb8;
    --opp-blue: #2468b3;
    --opp-green: #15966d;
    --opp-yellow: #d89a18;
    --opp-red: #d94b5f;
}

.stApp {
    background:
        radial-gradient(circle at 88% 5%, rgba(0,142,184,.07), transparent 24%),
        radial-gradient(circle at 10% 18%, rgba(36,104,179,.055), transparent 28%),
        linear-gradient(135deg, #eef3f7 0%, #f5f8fa 52%, #e9f0f5 100%);
    color: var(--opp-text);
}

/* Blueprint / engineering grid */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: .20;
    background-image:
        linear-gradient(rgba(55,91,120,.11) 1px, transparent 1px),
        linear-gradient(90deg, rgba(55,91,120,.11) 1px, transparent 1px);
    background-size: 38px 38px;
    z-index: 0;
}

/* Subtle engineering watermark: gear + process/plant silhouette */
.stApp::after {
    content: "⚙     ⚙        ────┐     ┌────      ⚙\\A   ────────┘     └────────\\A       OPP  •  PROCESS  •  ENGINEERING";
    white-space: pre;
    position: fixed;
    right: 2%;
    bottom: 4%;
    font-family: monospace;
    font-size: 30px;
    line-height: 2.1;
    letter-spacing: .08em;
    color: rgba(52,94,125,.055);
    pointer-events: none;
    z-index: 0;
}

.block-container {
    padding-top: 1.7rem;
    padding-bottom: 3rem;
    max-width: 1600px;
}

/* Header */
.opp-hero {
    position: relative;
    overflow: hidden;
    padding: 24px 30px;
    margin-bottom: 20px;
    border: 1px solid #cbd9e5;
    border-radius: 20px;
    background:
        linear-gradient(115deg, rgba(255,255,255,.97), rgba(239,247,251,.96));
    box-shadow: 0 10px 28px rgba(36,67,91,.10);
}

.opp-hero::before {
    content: "⚙";
    position: absolute;
    right: 42px;
    top: -38px;
    font-size: 170px;
    color: rgba(0,142,184,.055);
    transform: rotate(18deg);
}

.opp-hero::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 3px;
    background: linear-gradient(90deg, #008eb8, #2468b3, transparent 82%);
    opacity: .75;
}

.opp-kicker {
    color: var(--opp-cyan);
    font-size: 12px;
    font-weight: 750;
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-bottom: 7px;
}

.opp-hero-title {
    font-size: clamp(28px, 3vw, 42px);
    line-height: 1.08;
    font-weight: 800;
    letter-spacing: -.025em;
    margin: 0;
    color: #1e3045;
}

.opp-hero-sub {
    color: var(--opp-muted);
    margin-top: 8px;
    font-size: 14px;
}

.opp-live {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-top: 15px;
    padding: 7px 12px;
    border: 1px solid rgba(21,150,109,.25);
    border-radius: 999px;
    background: rgba(21,150,109,.07);
    color: #147956;
    font-size: 12px;
    font-weight: 700;
}

.opp-live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--opp-green);
    box-shadow: 0 0 12px rgba(21,150,109,.45);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, #e8f0f5 0%, #f5f8fa 100%);
    border-right: 1px solid #ccd9e3;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.4rem;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: #3b5065 !important;
    font-weight: 650;
    font-size: 15px !important;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    color: var(--opp-cyan) !important;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
    gap: 5px;
}

/* Metrics */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(255,255,255,.97), rgba(246,249,251,.96));
    border: 1px solid var(--opp-border);
    border-radius: 15px;
    padding: 15px 18px;
    box-shadow: 0 7px 20px rgba(42,71,94,.07);
}

[data-testid="stMetricLabel"] {
    color: #63778a !important;
    font-size: 13px !important;
    font-weight: 650 !important;
}

[data-testid="stMetricValue"] {
    color: #24384d !important;
    font-size: 27px !important;
    font-weight: 800 !important;
    letter-spacing: -.02em;
}

/* Cards / bordered containers */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--opp-border) !important;
    border-radius: 16px !important;
    background: rgba(255,255,255,.76);
    box-shadow: 0 5px 18px rgba(42,71,94,.05);
}

/* Inputs */
.stSelectbox > div > div,
.stTextInput > div > div,
.stDateInput > div > div {
    background: rgba(255,255,255,.96) !important;
    border: 1px solid #ccd9e3 !important;
    border-radius: 10px !important;
}

.stSelectbox label, .stTextInput label, .stDateInput label {
    color: #536a7e !important;
    font-weight: 650 !important;
    font-size: 14px !important;
}

/* Buttons */
.stButton > button, .stDownloadButton > button {
    border: 1px solid rgba(0,142,184,.30) !important;
    border-radius: 9px !important;
    background: linear-gradient(135deg, #f7fcfe, #edf6fa) !important;
    color: #21627c !important;
    font-weight: 700 !important;
}

.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: rgba(0,142,184,.65) !important;
    box-shadow: 0 0 18px rgba(0,142,184,.10);
}

/* Main headings: medium, readable, not oversized */
h1, h2, h3, h4 {
    color: #24364a !important;
    letter-spacing: -.018em;
}

h1 { font-size: 30px !important; }
h2 { font-size: 25px !important; }
h3 { font-size: 21px !important; }
h4 { font-size: 18px !important; }

.stMarkdown p, .stText, .stCaption, [data-testid="stCaptionContainer"] {
    color: #607487;
}

.stCaption, [data-testid="stCaptionContainer"] {
    font-size: 13px !important;
}

/* Tables */
[data-testid="stDataFrame"] {
    border: 1px solid var(--opp-border);
    border-radius: 12px;
    overflow: hidden;
    background: rgba(255,255,255,.90);
}

/* Alerts */
div[data-testid="stAlert"] {
    border-radius: 11px !important;
    border: 1px solid #d7e1ea !important;
}

/* Dividers */
hr {
    border-color: #d6e0e8 !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #5d7184 !important;
    font-size: 14px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--opp-cyan) !important;
}

/* Plotly charts */
.js-plotly-plot {
    border: 1px solid #d7e1ea;
    border-radius: 13px;
    overflow: hidden;
    background: rgba(255,255,255,.88);
}

/* Equipment/page titles */
.opp-equipment-title {
    font-size: 25px;
    font-weight: 800;
    color: #24364a;
}

/* Mobile */
@media (max-width: 900px) {
    .opp-hero { padding: 20px; border-radius: 16px; }
    .block-container { padding-left: 1rem; padding-right: 1rem; }
    h1 { font-size: 27px !important; }
    h2 { font-size: 23px !important; }
    h3 { font-size: 20px !important; }
}
</style>
""", unsafe_allow_html=True)



# ============================================================
# DATA LOAD
# ============================================================

@st.cache_data
def load_history():
    files = sorted((ROOT / "data").glob("*.csv.gz"))
    if not files:
        return pd.DataFrame(columns=["ArchiveTime"])
    frames = []
    for f in files:
        try:
            frames.append(pd.read_csv(f, parse_dates=["ArchiveTime"]))
        except Exception:
            # Keep deployment alive if one historical file is malformed.
            continue
    if not frames:
        return pd.DataFrame(columns=["ArchiveTime"])
    out = pd.concat(frames, ignore_index=True)
    if "ArchiveTime" not in out.columns:
        out["ArchiveTime"] = pd.NaT
    out["ArchiveTime"] = pd.to_datetime(out["ArchiveTime"], errors="coerce")
    return out.dropna(subset=["ArchiveTime"]).sort_values("ArchiveTime")


@st.cache_data
def load_master():
    path = ROOT / "config" / "tag_master.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path).fillna("")


df = load_history()
master = load_master()

# Defensive schema: never let a missing enrichment column crash the app.
required = [
    "PLC Tag", "Area", "Equipment Code", "Equipment", "Instrument Tag",
    "Suggested Parameter", "Suggested Unit", "IO Type", "Instrument Type",
    "Calibration Range", "Evidence", "Reference Source", "Confidence",
    "Mapping Status", "Baseline Low", "Baseline High",
]
for col in required:
    if col not in master.columns:
        master[col] = ""

if "PLC Tag" not in df.columns:
    # Historical data can still be displayed as empty until a valid export exists.
    pass


# ============================================================
# ENGINEERING HELPERS
# ============================================================

def safe_float(value):
    try:
        x = float(value)
        return x if np.isfinite(x) else np.nan
    except Exception:
        return np.nan


def parameter_label(meta):
    return (
        str(meta.get("Suggested Parameter", "")).strip()
        or str(meta.get("Instrument Type", "")).strip()
        or "PLC Parameter"
    )


def unit_label(meta):
    return str(meta.get("Suggested Unit", "")).strip() or "—"


def confidence_weight(conf):
    # Confidence changes the strength of the engineering screening,
    # not the physical severity of the signal.
    return {"High": 1.00, "Medium": 0.85, "Low": 0.70}.get(str(conf), 0.70)


def category_from_meta(meta):
    text = " ".join([
        str(meta.get("Suggested Parameter", "")),
        str(meta.get("Instrument Type", "")),
        str(meta.get("PLC Tag", "")),
    ]).upper()

    if any(k in text for k in ["VIB", "VIBRATION", "ACCEL", "VELOC"]):
        return "Vibration"
    if any(k in text for k in ["TEMP", "TEMPERATURE", "RTD", "THERMO", "TIT"]):
        return "Temperature"
    if any(k in text for k in ["PRESS", "PRESSURE", "PIT", "DP", "DIFFERENTIAL"]):
        return "Pressure"
    if any(k in text for k in ["FLOW", "FLOWMETER", "FIT", "FI"]):
        return "Flow"
    if any(k in text for k in ["CURRENT", "AMP", "ELECTRICAL", "POWER", "KW", "KVA", "IIT"]):
        return "Electrical"
    if any(k in text for k in ["SPEED", "RPM", "VSD", "FREQUENCY", "SIT"]):
        return "Speed"
    if any(k in text for k in ["LEVEL", "LIT", "LEVEL"]):
        return "Level"
    if any(k in text for k in ["DENSITY", "DENS"]):
        return "Density"
    if any(k in text for k in ["PH", "ORP", "CONDUCT"]):
        return "Process Chemistry"
    return "Other"


def engineering_checks(category):
    checks = {
        "Vibration": [
            "Verify vibration with a calibrated handheld/online measurement.",
            "Check bearing condition, lubrication and mechanical looseness.",
            "Check coupling/alignment and compare against previous maintenance history.",
        ],
        "Temperature": [
            "Verify the reading against local/independent measurement where practical.",
            "Check bearing/motor/gearbox cooling and lubrication condition.",
            "Compare temperature with load, speed and recent operating changes.",
        ],
        "Pressure": [
            "Verify transmitter indication and impulse/process connection condition.",
            "Compare pressure with upstream/downstream operating conditions.",
            "Check for restriction, leakage or abnormal process resistance.",
        ],
        "Flow": [
            "Verify transmitter indication and process conditions.",
            "Compare flow with pump/valve state, pressure and equipment load.",
            "Check for restriction, leakage, valve position or instrument issues.",
        ],
        "Electrical": [
            "Compare current/power with motor load and operating condition.",
            "Check for abnormal load change, phase imbalance or electrical indications.",
            "Review motor/drive condition and recent maintenance history.",
        ],
        "Speed": [
            "Compare speed with operating command/setpoint and process load.",
            "Check VSD/drive status and feedback signal quality.",
            "Investigate unexpected speed deviation or hunting.",
        ],
        "Level": [
            "Compare level with upstream/downstream flow and equipment state.",
            "Check for restriction, overflow, leakage or control-valve behaviour.",
            "Verify transmitter signal if the trend is physically implausible.",
        ],
        "Density": [
            "Compare density with slurry/feed condition and dilution water.",
            "Check sampling/instrument condition and process changes.",
            "Review associated flow and pressure trends.",
        ],
        "Process Chemistry": [
            "Compare the reading with the process operating condition and laboratory result.",
            "Verify instrument calibration/cleanliness where applicable.",
            "Review reagent/dosing and upstream process changes.",
        ],
        "Other": [
            "Verify the signal against actual equipment/process condition.",
            "Check recent operating changes and maintenance history.",
            "Confirm the signal against OEM/design limits before intervention.",
        ],
    }
    return checks.get(category, checks["Other"])


def build_parameter_health(meta, series):
    """
    Historical screening only:
    - baseline = engineering baseline in tag master when valid;
      otherwise historical P05-P95.
    - persistence = fraction of recent samples outside baseline.
    - trend = recent median vs prior median.
    - severity combines deviation + persistence + trend.
    No OEM alarm/protection limit is invented here.
    """
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < 20:
        return None

    configured_low = safe_float(meta.get("Baseline Low", ""))
    configured_high = safe_float(meta.get("Baseline High", ""))

    if np.isfinite(configured_low) and np.isfinite(configured_high) and configured_high > configured_low:
        low = configured_low
        high = configured_high
        baseline_source = "Engineering baseline in Tag Master"
    else:
        low = float(s.quantile(0.05))
        high = float(s.quantile(0.95))
        if not np.isfinite(low) or not np.isfinite(high) or high <= low:
            return None
        baseline_source = "Historical P05–P95"

    current = float(s.iloc[-1])
    span = max(abs(high - low), 1e-12)

    outside = (s < low) | (s > high)
    recent_n = min(max(20, len(s) // 10), 120)
    recent = s.iloc[-recent_n:]
    persistence = float(((recent < low) | (recent > high)).mean())

    # Current deviation from the baseline, normalized to baseline width.
    if current < low:
        deviation = (low - current) / span
        side = "Below baseline"
    elif current > high:
        deviation = (current - high) / span
        side = "Above baseline"
    else:
        deviation = 0.0
        side = "Within baseline"

    # Robust trend: median of recent samples vs preceding window.
    window = min(max(20, len(s) // 12), 100)
    if len(s) >= 2 * window:
        recent_med = float(s.iloc[-window:].median())
        prior_med = float(s.iloc[-2 * window:-window].median())
        pct_change = (recent_med - prior_med) / max(abs(prior_med), 1e-9) * 100
    else:
        pct_change = 0.0

    if pct_change > 5:
        direction = "Increasing"
    elif pct_change < -5:
        direction = "Decreasing"
    else:
        direction = "Stable"

    # Risk score: 0–100. This is a screening score, not an alarm limit.
    deviation_component = min(deviation / 0.50, 1.0) * 55
    persistence_component = persistence * 30
    trend_component = min(abs(pct_change) / 25, 1.0) * 15
    risk = min(100.0, deviation_component + persistence_component + trend_component)

    # Status uses persistence as well as instantaneous deviation.
    if deviation >= 0.50 or (persistence >= 0.60 and deviation >= 0.20):
        status = "Critical"
    elif deviation > 0 or persistence >= 0.10 or abs(pct_change) >= 15:
        status = "Attention"
    else:
        status = "Normal"

    category = category_from_meta(meta)
    conf = str(meta.get("Confidence", "")).strip() or "Low"

    return {
        "PLC Tag": str(meta.get("PLC Tag", "")),
        "Parameter": parameter_label(meta),
        "Category": category,
        "Unit": unit_label(meta),
        "Current": current,
        "Baseline Low": low,
        "Baseline High": high,
        "Direction": direction,
        "Trend Change %": pct_change,
        "Outside % (Recent)": persistence * 100,
        "Deviation": deviation,
        "Risk Score": risk,
        "Status": status,
        "Confidence": conf,
        "Confidence Weight": confidence_weight(conf),
        "Baseline Source": baseline_source,
        "Side": side,
    }


def calculate_equipment_health(eq_view, history):
    rows = []
    for _, meta in eq_view.iterrows():
        tag = str(meta.get("PLC Tag", "")).strip()
        if not tag or tag not in history.columns:
            continue
        result = build_parameter_health(meta, history[tag])
        if result is not None:
            rows.append(result)

    if not rows:
        return pd.DataFrame()

    health = pd.DataFrame(rows)

    # Severity-weighted equipment score.
    # High-confidence evidence contributes more strongly to the screening.
    weighted_risk = np.average(
        health["Risk Score"],
        weights=health["Confidence Weight"].clip(lower=0.5),
    )
    critical = int((health["Status"] == "Critical").sum())
    attention = int((health["Status"] == "Attention").sum())

    # A critical parameter dominates the equipment status.
    if critical:
        overall = "CRITICAL"
    elif attention:
        overall = "ATTENTION"
    else:
        overall = "HEALTHY"

    score = int(round(max(0, 100 - weighted_risk)))
    return health, overall, score, critical, attention


# ============================================================
# COMMON HEADER
# ============================================================

st.sidebar.markdown("## ⚙ OPP CONTROL")
st.sidebar.caption("Engineering Monitoring System")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Equipment Health", "Tag Master", "Engineering Trend", "Data Import"],
)

st.markdown("""
<div class="opp-hero">
    <div class="opp-kicker">ORE PROCESSING PLANT • ENGINEERING INTELLIGENCE</div>
    <div class="opp-hero-title">⚙ OPP Engineering Monitoring</div>
    <div class="opp-hero-sub">
        Equipment health • PLC behaviour • process performance • maintenance decision support
    </div>
    <div class="opp-live">
        <span class="opp-live-dot"></span>
        HISTORICAL PLC ANALYTICS • ENGINEERING MODE
    </div>
</div>
""", unsafe_allow_html=True)

high = int((master["Confidence"].astype(str) == "High").sum()) if len(master) else 0
medium = int((master["Confidence"].astype(str) == "Medium").sum()) if len(master) else 0
low = int((master["Confidence"].astype(str) == "Low").sum()) if len(master) else 0

a, b, c, d, e = st.columns(5)
a.metric("Historical Records", f"{len(df):,}")
b.metric("PLC Tags", f"{len(master):,}")
c.metric("High Confidence", f"{high:,}")
d.metric("Medium Confidence", f"{medium:,}")
e.metric("Low Confidence", f"{low:,}")

st.markdown("<div style=\"height:8px\"></div>", unsafe_allow_html=True)

# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":
    st.markdown("### ◈ OPP Engineering Overview")
    st.write(
        "Dashboard ini diarahkan sebagai decision-support untuk monitoring proses, "
        "kesehatan equipment, identifikasi penyimpangan dan penentuan prioritas pemeriksaan."
    )

    x, y, z = st.columns(3)
    x.metric("High", f"{high:,}", "Exact / strong evidence")
    y.metric("Medium", f"{medium:,}", "Equipment / family evidence")
    z.metric("Low", f"{low:,}", "Pattern / limited evidence")

    st.subheader("Area Coverage")
    if len(master):
        ac = master[master["Area"].astype(str) != ""]["Area"].value_counts().sort_index()
        cols = st.columns(4)
        for i, (area, n) in enumerate(ac.items()):
            cols[i % 4].metric(str(area), f"{n} tags")

    st.subheader("Equipment Health — Portfolio View")
    st.caption(
        "Screening otomatis berdasarkan historical behaviour. "
        "Gunakan daftar ini untuk menentukan equipment yang perlu dibuka dan diverifikasi."
    )

    eq_master = master[
        (master["Equipment Code"].astype(str).str.strip() != "")
    ].copy()

    equipment_rows = []
    for eq_code, group in eq_master.groupby("Equipment Code", sort=True):
        result = calculate_equipment_health(group, df)
        if isinstance(result, tuple):
            health, overall, score, critical, attention = result
            eq_name = (
                group["Equipment"].replace("", np.nan).dropna().iloc[0]
                if group["Equipment"].replace("", np.nan).notna().any()
                else "Equipment description not yet mapped"
            )
            equipment_rows.append({
                "Area": str(group["Area"].iloc[0]),
                "Equipment Code": str(eq_code),
                "Equipment": str(eq_name),
                "Health": overall,
                "Score": score,
                "Critical": critical,
                "Attention": attention,
                "Parameters": len(health),
            })

    if equipment_rows:
        portfolio = pd.DataFrame(equipment_rows)
        portfolio = portfolio.sort_values(
            ["Health", "Score", "Critical", "Attention"],
            ascending=[True, True, False, False],
        )
        st.dataframe(portfolio, use_container_width=True, height=430)
    else:
        st.info("Belum ada equipment yang mempunyai historical data yang cukup.")


# ============================================================
# EQUIPMENT HEALTH
# ============================================================

elif page == "Equipment Health":
    st.markdown("### ◈ Equipment Health — Engineering Decision Support")
    st.caption(
        "Preliminary screening from historical PLC behaviour. "
        "This is NOT an alarm/protection limit and does not replace OEM limits, "
        "operating philosophy, inspection standards, calibration requirements, "
        "inspection standards, or engineer judgement."
    )

    area_options = ["All"] + sorted(
        [str(x) for x in master["Area"].unique() if str(x).strip()]
    )
    selected_area = st.selectbox("Area", area_options, key="health_area")

    area_view = master if selected_area == "All" else master[master["Area"] == selected_area]
    eq_codes = sorted(
        [str(x) for x in area_view["Equipment Code"].unique() if str(x).strip()]
    )

    if not eq_codes:
        st.warning("No equipment code is available for this selection.")
    else:
        selected_eq = st.selectbox("Equipment Code", eq_codes, key="health_equipment")
        ev = area_view[area_view["Equipment Code"] == selected_eq].copy()

        names = ev["Equipment"].replace("", np.nan).dropna()
        eq_name = names.iloc[0] if len(names) else "Equipment description not yet mapped"

        st.markdown(f'<div class="opp-equipment-title">{selected_eq}</div>', unsafe_allow_html=True)
        st.caption(eq_name)

        result = calculate_equipment_health(ev, df)

        if not isinstance(result, tuple):
            st.warning("No sufficient historical data is available for this equipment.")
        else:
            health, overall, score, critical, attention = result

            icon = "🔴" if overall == "CRITICAL" else ("🟡" if overall == "ATTENTION" else "🟢")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Equipment Health", f"{icon} {overall}")
            c2.metric("Screening Score", f"{score}/100")
            c3.metric("Parameters", f"{len(health):,}")
            c4.metric("Critical / Attention", f"{critical} / {attention}")

            # ------------------------------------------------
            # Top attention / critical parameters
            # ------------------------------------------------
            st.markdown("#### 🔎 Engineering Focus — Top Parameters")
            flagged = health[health["Status"] != "Normal"].copy()

            if flagged.empty:
                st.success("No parameter is currently outside the preliminary historical screening.")
            else:
                flagged = flagged.sort_values(
                    ["Status", "Risk Score", "Outside % (Recent)"],
                    ascending=[True, False, False],
                )
                display_flagged = flagged[
                    [
                        "PLC Tag", "Parameter", "Category", "Current", "Unit",
                        "Baseline Low", "Baseline High", "Direction",
                        "Trend Change %", "Outside % (Recent)",
                        "Risk Score", "Status", "Confidence",
                    ]
                ].copy()
                st.dataframe(display_flagged, use_container_width=True, height=260)

                top = flagged.iloc[0]
                st.markdown("##### Priority signal")
                st.warning(
                    f"**{top['PLC Tag']} — {top['Parameter']}** | "
                    f"Status: **{top['Status']}** | "
                    f"Risk screening: **{top['Risk Score']:.0f}/100** | "
                    f"Direction: **{top['Direction']}** | "
                    f"Recent outside-baseline: **{top['Outside % (Recent)']:.1f}%**."
                )

                st.markdown("##### Suggested engineering checks")
                for item in engineering_checks(top["Category"]):
                    st.write(f"• {item}")

            # ------------------------------------------------
            # Parameter condition
            # ------------------------------------------------
            st.markdown("#### Parameter Condition")
            parameter_view = health[
                [
                    "PLC Tag", "Parameter", "Category", "Unit", "Current",
                    "Baseline Low", "Baseline High", "Direction",
                    "Trend Change %", "Outside % (Recent)",
                    "Risk Score", "Status", "Confidence", "Baseline Source",
                ]
            ].copy()
            st.dataframe(parameter_view, use_container_width=True, height=440)

            # ------------------------------------------------
            # Category summary
            # ------------------------------------------------
            st.markdown("#### Parameter Group Summary")
            category_summary = (
                health.groupby("Category", dropna=False)
                .agg(
                    Parameters=("PLC Tag", "count"),
                    Attention=("Status", lambda x: int((x == "Attention").sum())),
                    Critical=("Status", lambda x: int((x == "Critical").sum())),
                    Avg_Risk=("Risk Score", "mean"),
                )
                .reset_index()
                .rename(columns={"Avg_Risk": "Average Risk Score"})
            )
            category_summary["Average Risk Score"] = category_summary["Average Risk Score"].round(1)
            st.dataframe(category_summary, use_container_width=True, hide_index=True)

            st.info(
                "Engineering workflow: identify flagged parameter → open Engineering Trend → "
                "correlate with related parameters/process condition → verify physically/OEM/design limit → "
                "then decide inspection or maintenance action. The dashboard does not automatically create a work order."
            )


# ============================================================
# TAG MASTER
# ============================================================

elif page == "Tag Master":
    st.markdown("### ◈ PLC Tag Master")
    st.caption(
        "Gunakan tabel ini sebagai kamus resmi mapping PLC. "
        "Confidence menunjukkan kekuatan evidence, bukan final engineering approval."
    )

    q = st.text_input("Search tag / equipment / parameter")
    area = st.selectbox(
        "Area",
        ["All"] + sorted([x for x in master["Area"].unique() if str(x).strip()]),
        key="tag_area",
    )
    conf = st.selectbox(
        "Confidence",
        ["All", "High", "Medium", "Low"],
        key="tag_conf",
    )

    view = master.copy()
    if q:
        mask = view.astype(str).apply(
            lambda s: s.str.contains(q, case=False, na=False, regex=False)
        ).any(axis=1)
        view = view[mask]
    if area != "All":
        view = view[view["Area"] == area]
    if conf != "All":
        view = view[view["Confidence"] == conf]

    st.dataframe(view, use_container_width=True, height=620)
    st.download_button(
        "Download Tag Master CSV",
        master.to_csv(index=False).encode("utf-8"),
        "OPP_Tag_Master_Phase5.csv",
        "text/csv",
    )


# ============================================================
# ENGINEERING TREND
# ============================================================

elif page == "Engineering Trend":
    st.markdown("### ◈ Engineering Trend — Equipment View")
    st.caption(
        "Pilih equipment untuk melihat seluruh tag yang terkait. "
        "Setiap parameter tetap mempunyai panel trend dan unitnya sendiri."
    )

    area_options = ["All"] + sorted(
        [str(x) for x in master["Area"].unique() if str(x).strip()]
    )
    selected_area = st.selectbox("Area", area_options, key="trend_area")

    area_view = master if selected_area == "All" else master[master["Area"] == selected_area]
    eq_codes = sorted(
        [str(x) for x in area_view["Equipment Code"].unique() if str(x).strip()]
    )

    if not eq_codes:
        st.warning("No equipment code is mapped for this selection yet.")
    else:
        selected_eq = st.selectbox("Equipment Code", eq_codes, key="trend_equipment")
        eq_view = area_view[area_view["Equipment Code"] == selected_eq].copy()

        names = eq_view["Equipment"].replace("", np.nan).dropna()
        eq_name = names.iloc[0] if len(names) else "Equipment description not yet mapped"

        st.markdown(f'<div class="opp-equipment-title">{selected_eq}</div>', unsafe_allow_html=True)
        st.caption(f"{eq_name} • {len(eq_view)} associated PLC tags")

        if df.empty or "ArchiveTime" not in df.columns:
            st.warning("Historical PLC data is not available.")
        else:
            min_d = df["ArchiveTime"].min().date()
            max_d = df["ArchiveTime"].max().date()

            c1, c2, c3 = st.columns([1, 1, 2])
            start = c1.date_input(
                "Start Date", min_d, min_value=min_d, max_value=max_d, key="trend_start"
            )
            end = c2.date_input(
                "End Date", max_d, min_value=min_d, max_value=max_d, key="trend_end"
            )

            if start > end:
                st.error("Start Date cannot be later than End Date.")
            else:
                date_mask = (
                    (df["ArchiveTime"].dt.date >= start)
                    & (df["ArchiveTime"].dt.date <= end)
                )

                rows = []
                for _, meta in eq_view.iterrows():
                    tag = str(meta.get("PLC Tag", "")).strip()
                    if not tag or tag not in df.columns:
                        continue

                    d = df.loc[date_mask, ["ArchiveTime", tag]].copy()
                    d[tag] = pd.to_numeric(d[tag], errors="coerce")
                    s = d[tag].dropna()
                    if len(s) == 0:
                        continue

                    rows.append((meta, d, s))

                if not rows:
                    st.warning("No historical PLC data found for the mapped tags of this equipment.")
                else:
                    # Summary
                    st.markdown("#### Equipment Parameter Summary")
                    summary = []
                    for meta, d, s in rows:
                        summary.append({
                            "PLC Tag": meta["PLC Tag"],
                            "Parameter": parameter_label(meta),
                            "Category": category_from_meta(meta),
                            "Unit": unit_label(meta),
                            "Current": float(s.iloc[-1]),
                            "Average": float(s.mean()),
                            "Min": float(s.min()),
                            "Max": float(s.max()),
                            "Confidence": str(meta.get("Confidence", "") or "Low"),
                        })
                    st.dataframe(
                        pd.DataFrame(summary),
                        use_container_width=True,
                        height=280,
                    )

                    # Optional parameter focus, then all equipment trends.
                    tag_options = [
                        f"{m['PLC Tag']} — {parameter_label(m)}"
                        for m, _, _ in rows
                    ]
                    focus = st.selectbox(
                        "Focus Parameter (optional)",
                        ["All"] + tag_options,
                        key="trend_focus",
                    )

                    st.markdown("#### Parameter Trends")

                    selected_rows = rows
                    if focus != "All":
                        focus_tag = focus.split(" — ", 1)[0]
                        selected_rows = [r for r in rows if str(r[0]["PLC Tag"]) == focus_tag]

                    for meta, d, s in selected_rows:
                        tag = str(meta["PLC Tag"])
                        label = parameter_label(meta)
                        unit = unit_label(meta)

                        st.markdown(f"**{tag} — {label}**")
                        st.caption(
                            f"Category: {category_from_meta(meta)} | "
                            f"Unit: {unit} | "
                            f"Confidence: {meta.get('Confidence', '') or 'Low'} | "
                            f"Reference: {meta.get('Reference Source', '') or 'Not available'}"
                        )

                        chart = d.set_index("ArchiveTime")[tag].dropna()
                        if len(chart):
                            st.line_chart(chart, height=230)
                        else:
                            st.info("No valid data in selected date range.")

                    st.info(
                        "Trend panels are intentionally separated by parameter/unit. "
                        "Do not combine flow, temperature, pressure and vibration on one Y-axis."
                    )


# ============================================================
# DATA IMPORT
# ============================================================

elif page == "Data Import":
    st.markdown("### ◈ Daily PLC Excel Import — Validation")
    st.caption(
        "Fase ini memvalidasi file Excel sebelum data dimasukkan ke historical dataset."
    )

    uploaded = st.file_uploader(
        "Upload daily PLC export (.xlsx)",
        type=["xlsx"],
    )

    if uploaded:
        try:
            incoming = pd.read_excel(uploaded)
        except Exception as exc:
            st.error(f"Unable to read Excel file: {exc}")
        else:
            if "ArchiveTime" not in incoming.columns:
                st.error("ArchiveTime not found.")
            else:
                incoming["ArchiveTime"] = pd.to_datetime(
                    incoming["ArchiveTime"], errors="coerce"
                )
                known = set(df["ArchiveTime"]) if "ArchiveTime" in df.columns else set()

                q1, q2, q3 = st.columns(3)
                q1.metric("Rows", f"{len(incoming):,}")
                q2.metric(
                    "New timestamps",
                    f"{(~incoming['ArchiveTime'].isin(known)).sum():,}",
                )
                q3.metric(
                    "Invalid timestamps",
                    f"{incoming['ArchiveTime'].isna().sum():,}",
                )

                st.dataframe(incoming.head(30), use_container_width=True)

                required_history = ["ArchiveTime"]
                missing = [c for c in required_history if c not in incoming.columns]
                if missing:
                    st.error(f"Missing required columns: {missing}")
                else:
                    st.success("Excel structure passed the basic validation.")
                    st.info(
                        "Permanent database append will be implemented after mapping validation. "
                        "For now this upload is validation-only and does not modify the repository."
                    )
