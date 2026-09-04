import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import re
from urllib.parse import quote
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="OPP Engineering Monitoring", page_icon="⚙️", layout="wide")
ROOT = Path(__file__).resolve().parent

# --- Professional UI theme ---
st.markdown("""<style>
.main .block-container{padding-top:1.15rem;padding-bottom:3rem;max-width:1500px}
/* ===== LEFT SIDEBAR — dashboard reference layout ===== */
[data-testid="stSidebar"]{
    background:#fbfcfe!important;
    border-right:1px solid #e4e8ef!important;
}
[data-testid="stSidebar"] > div:first-child{padding-top:.55rem!important}
[data-testid="stSidebar"] .block-container{padding:.45rem .55rem 1rem!important}
[data-testid="stSidebar"] .stRadio>label{
    font-size:.67rem!important;font-weight:800!important;
    color:#6938d6!important;letter-spacing:.03em!important;
    text-transform:uppercase!important;margin:.25rem 0 .45rem!important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"]{
    gap:.12rem!important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label{
    padding:.50rem .48rem!important;
    border-radius:.46rem!important;
    font-size:.78rem!important;
    line-height:1.05!important;
    min-height:31px!important;
    color:#24344d!important;
    font-weight:650!important;
    border:1px solid transparent!important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover{
    background:#f0edff!important;color:#2f62b5!important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked){
    background:#e9e6ff!important;
    color:#1769e0!important;
    font-weight:750!important;
    border-color:#e3defc!important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > div:first-child{
    margin-right:.38rem!important;
}



/* V21 — Data Coverage visual polish */
.coverage-date-v19,
.coverage-date-v19 b,
.coverage-date-v19 small,
.coverage-label-v21,
.coverage-value-v21,
.coverage-note-v21{
    font-family:inherit!important;
}
.coverage-date-v19>div{
    padding-top:.34rem!important;
    padding-bottom:.42rem!important;
}
.coverage-date-v19 b{
    font-size:.72rem!important;
    font-weight:700!important;
    color:#344054!important;
}
.coverage-date-v19 small{
    font-size:.60rem!important;
    color:#98a2b3!important;
    top:.38rem!important;
}
.coverage-icon-v19{
    font-size:.76rem!important;
    color:#667085!important;
    top:.31rem!important;
}
.coverage-summary-v21{
    display:flex!important;
    align-items:center!important;
    gap:.72rem!important;
    padding:.52rem 0 .28rem!important;
}
.coverage-ring-v21{
    width:58px!important;
    height:58px!important;
    min-width:58px!important;
    border-radius:50%!important;
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    background:#087443!important;
    color:#fff!important;
    border:4px solid #087443!important;
    box-shadow:0 3px 8px rgba(8,116,67,.18)!important;
    position:relative!important;
}
.coverage-ring-v21:after{
    content:""!important;
    position:absolute!important;
    inset:0!important;
    border-radius:50%!important;
    border:1px solid rgba(255,255,255,.16)!important;
}
.coverage-ring-v21 span{
    position:relative!important;
    z-index:1!important;
    color:#fff!important;
    font-family:inherit!important;
    font-size:.72rem!important;
    font-weight:800!important;
    letter-spacing:-.01em!important;
}
.coverage-copy-v21{
    min-width:0!important;
}
.coverage-label-v21{
    color:#667085!important;
    font-size:.62rem!important;
    font-weight:500!important;
    line-height:1.2!important;
}
.coverage-value-v21{
    color:#344054!important;
    font-size:.76rem!important;
    font-weight:750!important;
    line-height:1.35!important;
    margin-top:.10rem!important;
}
.coverage-note-v21{
    color:#98a2b3!important;
    font-size:.58rem!important;
    font-weight:500!important;
    line-height:1.25!important;
    margin-top:.04rem!important;
}

/* V20 — visible but subtle sidebar boundary. No fixed width. */
[data-testid="stSidebar"]{
    box-shadow:1px 0 0 #e5e7eb;
}
[data-testid="stSidebar"] > div:first-child{
    border-right:1px solid #e5e7eb;
}

/* V19 SIDEBAR — clean, compact, professional */
.opp-brand-v19{padding:.15rem .15rem .95rem!important}
.opp-brand-row{display:flex;align-items:center;gap:.62rem}
.brand-gear-v19{
    width:35px;height:35px;border-radius:10px;display:flex;align-items:center;
    justify-content:center;background:#6738d4;color:#fff;font-size:1.18rem;
    box-shadow:0 4px 10px rgba(103,56,212,.18);
}
.opp-brand-title-v19{font-size:1.15rem;font-weight:850;color:#182230;line-height:1.05}
.opp-brand-sub-v19{margin-top:.16rem;color:#667085;font-size:.62rem;font-weight:550}
.sidebar-divider-v19{height:1px;background:#e6e9ef;margin:.35rem -.25rem .75rem}
.sidebar-divider-v19.compact{margin-top:1rem;margin-bottom:.7rem}
.sidebar-section-title-v19{
    color:#6738d4;font-size:.62rem;font-weight:850;letter-spacing:.055em;
    text-transform:uppercase;margin:.45rem .05rem .55rem;
}
.coverage-date-v19>div{position:relative;padding:.28rem 0 .38rem 1.38rem;color:#344054;font-size:.61rem;line-height:1.1}
.coverage-date-v19 b{font-size:.63rem;font-weight:750}
.coverage-date-v19 small{position:absolute;right:0;top:.31rem;color:#98a2b3;font-size:.53rem}
.coverage-icon-v19{position:absolute;left:0;top:.23rem;color:#667085;font-size:.72rem}
.coverage-summary-v19{display:flex;align-items:center;gap:.65rem;padding:.25rem 0 .15rem}
.sidebar-ring-v19{
    width:51px;height:51px;border-radius:50%;display:flex;align-items:center;
    justify-content:center;font-size:.66rem;font-weight:850;color:#344054;
    background:conic-gradient(#12b76a var(--pct),#e9edf2 0);position:relative;flex:0 0 auto;
}
.sidebar-ring-v19:after{content:"";position:absolute;inset:6px;background:#fbfcfe;border-radius:50%}
.sidebar-ring-v19 span{position:relative;z-index:1}
.coverage-label-v19{color:#667085;font-size:.58rem;line-height:1.2}
.coverage-value-v19{color:#344054;font-size:.73rem;font-weight:800;margin-top:.12rem}
.coverage-note-v19{color:#98a2b3;font-size:.53rem;margin-top:.08rem}
.system-status-v19{border:1px solid #e7ebf1;background:#fff;border-radius:9px;padding:.62rem .65rem}
.status-row-v19{display:flex;align-items:center;gap:.38rem;color:#079455;font-size:.67rem}
.status-dot-v19{width:7px;height:7px;border-radius:50%;background:#12b76a;box-shadow:0 0 0 3px rgba(18,183,106,.10)}
.status-live-v19{margin-left:auto;font-size:.5rem;font-weight:850;color:#079455;background:#ecfdf3;border-radius:99px;padding:.16rem .34rem}
.status-update-v19{color:#98a2b3;font-size:.54rem;margin-top:.42rem}
.status-update-v19 b{color:#475467;font-weight:700}
.sidebar-footer-v19{margin-top:1rem;padding:.7rem .05rem 0;border-top:1px solid #eef0f3;color:#98a2b3;font-size:.5rem;line-height:1.55}
.sidebar-footer-v19 span{display:block}

/* Hide obsolete V18 filter/quality/database elements. */
.sidebar-filter-icon,.sidebar-filter-wrap,.sidebar-select,.sidebar-quality-btn,
.sidebar-db-card,.sidebar-connected,.sidebar-meta-row,.sidebar-coverage{display:none!important}

/* Clean navigation surface. */
[data-testid="stSidebar"] [data-testid="stRadio"]{margin-top:.1rem!important}
[data-testid="stSidebar"] [data-testid="stRadio"]>label{display:none!important}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"]{gap:.12rem!important}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radio"]{
    min-height:35px!important;padding:.43rem .55rem!important;border-radius:8px!important;
    color:#344054!important;font-size:.68rem!important;font-weight:650!important;
    border:1px solid transparent!important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radio"]:hover{background:#f5f2ff!important}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radio"][aria-checked="true"]{
    background:#eee8ff!important;color:#4f24bd!important;border-color:#e4dbff!important;font-weight:800!important;
}

.opp-brand{
    padding:.05rem .15rem .85rem!important;
    border-bottom:0!important;
    margin-bottom:.18rem!important;
}
.opp-brand-title{
    font-size:1.18rem!important;font-weight:850!important;
    color:#182230!important;line-height:1!important;
}
.opp-brand-title .brand-gear{color:#6738d4!important}
.opp-brand-sub{
    color:#667085!important;font-size:.65rem!important;
    margin:.22rem 0 0 2.35rem!important;
    font-weight:550!important;
}
.sidebar-divider{
    height:1px;background:#e4e8ef;margin:.65rem -.55rem .7rem;
}
.sidebar-section-title{
    color:#6938d6;font-size:.65rem;font-weight:850;
    letter-spacing:.04em;text-transform:uppercase;
    margin:.72rem .18rem .42rem;
}
.sidebar-meta-row{
    display:flex;align-items:center;gap:.48rem;
    padding:.27rem .16rem;color:#344054;font-size:.66rem;
    line-height:1.15;
}
.sidebar-meta-row .sicon{width:15px;text-align:center;color:#667085;font-size:.78rem}
.sidebar-meta-row .svalue{font-weight:700;color:#344054;white-space:nowrap}
.sidebar-meta-row .slabel{margin-left:auto;color:#667085;font-size:.56rem}
.sidebar-coverage{
    display:flex;align-items:center;gap:.58rem;margin:.18rem 0 .55rem;
}
.sidebar-ring{
    width:52px;height:52px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    font-size:.67rem;font-weight:850;color:#344054;
    background:conic-gradient(#12b76a var(--pct),#e7ebf0 0);
    position:relative;flex:0 0 auto;
}
.sidebar-ring:after{
    content:"";position:absolute;inset:6px;background:#fbfcfe;border-radius:50%;
}
.sidebar-ring span{position:relative;z-index:1}
.sidebar-coverage-text{font-size:.61rem;color:#667085;line-height:1.4}
.sidebar-coverage-text b{display:block;color:#344054;font-size:.75rem}
.sidebar-coverage-text .available{color:#667085}
.sidebar-quality-btn{
    border:1px solid #ddd7fb;border-radius:6px;background:#fff;
    color:#6938d6;font-size:.62rem;font-weight:750;
    text-align:center;padding:.43rem .25rem;margin:.15rem 0 .35rem;
}
.sidebar-connected{
    display:flex;align-items:center;gap:.42rem;
    color:#12a66a;font-size:.66rem;font-weight:750;padding:.28rem .16rem;
}
.sidebar-db-card{
    margin:.9rem -.05rem 0;padding:.62rem .55rem;
    background:#fff;border:1px solid #e7ebf1;border-radius:7px;
    box-shadow:0 1px 3px rgba(16,24,40,.04);
}
.sidebar-db-title{font-size:.56rem;color:#667085;margin-bottom:.18rem}
.sidebar-db-value{font-size:.68rem;color:#079455;font-weight:800}
.sidebar-db-dot{display:inline-block;width:7px;height:7px;background:#12b76a;border-radius:50%;margin-right:.3rem}
.sidebar-version{text-align:right;color:#98a2b3;font-size:.52rem;margin-top:.18rem}
.sidebar-select .stSelectbox>label{display:none!important}
.sidebar-select [data-baseweb="select"]{
    min-height:31px!important;border:1px solid #dfe5ee!important;
    border-radius:6px!important;background:#fff!important;
}
.sidebar-select [data-baseweb="select"]>div{
    min-height:31px!important;padding:0 .45rem!important;
    font-size:.67rem!important;color:#344054!important;
}
.sidebar-select{margin-bottom:.18rem!important}\n[data-testid="stSidebar"] .stSelectbox{margin-bottom:.18rem!important}\n[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"]{box-shadow:0 1px 2px rgba(16,24,40,.03)!important}
.sidebar-filter-icon{
    position:absolute;left:.62rem;z-index:2;line-height:31px;
    color:#667085;font-size:.72rem;pointer-events:none;
}
.sidebar-filter-wrap{position:relative}

.opp-page-title{font-size:1.75rem;font-weight:800;color:#1d2939;margin-bottom:.15rem}.opp-page-sub{color:#667085;font-size:.88rem;margin-bottom:1rem}
.dashboard-kpi{color:#fff!important;border:0!important;border-radius:5px!important;min-height:96px;padding:.95rem 1rem!important;box-shadow:0 3px 8px rgba(18,44,88,.14)!important;text-align:center;display:flex;flex-direction:column;justify-content:center}
.dashboard-kpi .opp-card-title,.dashboard-kpi .opp-card-value,.dashboard-kpi .opp-card-small{color:#fff!important}
.dashboard-kpi .opp-card-title{font-size:.76rem!important;font-weight:750!important;line-height:1.2;margin-bottom:.35rem}
.dashboard-kpi .opp-card-value{font-size:1.75rem!important;line-height:1.05!important;font-weight:850!important}
.dashboard-kpi .opp-card-small{font-size:.68rem!important;margin-top:.35rem;font-weight:600}
.dashboard-action-kpi,.dashboard-action-kpi *{color:#fff!important}
.dashboard-action-kpi{background:linear-gradient(135deg,#4c36ae,#704bd7)!important;border-radius:8px!important}
.kpi-blue{background:linear-gradient(135deg,#1720a5,#2146cf)!important}.kpi-cyan{background:linear-gradient(135deg,#078fd2,#17b6df)!important}.kpi-purple{background:linear-gradient(135deg,#4c36ae,#704bd7)!important}.kpi-orange{background:linear-gradient(135deg,#ef7d18,#f5a623)!important}.kpi-red{background:linear-gradient(135deg,#d9364f,#f0445e)!important}
.kpi-purple .opp-card-title,.kpi-purple .opp-card-value,.kpi-purple .opp-card-small{color:#fff!important}
.dashboard-row{margin-bottom:.85rem}
/* Keep paired dashboard columns visually locked to the same grid. */
[data-testid="stHorizontalBlock"]{align-items:stretch}
[data-testid="stHorizontalBlock"] > [data-testid="column"]{display:flex;flex-direction:column}
[data-testid="stHorizontalBlock"] > [data-testid="column"] > div{width:100%}
.dashboard-panel{background:#f8fafc;border:1px solid #dfe5ee;border-radius:8px;padding:.78rem .85rem;margin:0;box-sizing:border-box;overflow:hidden;position:relative}
.dashboard-panel.tall{min-height:365px;height:365px}.dashboard-panel.medium{min-height:286px;height:286px}.dashboard-panel.short{min-height:210px;height:210px}
.dashboard-panel-head{height:34px;box-sizing:border-box;display:flex;align-items:center;background:#e9eef5;border:1px solid #dce3ec;border-radius:5px;padding:.45rem .7rem;margin:-.78rem -.85rem .72rem;font-weight:800;color:#26364a;font-size:.82rem;line-height:1.15;letter-spacing:.01em}
.dashboard-panel-sub{font-size:.75rem;color:#7b8798;margin:.05rem 0 .65rem;line-height:1.35}
/* Strong contrast rule: dark surfaces always use light text. */
.dashboard-panel .dashboard-kpi.kpi-blue *,
.dashboard-panel .dashboard-kpi.kpi-cyan *,
.dashboard-panel .dashboard-kpi.kpi-orange *,
.dashboard-panel .dashboard-kpi.kpi-red *,
.dashboard-panel .dashboard-kpi.kpi-purple *,
.dashboard-kpi.kpi-blue *, .dashboard-kpi.kpi-cyan *,
.dashboard-kpi.kpi-orange *, .dashboard-kpi.kpi-red *,
.dashboard-kpi.kpi-purple *{color:#fff!important}
/* Status colours: healthy=green, warning=orange, urgent=red. */
.condition-card.condition-healthy{border-top-color:#12b76a!important}
.condition-card.condition-deteriorating{border-top-color:#f5b82e!important}
.condition-card.condition-attention{border-top-color:#f79009!important}
.condition-card.condition-critical{border-top-color:#f04438!important}
.status-healthy{color:#079455!important}.status-deteriorating{color:#b54708!important}.status-attention{color:#c4320a!important}.status-critical{color:#d92d20!important}
.condition-card{background:#fff;border:1px solid #dfe5ed;border-radius:8px;padding:.78rem .82rem;min-height:104px;box-shadow:0 2px 6px rgba(16,24,40,.04);box-sizing:border-box}
.condition-card .count{font-size:1.55rem;font-weight:850;color:#1d2939;line-height:1.1}.condition-card .label{font-size:.69rem;font-weight:800;color:#667085}.condition-card .pct{font-size:.68rem;color:#98a2b3;margin-top:.25rem;line-height:1.25}
.condition-healthy{border-top:4px solid #12b76a}.condition-deteriorating{border-top:4px solid #f5b82e}.condition-attention{border-top:4px solid #f79009}.condition-critical{border-top:4px solid #f04438}
.focus-box{background:linear-gradient(135deg,#eef6ff,#f8fbff);border:1px solid #b9d9ff;border-radius:8px;padding:.82rem .9rem;color:#344054;line-height:1.45;font-size:.8rem}
.focus-box b{color:#175cd3}
.area-card{background:#fff;border:1px solid #e1e6ee;border-radius:8px;padding:.75rem .8rem;box-shadow:0 2px 6px rgba(16,24,40,.04);min-height:105px;box-sizing:border-box}.area-card .area-title{font-weight:800;color:#344054;font-size:.76rem}.area-card .area-number{font-size:1.35rem;font-weight:850;color:#1d2939;margin-top:.3rem}.area-card .area-pct{font-size:.68rem;color:#667085}.signal-bar{height:6px;border-radius:8px;background:#e9edf3;margin-top:.48rem;overflow:hidden}.signal-fill{height:100%;border-radius:8px;background:linear-gradient(90deg,#1597e5,#ef476f)}
.priority-line{margin:.45rem 0}.priority-line-top{display:flex;justify-content:space-between;align-items:center;font-size:.75rem;color:#475467;margin-bottom:.2rem}.priority-line-top b{color:#1d2939}.priority-line .signal-fill{background:linear-gradient(90deg,#2948d3,#1597e5)}
.opp-card-title{font-size:.78rem;color:#667085;font-weight:600;margin-bottom:.35rem}.opp-card-value{font-size:1.25rem;color:#1d2939;font-weight:800;line-height:1.2;white-space:normal}.opp-card-small{font-size:.76rem;color:#667085;margin-top:.35rem}
.status-normal{border-left:4px solid #12b76a}.status-deteriorating{border-left:4px solid #f5a524}.status-attention{border-left:4px solid #f79009}.status-critical{border-left:4px solid #f04438}.status-healthy{border-left:4px solid #12b76a}
.opp-section{margin-top:1.15rem;margin-bottom:.65rem;font-size:1.05rem;font-weight:800;color:#1d2939}.opp-note{background:#eff8ff;border:1px solid #b2ddff;border-radius:12px;padding:.85rem 1rem;color:#175cd3;font-size:.86rem}.opp-warning{background:#fffaeb;border:1px solid #fedf89;border-radius:12px;padding:.85rem 1rem;color:#9b6500;font-size:.86rem}
.priority-kpi{background:#fff;border:1px solid #e4e7ec;border-radius:14px;padding:.9rem 1rem;min-height:105px;box-shadow:0 1px 2px rgba(16,24,40,.04)}
.priority-kpi>div{font-size:.76rem;font-weight:700;color:#667085}.priority-kpi strong{display:block;font-size:1.65rem;line-height:1.15;color:#1d2939;margin:.3rem 0}.priority-kpi span{font-size:.7rem;color:#98a2b3}.priority-p1{border-top:4px solid #f04438}.priority-p2{border-top:4px solid #f79009}.priority-p3{border-top:4px solid #f5a524}.priority-p4{border-top:4px solid #12b76a}.priority-focus{border-top:4px solid #175cd3}
.priority-matrix-card{background:linear-gradient(180deg,#fff,#f8fafc);border:1px solid #e4e7ec;border-radius:16px;padding:1rem;min-height:155px;position:relative;box-shadow:0 2px 5px rgba(16,24,40,.05);transition:transform .15s ease,box-shadow .15s ease}.priority-matrix-card:hover{transform:translateY(-2px);box-shadow:0 7px 18px rgba(16,24,40,.09)}.matrix-icon{font-size:1.15rem}.matrix-code{font-size:.72rem;font-weight:800;color:#667085;margin-top:.25rem}.matrix-title{font-size:.88rem;font-weight:700;color:#344054}.matrix-count{font-size:2rem;font-weight:850;color:#1d2939;margin-top:.25rem}.matrix-note{font-size:.7rem;color:#98a2b3;margin-top:.2rem}

/* Dashboard v4: true panel alignment and readable contrast */
.dashboard-grid-gap{height:.65rem}
.dashboard-panel-wrap{
    background:#f8fafc;
    border:1px solid #dfe5ee;
    border-radius:8px;
    overflow:hidden;
    box-sizing:border-box;
}
.dashboard-panel-header{
    height:38px;
    display:flex;
    align-items:center;
    padding:0 .78rem;
    background:#edf1f6;
    border-bottom:1px solid #dfe5ee;
    color:#25364d;
    font-size:.82rem;
    font-weight:800;
    line-height:1;
}
.dashboard-panel-body{padding:.72rem .78rem .78rem}
.dashboard-panel-body .dashboard-panel-sub{margin:0 0 .65rem}
.dashboard-row-wrap{
    display:grid;
    grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);
    gap:.65rem;
    align-items:stretch;
}
.dashboard-row-wrap > .dash-cell{
    min-width:0;
}
.dashboard-kpi{
    min-height:108px!important;
    border-radius:5px!important;
}
.dashboard-kpi .opp-card-title{font-size:.74rem!important}
.dashboard-kpi .opp-card-value{font-size:1.7rem!important}
.dashboard-kpi .opp-card-small{font-size:.67rem!important}
.dashboard-kpi.kpi-blue,.dashboard-kpi.kpi-cyan,.dashboard-kpi.kpi-orange,
.dashboard-kpi.kpi-red,.dashboard-kpi.kpi-purple,
.dashboard-action-kpi,.dashboard-action-kpi *{
    color:#fff!important;
}
.dashboard-action-kpi{
    background:linear-gradient(135deg,#5037b5,#704bd7)!important;
}
.condition-card{
    min-height:116px;
    display:flex;
    flex-direction:column;
    justify-content:flex-start;
}
.condition-card .count{margin-top:.32rem}
.condition-card .pct{margin-top:.25rem;min-height:1.8rem}
.dashboard-panel-wrap .stButton{margin-top:.28rem!important}
.dashboard-panel-wrap .stButton>button{
    border:1px solid #d9e0e8!important;
    background:#fff!important;
    color:#344054!important;
    font-weight:650!important;
    min-height:36px!important;
    border-radius:7px!important;
}
.dashboard-panel-wrap .stButton>button:hover{
    border-color:#8db7ef!important;
    background:#f5f9ff!important;
}
.dashboard-panel-wrap .stMetric{
    padding:.05rem 0!important;
}
.dashboard-panel-wrap .stMetric label{font-size:.72rem!important}
.dashboard-panel-wrap .stMetric [data-testid="stMetricValue"]{font-size:1.45rem!important}
.dq-card{
    background:#fff;border:1px solid #e3e8ef;border-radius:8px;
    padding:.72rem .7rem;min-height:105px;box-sizing:border-box;
}
.dq-label{font-size:.7rem;color:#667085;font-weight:700}
.dq-value{font-size:1.55rem;color:#1d2939;font-weight:850;margin-top:.28rem}
.dq-high{color:#079455!important}.dq-medium{color:#dc6803!important}.dq-low{color:#d92d20!important}
.area-card{
    min-height:112px!important;
    padding:.7rem .72rem!important;
}
.area-card .signal-bar{margin-top:.45rem}
.priority-line{margin:.55rem 0!important}
.priority-line .signal-bar{height:7px}
.priority-line.p1 .signal-fill{background:#f04438}
.priority-line.p2 .signal-fill{background:#f79009}
.priority-line.p3 .signal-fill{background:#f5b82e}
.priority-line.p4 .signal-fill{background:#12b76a}
@media(max-width:900px){
    .dashboard-row-wrap{grid-template-columns:1fr}
}

/* ===== Dashboard v5 polish ===== */
.dashboard-intro{margin-bottom:.72rem!important}
.condition-card .label.status-healthy,.condition-card .label.status-deteriorating,.condition-card .label.status-attention,.condition-card .label.status-critical{border-left:0!important;padding-left:0!important;display:block;margin-left:0}
.condition-card.condition-healthy{background:linear-gradient(180deg,#f3fff8,#ffffff)!important}
.condition-card.condition-deteriorating{background:linear-gradient(180deg,#fffaf0,#ffffff)!important}
.condition-card.condition-attention{background:linear-gradient(180deg,#fff7ed,#ffffff)!important}
.condition-card.condition-critical{background:linear-gradient(180deg,#fff5f5,#ffffff)!important}
[data-testid="stVerticalBlockBorderWrapper"]{background:#f8fafc!important}
.dashboard-panel-body{background:#f8fafc}
.priority-summary-card{border:1px solid rgba(255,255,255,.18);border-radius:10px;min-height:118px;padding:.82rem .85rem;box-sizing:border-box;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 4px 10px rgba(16,24,40,.12);color:#fff!important}
.priority-summary-card .psc-top{display:flex;align-items:center;gap:.42rem;font-size:.76rem;font-weight:800;color:#fff!important}
.priority-summary-card .psc-dot{width:10px;height:10px;border-radius:50%;display:inline-block;flex:0 0 10px;background:#fff!important;box-shadow:0 0 0 3px rgba(255,255,255,.18)}
.priority-summary-card .psc-count{font-size:1.85rem;font-weight:850;line-height:1;margin-top:.3rem;color:#fff!important}
.priority-summary-card .psc-desc{font-size:.68rem;line-height:1.25;margin-top:.28rem;color:rgba(255,255,255,.9)!important}
.priority-summary-card.p1{background:linear-gradient(135deg,#c6283d,#ef4057)!important;border-color:#ef4057}.priority-summary-card.p1 .psc-dot{background:#fff!important}
.priority-summary-card.p2{background:linear-gradient(135deg,#d96508,#f79009)!important;border-color:#f79009}.priority-summary-card.p2 .psc-dot{background:#fff!important}
.priority-summary-card.p3{background:linear-gradient(135deg,#c48a08,#eab52b)!important;border-color:#eab52b}.priority-summary-card.p3 .psc-dot{background:#fff!important}
.priority-summary-card.p4{background:linear-gradient(135deg,#078b55,#12b76a)!important;border-color:#12b76a}.priority-summary-card.p4 .psc-dot{background:#fff!important}
.priority-summary-card{margin-top:.35rem}
.priority-summary-card + .priority-summary-card{margin-left:.05rem}
.dashboard-panel-body .priority-summary-card + .priority-summary-card{}
.dq-card{background:#f8fafc!important}.dq-card.dq-high-bg{background:#f0fdf4!important;border-color:#bbf7d0!important}.dq-card.dq-medium-bg{background:#fff7ed!important;border-color:#fed7aa!important}.dq-card.dq-low-bg{background:#fff5f5!important;border-color:#fecaca!important}
.area-card{background:#f8fafc!important}
.dashboard-action-kpi,.dashboard-action-kpi *,.dashboard-action-kpi .opp-card-title,.dashboard-action-kpi .opp-card-value,.dashboard-action-kpi .opp-card-small{color:#fff!important}


/* =========================================================================
   Equipment Health v22 — premium engineering workspace
   ========================================================================= */
.eh22-header{display:flex;align-items:center;justify-content:space-between;gap:1rem;margin:.05rem 0 .85rem}
.eh22-title{font-size:1.72rem;font-weight:850;color:#14213d;line-height:1.12}
.eh22-subtitle{font-size:.78rem;color:#667085;margin-top:.3rem;line-height:1.4}
.eh22-live{font-size:.62rem;font-weight:850;color:#087443;background:#ecfdf3;border:1px solid #bbf7d0;border-radius:999px;padding:.36rem .58rem;white-space:nowrap}
.eh22-hero{
    background:linear-gradient(135deg,#102b55,#244f82);color:#fff;border-radius:12px;
    padding:1rem 1.1rem;display:flex;align-items:center;justify-content:space-between;
    gap:1rem;box-shadow:0 5px 14px rgba(16,24,40,.13);margin:.55rem 0 .75rem;
}
.eh22-hero-left{display:flex;align-items:center;gap:.85rem;min-width:0}
.eh22-eq-icon{width:50px;height:50px;border-radius:12px;background:rgba(255,255,255,.12);display:flex;align-items:center;justify-content:center;font-size:1.7rem}
.eh22-code{font-size:1.28rem;font-weight:900;line-height:1.05}
.eh22-name{font-size:.75rem;color:#d7e5f5;margin-top:.22rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:600px}
.eh22-tags{display:flex;gap:.35rem;flex-wrap:wrap;margin-top:.38rem}
.eh22-tags span{font-size:.56rem;font-weight:750;color:#e7f0fb;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.08);border-radius:999px;padding:.2rem .4rem}
.eh22-hero-right{text-align:right;white-space:nowrap}
.eh22-status{display:inline-block;padding:.42rem .7rem;border-radius:999px;font-size:.72rem;font-weight:900;border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.12);color:#fff}
.eh22-status.healthy{background:rgba(18,183,106,.20)}.eh22-status.data-stale,.eh22-status.no-data{background:rgba(247,144,9,.24)}.eh22-status.data-review{background:rgba(245,184,46,.24)}.eh22-status.deteriorating{background:rgba(245,184,46,.20)}.eh22-status.attention{background:rgba(247,144,9,.22)}.eh22-status.critical{background:rgba(240,68,56,.24)}
.eh22-last{font-size:.61rem;color:#d7e5f5;margin-top:.3rem}
.eh22-kpi{border:1px solid #dfe5ee;border-radius:9px;background:#f8fafc;min-height:100px;padding:.72rem .78rem;box-sizing:border-box;box-shadow:0 2px 6px rgba(16,24,40,.045)}
.eh22-kpi-label{font-size:.61rem;font-weight:850;color:#667085;letter-spacing:.025em}
.eh22-kpi-value{font-size:1.36rem;font-weight:900;color:#172b4d;line-height:1.08;margin-top:.3rem;white-space:nowrap}
.eh22-kpi-value small{font-size:.68rem;font-weight:750;color:#98a2b3;margin-left:.2rem}
.eh22-kpi-small{font-size:.61rem;color:#98a2b3;margin-top:.32rem;line-height:1.25}
.eh22-kpi.blue{background:#eef6ff;border-color:#bfdbfe}.eh22-kpi.blue .eh22-kpi-value{color:#175cd3}
.eh22-kpi.healthy,.eh22-kpi.green{background:#f0fdf4;border-color:#bbf7d0}.eh22-kpi.healthy .eh22-kpi-value,.eh22-kpi.green .eh22-kpi-value{color:#07895a}
.eh22-kpi.orange,.eh22-kpi.attention{background:#fff7ed;border-color:#fed7aa}.eh22-kpi.orange .eh22-kpi-value,.eh22-kpi.attention .eh22-kpi-value{color:#c2410c}
.eh22-kpi.deteriorating,.eh22-kpi.p3{background:#fffbeb;border-color:#fde68a}.eh22-kpi.deteriorating .eh22-kpi-value,.eh22-kpi.p3 .eh22-kpi-value{color:#a16207}
.eh22-kpi.critical,.eh22-kpi.p1{background:#fff1f2;border-color:#fecdd3}.eh22-kpi.critical .eh22-kpi-value,.eh22-kpi.p1 .eh22-kpi-value{color:#c81e1e}
.eh22-kpi.p2{background:#fff7ed;border-color:#fed7aa}.eh22-kpi.p2 .eh22-kpi-value{color:#c2410c}
.eh22-kpi.p4{background:#f0fdf4;border-color:#bbf7d0}.eh22-kpi.p4 .eh22-kpi-value{color:#07895a}
.eh22-decision{display:flex;align-items:center;gap:.75rem;background:#fff7ed;border:1px solid #fed7aa;border-left:5px solid #f79009;border-radius:9px;padding:.68rem .78rem;margin:.75rem 0}
.eh22-decision.healthy{background:#f0fdf4;border-color:#bbf7d0;border-left-color:#12b76a}
.eh22-decision-icon{font-size:1.25rem}
.eh22-decision-title{font-size:.58rem;font-weight:900;color:#9a5b00;letter-spacing:.03em}
.eh22-decision.healthy .eh22-decision-title{color:#07895a}
.eh22-decision-text{font-size:.7rem;color:#475467;line-height:1.35;margin-top:.12rem}
.eh22-panel{background:#fff;border:1px solid #dfe5ee;border-radius:10px;padding:.76rem .8rem;box-sizing:border-box;height:100%;box-shadow:0 2px 5px rgba(16,24,40,.035)}
.eh22-panel-head{font-size:.76rem;font-weight:900;color:#25364d;padding-bottom:.45rem;border-bottom:1px solid #edf0f4}
.eh22-panel-sub{font-size:.61rem;color:#98a2b3;margin:.28rem 0 .5rem}
.eh22-dist-row{display:grid;grid-template-columns:1fr auto 35px;align-items:center;gap:.35rem;padding:.43rem .38rem;border-bottom:1px solid #f0f2f5;font-size:.63rem;color:#475467}
.eh22-dist-row:last-child{border-bottom:0}.eh22-dist-row strong{font-size:.9rem;color:#172b4d}.eh22-dist-row small{text-align:right;color:#98a2b3}
.eh22-mini-dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:.3rem}.eh22-mini-dot.normal{background:#12b76a}
.eh22-mini-dot.unverified{background:#94a3b8}
.eh22-mini-dot.deteriorating{background:#f5b82e}.eh22-mini-dot.attention{background:#f79009}.eh22-mini-dot.critical{background:#f04438}
.eh22-abnormal-row{display:flex;justify-content:space-between;align-items:center;gap:.6rem;padding:.48rem .42rem;border-bottom:1px solid #edf0f4}
.eh22-abnormal-row:last-child{border-bottom:0}.eh22-abnormal-main{display:flex;align-items:center;gap:.35rem;min-width:0}.eh22-abnormal-main>b{font-size:.65rem;color:#344054;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.eh22-tag{font-size:.55rem;color:#98a2b3;white-space:nowrap}
.eh22-status-pill{font-size:.5rem;font-weight:900;border-radius:999px;padding:.18rem .32rem;white-space:nowrap}.eh22-status-pill.critical{color:#c81e1e;background:#fff1f2}.eh22-status-pill.attention{color:#c2410c;background:#fff7ed}.eh22-status-pill.deteriorating{color:#a16207;background:#fffbeb}
.eh22-abnormal-value{text-align:right;white-space:nowrap}.eh22-abnormal-value b{font-size:.68rem;color:#c2410c}.eh22-abnormal-value small{display:block;font-size:.51rem;color:#98a2b3;margin-top:.08rem}
.eh22-read-card{background:#f8fafc;border:1px solid #e3e8ef;border-radius:8px;padding:.65rem}.eh22-read-title{font-size:.78rem;font-weight:900;color:#172b4d}.eh22-read-text{font-size:.63rem;color:#667085;line-height:1.4;margin-top:.3rem}.eh22-read-rule{height:1px;background:#e6e9ef;margin:.5rem 0}.eh22-read-small{font-size:.57rem;color:#98a2b3}.eh22-read-small b{color:#475467}
.eh22-no-issue{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;color:#07895a;font-size:.65rem;font-weight:700;padding:.65rem;line-height:1.35}
.eh22-evidence-chip{height:100%;min-height:63px;background:#f8fafc;border:1px solid #dfe5ee;border-radius:8px;padding:.55rem .65rem;box-sizing:border-box}
.eh22-evidence-chip span{display:block;font-size:.52rem;font-weight:850;color:#98a2b3}.eh22-evidence-chip b{display:block;font-size:.72rem;color:#344054;margin-top:.12rem}.eh22-evidence-chip small{font-size:.55rem;color:#667085}
.eh22-evidence-row{display:flex;justify-content:space-between;gap:.4rem;padding:.43rem 0;border-bottom:1px solid #edf0f4;font-size:.61rem}.eh22-evidence-row:last-child{border-bottom:0}.eh22-evidence-row span{color:#667085}.eh22-evidence-row b{text-align:right;color:#172b4d}
.eh22-recommendation{background:#eef6ff;border:1px solid #bfdbfe;border-radius:10px;padding:.78rem .85rem;min-height:120px;box-sizing:border-box}.eh22-rec-head{font-size:.61rem;font-weight:900;color:#175cd3}.eh22-rec-title{font-size:.76rem;font-weight:800;color:#1e40af;line-height:1.4;margin-top:.35rem}.eh22-rec-note{font-size:.59rem;color:#667085;line-height:1.35;margin-top:.45rem}
.eh22-panel .stButton>button{min-height:34px!important;border-radius:7px!important;font-size:.62rem!important;font-weight:750!important}
.eh22-disclaimer{background:#f8fafc;border:1px solid #e3e8ef;border-radius:8px;padding:.55rem .7rem;margin-top:.7rem;color:#667085;font-size:.57rem;line-height:1.35}
.eh22-empty{background:#f8fafc;border:1px solid #dfe5ee;border-radius:12px;padding:1.5rem;text-align:center;margin-top:.8rem}.eh22-empty-icon{font-size:2rem;color:#98a2b3}.eh22-empty b{display:block;color:#344054;font-size:.82rem;margin-top:.3rem}.eh22-empty span{display:block;color:#98a2b3;font-size:.64rem;margin-top:.25rem}
@media(max-width:900px){.eh22-header{align-items:flex-start;flex-direction:column}.eh22-hero{align-items:flex-start;flex-direction:column}.eh22-hero-right{text-align:left}.eh22-name{max-width:75vw}}

/* ===== Equipment Health v29 — Engineering Diagnosis ===== */
.eh29-section-title{
    font-size:.78rem;font-weight:900;color:#25364d;margin:.95rem 0 .08rem
}
.eh29-section-sub{
    font-size:.61rem;color:#98a2b3;margin-bottom:.55rem
}
.eh29-gate{
    border:1px solid #fed7aa;border-left:4px solid #f79009;background:#fff7ed;
    border-radius:9px;padding:.58rem .7rem;font-size:.57rem;color:#8a4b08;
    line-height:1.45;margin-bottom:.6rem
}
.eh29-empty{
    border:1px dashed #d0d5dd;border-radius:9px;background:#fafbfc;
    padding:.75rem;font-size:.59rem;color:#667085;margin-bottom:.6rem
}
.eh29-dx-card{
    min-height:175px;border:1px solid #dfe5ee;border-top:3px solid #2563eb;
    border-radius:10px;background:#fff;padding:.7rem;
    box-shadow:0 2px 7px rgba(16,24,40,.035)
}
.eh29-dx-rank{
    font-size:.48rem;font-weight:900;color:#667085;letter-spacing:.025em
}
.eh29-dx-title{
    font-size:.76rem;font-weight:900;color:#172b4d;margin:.25rem 0 .35rem
}
.eh29-dx-card ul{margin:.1rem 0 .45rem;padding-left:1rem}
.eh29-dx-card li{
    font-size:.55rem;color:#667085;line-height:1.35;margin:.15rem 0
}
.eh29-dx-caution{
    font-size:.51rem;color:#9a5b00;background:#fffaf5;border-radius:6px;
    padding:.4rem;line-height:1.35
}
.eh29-panel{
    border:1px solid #dfe5ee;border-radius:10px;background:#fff;
    padding:.7rem;min-height:260px
}
.eh29-panel-title{
    font-size:.66rem;font-weight:900;color:#25364d
}
.eh29-panel-sub{
    font-size:.52rem;color:#98a2b3;margin:.15rem 0 .5rem
}
.eh29-check{
    display:flex;gap:.45rem;padding:.42rem 0;border-top:1px solid #eef1f5;
    font-size:.57rem;color:#475467;line-height:1.4
}
.eh29-check span{font-size:.72rem;color:#2563eb}
.eh29-caution{
    margin-top:.55rem;border-top:1px solid #eef1f5;padding-top:.5rem;
    font-size:.53rem;color:#8a4b08;line-height:1.4
}
.eh29-correlation{
    border:1px solid #dfe5ee;border-radius:10px;background:#fff;
    padding:.7rem;margin-top:.6rem
}
.eh29-correlation table{width:100%;border-collapse:collapse;font-size:.55rem}
.eh29-correlation th{
    text-align:left;color:#667085;background:#f8fafc;padding:.38rem;
    border-bottom:1px solid #e4e7ec
}
.eh29-correlation td{
    padding:.38rem;border-bottom:1px solid #eef1f5;color:#475467
}
@media(max-width:1000px){
    .eh29-panel{min-height:auto}
}

/* ===== Equipment Health v28 — Maintenance Context ===== */
.eh28-section-title{
    font-size:.78rem;font-weight:900;color:#25364d;margin:.95rem 0 .08rem;
    letter-spacing:.01em
}
.eh28-section-sub{
    font-size:.61rem;color:#98a2b3;margin-bottom:.5rem
}
.eh28-maint-grid{
    display:grid;grid-template-columns:1.15fr 1fr 1fr 1.35fr;
    gap:.55rem;margin-bottom:.45rem
}
.eh28-maint-note{
    border:1px solid #dfe5ee;border-left:4px solid #98a2b3;
    background:#f8fafc;border-radius:8px;padding:.5rem .65rem;
    color:#667085;font-size:.57rem;line-height:1.4;margin-bottom:.5rem
}
.eh28-maint-note.active{
    border-color:#fed7aa;border-left-color:#f79009;
    background:#fff7ed;color:#9a5b00
}
.eh28-decision{
    border-radius:9px;padding:.62rem .7rem;margin:.45rem 0 .7rem;
    border:1px solid #dfe5ee;background:#fff
}
.eh28-decision.blocked{border-left:4px solid #f79009;background:#fffaf5}
.eh28-decision.review{border-left:4px solid #f59e0b;background:#fffaf5}
.eh28-decision.active{border-left:4px solid #2563eb;background:#f5f9ff}
.eh28-decision.normal{border-left:4px solid #12b76a;background:#f6fffa}
.eh28-decision-title{
    font-size:.61rem;font-weight:900;color:#25364d;letter-spacing:.01em
}
.eh28-decision-text{
    font-size:.57rem;color:#667085;margin-top:.18rem;line-height:1.4
}
@media(max-width:1000px){
    .eh28-maint-grid{grid-template-columns:repeat(2,1fr)}
}

/* ===== Equipment Health v27 refinements ===== */
.eh26-context-card{min-width:0}
.eh26-context-value{font-size:.69rem}
.eh26-context-sub{font-size:.49rem}
.eh25-matrix-head,.eh25-matrix-row{
    grid-template-columns:1.65fr .75fr .9fr 1fr .85fr 1.2fr .5fr;
}
.eh25-focus{margin-top:.55rem}

/* ===== Equipment Health v26 — Operating Context ===== */
.eh26-section-title{
    font-size:.78rem;font-weight:900;color:#25364d;margin:.95rem 0 .08rem;
    letter-spacing:.01em
}
.eh26-section-sub{
    font-size:.61rem;color:#98a2b3;margin-bottom:.5rem
}
.eh26-context-grid{
    display:grid;grid-template-columns:1.15fr 1fr 1fr 1fr 1fr;
    gap:.55rem;margin-bottom:.45rem
}
.eh26-context-card{
    min-height:78px;border:1px solid #e1e7ef;border-radius:10px;
    background:#fff;padding:.62rem .65rem;
    box-shadow:0 2px 6px rgba(16,24,40,.03)
}
.eh26-context-card.running{border-top:3px solid #12b76a;background:#f6fffa}
.eh26-context-card.stopped{border-top:3px solid #f79009;background:#fffaf5}
.eh26-context-card.neutral{border-top:3px solid #cbd5e1}
.eh26-context-label{
    font-size:.51rem;font-weight:900;color:#667085;letter-spacing:.025em
}
.eh26-context-value{
    margin-top:.22rem;font-size:.76rem;font-weight:900;color:#172b4d;
    line-height:1.2
}
.eh26-context-sub{
    margin-top:.18rem;font-size:.51rem;color:#98a2b3;
    line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis
}
.eh26-context-note{
    border:1px solid #e1e7ef;background:#f8fafc;border-radius:8px;
    padding:.48rem .62rem;margin-bottom:.65rem;
    color:#667085;font-size:.57rem;line-height:1.35
}
@media(max-width:1000px){
    .eh26-context-grid{grid-template-columns:repeat(2,1fr)}
}

/* ===== Equipment Health v25 — Parameter Health Matrix ===== */
.eh25-section-title{
    font-size:.78rem;font-weight:900;color:#25364d;margin:.95rem 0 .08rem;
    letter-spacing:.01em
}
.eh25-section-sub{
    font-size:.61rem;color:#98a2b3;margin-bottom:.5rem
}
.eh25-matrix{
    border:1px solid #dfe5ee;border-radius:10px;background:#fff;
    overflow:hidden;box-shadow:0 2px 6px rgba(16,24,40,.035)
}
.eh25-matrix-head,.eh25-matrix-row{
    display:grid;
    grid-template-columns:1.55fr .78fr .86fr 1fr .88fr 1.25fr .5fr;
    align-items:center;gap:.5rem;padding:.58rem .65rem
}
.eh25-matrix-head{
    background:#f8fafc;border-bottom:1px solid #e6e9ef;
    font-size:.53rem;font-weight:900;color:#667085;letter-spacing:.025em
}
.eh25-matrix-row{
    min-height:48px;border-bottom:1px solid #edf0f4;
    font-size:.62rem;color:#344054
}
.eh25-matrix-row:last-child{border-bottom:0}
.eh25-param b{display:block;font-size:.64rem;color:#25364d}
.eh25-param small,.eh25-current small,.eh25-direction small,.eh25-deviation small{
    display:block;font-size:.52rem;color:#98a2b3;margin-top:.12rem
}
.eh25-current b{font-size:.66rem;color:#172b4d}
.eh25-direction b{font-size:.58rem;color:#475467}
.eh25-deviation b{font-size:.62rem;color:#172b4d}
.eh25-confidence b{font-size:.56rem;color:#667085}
.eh25-pill,.eh25-quality{
    display:inline-block;border-radius:999px;padding:.2rem .4rem;
    font-size:.49rem;font-weight:900;white-space:nowrap
}
.eh25-pill.normal{background:#ecfdf3;color:#07895a}
.eh25-pill.deteriorating{background:#fffbeb;color:#a16207}
.eh25-pill.attention{background:#fff7ed;color:#c2410c}
.eh25-pill.critical{background:#fff1f2;color:#c81e1e}
.eh25-pill.unverified{background:#f2f4f7;color:#667085}
.eh25-quality.valid{background:#ecfdf3;color:#07895a}
.eh25-quality.warn{background:#fffbeb;color:#a16207}
.eh25-quality.flatline{background:#fff7ed;color:#9a5b00}
.eh25-quality.bad{background:#fff1f2;color:#c81e1e}
.eh25-focus{
    margin:.5rem 0 .75rem;padding:.55rem .68rem;border-radius:8px;
    border:1px solid #fed7aa;border-left:4px solid #f79009;
    background:#fff7ed;color:#9a5b00;font-size:.61rem;line-height:1.35
}
.eh25-focus.neutral{
    background:#f8fafc;border-color:#dfe5ee;border-left-color:#98a2b3;color:#667085
}
.eh25-empty{padding:.8rem;color:#98a2b3;font-size:.62rem;text-align:center}
@media(max-width:900px){
    .eh25-matrix{overflow-x:auto}
    .eh25-matrix-head,.eh25-matrix-row{min-width:760px}
}

/* ===== Equipment Health v7 ===== */
.health-selector-grid{display:grid;grid-template-columns:1fr 2fr;gap:.7rem;margin:.65rem 0 1rem}
.health-equipment-banner{background:linear-gradient(135deg,#172b4d,#274c77);color:#fff;border-radius:10px;padding:1rem 1.1rem;display:flex;align-items:center;justify-content:space-between;gap:1rem;box-shadow:0 4px 12px rgba(16,24,40,.12);margin:.35rem 0 .8rem}
.health-equipment-banner .heb-code{font-size:1.25rem;font-weight:850;line-height:1.1}.health-equipment-banner .heb-name{font-size:.76rem;color:#d7e5f5;margin-top:.28rem}.health-equipment-banner .heb-badge{padding:.42rem .72rem;border-radius:999px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.25);font-size:.72rem;font-weight:850;white-space:nowrap;color:#fff}
.health-kpi{border-radius:9px;padding:.78rem .85rem;min-height:105px;box-sizing:border-box;border:1px solid #dfe5ee;background:#f8fafc;box-shadow:0 2px 6px rgba(16,24,40,.05)}
.health-kpi .hk-label{font-size:.69rem;color:#667085;font-weight:750}.health-kpi .hk-value{font-size:1.38rem;font-weight:850;color:#1d2939;line-height:1.15;margin-top:.3rem}.health-kpi .hk-small{font-size:.67rem;color:#98a2b3;margin-top:.35rem;line-height:1.25}
.health-kpi.overall{background:#fff7ed;border-color:#fed7aa}.health-kpi.overall.healthy{background:#f0fdf4;border-color:#bbf7d0}.health-kpi.overall.attention{background:#fff7ed;border-color:#fed7aa}.health-kpi.overall.critical{background:#fff1f2;border-color:#fecdd3}.health-kpi.overall.deteriorating{background:#fffbeb;border-color:#fde68a}
.health-dist-card{border-radius:9px;padding:.72rem .8rem;min-height:92px;box-sizing:border-box;border:1px solid #dfe5ee;background:#fff}.health-dist-card .hd-label{font-size:.7rem;font-weight:800}.health-dist-card .hd-value{font-size:1.35rem;font-weight:850;color:#1d2939;margin-top:.28rem}.health-dist-card .hd-pct{font-size:.66rem;color:#98a2b3;margin-top:.15rem}
.hd-normal{background:#f0fdf4;border-color:#bbf7d0}.hd-normal .hd-label{color:#07895a}.hd-deteriorating{background:#fffbeb;border-color:#fde68a}.hd-deteriorating .hd-label{color:#a16207}.hd-attention{background:#fff7ed;border-color:#fed7aa}.hd-attention .hd-label{color:#c2410c}.hd-critical{background:#fff1f2;border-color:#fecdd3}.hd-critical .hd-label{color:#c81e1e}
.health-findings{background:#f8fafc;border:1px solid #dfe5ee;border-radius:9px;padding:.8rem}.health-finding-title{font-weight:800;color:#25364d;font-size:.82rem}.health-finding-meta{font-size:.72rem;color:#667085;margin-top:.25rem}.health-recommendation{background:#eef6ff;border:1px solid #bfdbfe;border-radius:8px;padding:.72rem .8rem;color:#1e40af;font-size:.76rem;line-height:1.4;margin-top:.65rem}
@media(max-width:900px){.health-selector-grid{grid-template-columns:1fr}}


/* ===== Equipment Health v8 — visual layout matching approved concept ===== */
.health-v8-banner{
    background:linear-gradient(135deg,#102b55 0%,#244f82 100%);
    color:#fff;border-radius:10px;padding:.85rem 1rem;
    display:flex;align-items:center;justify-content:space-between;gap:1rem;
    box-shadow:0 4px 12px rgba(16,24,40,.12);margin:.55rem 0 .65rem;
}
.health-v8-banner-left{display:flex;align-items:center;gap:.85rem;min-width:0}
.health-v8-eq-icon{font-size:2.35rem;line-height:1}
.health-v8-code{font-size:1.28rem;font-weight:850;line-height:1.05}
.health-v8-name{font-size:.75rem;color:#d7e5f5;margin-top:.22rem}
.health-v8-area{display:inline-block;margin-top:.28rem;padding:.18rem .48rem;border-radius:999px;background:rgba(255,255,255,.13);font-size:.64rem;color:#e7f0fb}
.health-v8-banner-right{text-align:right;white-space:nowrap}
.health-v8-badge{display:inline-block;padding:.42rem .7rem;border-radius:999px;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);font-size:.72rem;font-weight:850;color:#fff}
.health-v8-last{font-size:.64rem;color:#d7e5f5;margin-top:.3rem}
.health-v8-kpi{
    border:1px solid #dce3ec;border-radius:9px;background:#f8fafc;
    min-height:96px;padding:.72rem .78rem;box-sizing:border-box;
    box-shadow:0 2px 6px rgba(16,24,40,.045)
}
.health-v8-kpi .label{font-size:.66rem;color:#667085;font-weight:800;text-transform:uppercase;letter-spacing:.02em}
.health-v8-kpi .value{font-size:1.32rem;font-weight:850;color:#172b4d;line-height:1.12;margin-top:.28rem}
.health-v8-kpi .small{font-size:.64rem;color:#98a2b3;margin-top:.32rem;line-height:1.25}
.health-v8-kpi.condition-attention{background:#fff7ed;border-color:#fed7aa}
.health-v8-kpi.condition-deteriorating{background:#fffbeb;border-color:#fde68a}
.health-v8-kpi.condition-critical{background:#fff1f2;border-color:#fecdd3}
.health-v8-kpi.condition-healthy{background:#f0fdf4;border-color:#bbf7d0}
.health-v8-kpi.priority-p1{background:#fff1f2;border-color:#fecdd3}
.health-v8-kpi.priority-p2{background:#fff7ed;border-color:#fed7aa}
.health-v8-kpi.priority-p3{background:#fffbeb;border-color:#fde68a}
.health-v8-kpi.priority-p4{background:#f0fdf4;border-color:#bbf7d0}
.health-v8-why{
    background:#fffbeb;border:1px solid #fed7aa;border-radius:9px;
    padding:.7rem .82rem;color:#7a4b00;font-size:.73rem;line-height:1.4;margin:.48rem 0 .65rem
}
.health-v8-why-title{font-weight:850;color:#9a5b00;margin-bottom:.16rem}
.health-v8-panel{
    background:#fff;border:1px solid #dfe5ee;border-radius:9px;
    padding:.72rem .76rem;box-sizing:border-box;height:100%
}
.health-v8-panel-head{
    font-size:.76rem;font-weight:850;color:#25364d;
    padding-bottom:.5rem;border-bottom:1px solid #edf0f4;margin-bottom:.55rem
}
.health-v8-dist-grid{display:grid;grid-template-columns:1fr 1fr;gap:.42rem}
.health-v8-dist{
    border-radius:8px;padding:.55rem .62rem;min-height:82px;box-sizing:border-box;
    border:1px solid #e3e8ef
}
.health-v8-dist .dlabel{font-size:.62rem;font-weight:850}
.health-v8-dist .dvalue{font-size:1.18rem;font-weight:850;color:#172b4d;margin-top:.22rem}
.health-v8-dist .dpct{font-size:.59rem;color:#98a2b3;margin-top:.1rem}
.health-v8-dist.normal{background:#f0fdf4;border-color:#bbf7d0}.health-v8-dist.normal .dlabel{color:#07895a}
.health-v8-dist.deteriorating{background:#fffbeb;border-color:#fde68a}.health-v8-dist.deteriorating .dlabel{color:#a16207}
.health-v8-dist.attention{background:#fff7ed;border-color:#fed7aa}.health-v8-dist.attention .dlabel{color:#c2410c}
.health-v8-dist.critical{background:#fff1f2;border-color:#fecdd3}.health-v8-dist.critical .dlabel{color:#c81e1e}
.health-v8-table-wrap{overflow-x:auto;border:1px solid #e5e9ef;border-radius:7px}
.health-v8-table{width:100%;border-collapse:collapse;font-size:.61rem;color:#344054}
.health-v8-table th{background:#f4f7fa;color:#667085;font-weight:800;text-align:left;padding:.42rem .38rem;white-space:nowrap;border-bottom:1px solid #dfe5ee}
.health-v8-table td{padding:.45rem .38rem;border-bottom:1px solid #edf0f4;white-space:nowrap}
.health-v8-table tr:last-child td{border-bottom:0}
.health-v8-status{font-weight:850}
.health-v8-status.deteriorating{color:#a16207}.health-v8-status.attention{color:#c2410c}.health-v8-status.critical{color:#c81e1e}
.health-v8-finding{
    background:#f8fafc;border:1px solid #dfe5ee;border-radius:8px;padding:.65rem .7rem
}
.health-v8-finding-title{font-size:.74rem;font-weight:850;color:#25364d}
.health-v8-pills{display:flex;gap:.32rem;flex-wrap:wrap;margin-top:.45rem}
.health-v8-pill{font-size:.59rem;font-weight:750;color:#475467;background:#fff;border:1px solid #dfe5ee;border-radius:999px;padding:.22rem .42rem}
.health-v8-reco{
    background:#eef6ff;border:1px solid #bfdbfe;border-radius:7px;
    padding:.58rem .65rem;color:#1e40af;font-size:.65rem;line-height:1.35;margin-top:.52rem
}
.health-v8-trend-panel{
    background:#fff;border:1px solid #dfe5ee;border-radius:9px;padding:.72rem .76rem;margin-top:.65rem
}
.health-v8-trend-head{font-size:.76rem;font-weight:850;color:#25364d;margin-bottom:.2rem}
.health-v8-trend-sub{font-size:.62rem;color:#98a2b3;margin-bottom:.35rem}
.health-v8-trend-metric{
    padding:.5rem .55rem;background:#f8fafc;border:1px solid #e5e9ef;border-radius:7px
}
.health-v8-trend-metric .tm-label{font-size:.58rem;color:#667085;font-weight:750}
.health-v8-trend-metric .tm-value{font-size:1.02rem;color:#172b4d;font-weight:850;margin-top:.18rem}
.health-v8-trend-metric .tm-note{font-size:.57rem;color:#98a2b3;margin-top:.12rem}
.health-v8-actions{margin-top:.55rem}
.health-v8-note{
    background:#eff8ff;border:1px solid #b2ddff;border-radius:8px;
    padding:.58rem .7rem;color:#175cd3;font-size:.63rem;line-height:1.35;margin-top:.6rem
}
@media(max-width:1000px){
    .health-v8-banner{align-items:flex-start}
    .health-v8-banner-right{text-align:left}
    .health-v8-dist-grid{grid-template-columns:1fr 1fr}
}
@media(max-width:700px){
    .health-v8-banner{flex-direction:column}
    .health-v8-banner-right{text-align:left}
}


/* ===== Dashboard v16 — whole-card navigation ===== */
.v16-click{
    display:block;text-decoration:none!important;color:inherit!important;
    cursor:pointer;position:relative;
}
.v16-click:hover{text-decoration:none!important}
.v16-click .v15-kpi,.v16-click .v15-condition,.v16-click .v15-action-main,
.v16-click .v15-priority,.v16-click .v15-dq{
    transition:transform .14s ease,box-shadow .14s ease,filter .14s ease;
}
.v16-click:hover .v15-kpi,.v16-click:hover .v15-condition,
.v16-click:hover .v15-action-main,.v16-click:hover .v15-priority,.v16-click:hover .v15-dq{
    transform:translateY(-2px);
    box-shadow:0 7px 18px rgba(16,24,40,.16);
    filter:saturate(1.04);
}
.v16-arrow{
    position:absolute;right:.7rem;bottom:.55rem;font-size:1.05rem;font-weight:900;
    color:rgba(255,255,255,.95);pointer-events:none;
}
.v16-condition-arrow{color:#667085}
.v16-mini-link{
    display:block;text-decoration:none!important;color:inherit!important;cursor:pointer;
}
.v16-panel-link{
    display:block;text-decoration:none!important;color:inherit!important;cursor:pointer;
}
.v16-panel-link:hover{color:inherit!important}
.v16-linkbar{
    margin-top:.55rem;border:1px solid #d9e0e8;background:#fff;border-radius:7px;
    min-height:36px;display:flex;align-items:center;justify-content:center;gap:.35rem;
    color:#344054;font-size:.68rem;font-weight:750;box-sizing:border-box;
    transition:transform .14s ease,box-shadow .14s ease,border-color .14s ease;
}
.v16-linkbar b{font-size:1rem;color:#175cd3}
.v16-panel-link:hover .v16-linkbar{transform:translateY(-1px);box-shadow:0 4px 10px rgba(16,24,40,.08);border-color:#8db7ef}


/* ===== Dashboard v15 — bright, solid-color executive UI ===== */

/* V16 spacing polish: each dashboard block is visually independent. */
.v15-row-gap{height:1rem}
[data-testid="stHorizontalBlock"]{column-gap:1rem!important}
.v15-kpi{margin-bottom:0!important}
.v15-panel-head{border-radius:8px 8px 0 0}
.v15-condition{box-shadow:0 1px 3px rgba(16,24,40,.05)}
.v15-mini{box-shadow:0 1px 3px rgba(16,24,40,.04)}
.v15-priority{box-shadow:0 2px 5px rgba(16,24,40,.10)}
.v15-dq{box-shadow:0 1px 3px rgba(16,24,40,.04)}
.v15-table{background:#fff;border:1px solid #e4e7ec;border-radius:7px;overflow:hidden}
.v15-header{padding:.15rem 0 .7rem}.v15-title{font-size:1.72rem;font-weight:850;color:#14213d;line-height:1.12}.v15-live{display:inline-block;margin-left:.35rem;padding:.22rem .48rem;border-radius:999px;background:#e7f8ee;color:#07895a;font-size:.62rem;font-weight:850;vertical-align:middle}.v15-subtitle{font-size:.78rem;color:#667085;margin-top:.32rem;line-height:1.4}.v15-period{border:1px solid #dce3ec;background:#f8fafc;border-radius:9px;padding:.55rem .7rem;min-height:68px;box-sizing:border-box}.v15-period-label{font-size:.59rem;font-weight:800;color:#667085}.v15-period-value{font-size:.79rem;font-weight:800;color:#172b4d;margin-top:.18rem}.v15-period-small{font-size:.59rem;color:#98a2b3;margin-top:.1rem}.v15-kpi{border-radius:8px;min-height:104px;padding:.82rem .85rem;box-sizing:border-box;color:#fff;box-shadow:0 3px 8px rgba(16,24,40,.13);margin-bottom:.68rem}.v15-kpi-top{font-size:.67rem;font-weight:800;display:flex;align-items:center;gap:.35rem;line-height:1.2}.v15-kpi-value{font-size:1.72rem;font-weight:900;line-height:1.05;margin-top:.38rem}.v15-kpi-small{font-size:.61rem;font-weight:600;margin-top:.35rem;opacity:.95}.v15-panel-head{height:38px;margin:-.65rem -.7rem .58rem;padding:0 .7rem;display:flex;align-items:center;background:#edf2f7;border-bottom:1px solid #dfe5ee;color:#25364d;font-size:.78rem;font-weight:850}.v15-panel-head span{font-size:.62rem;font-weight:600;color:#98a2b3;margin-left:.4rem}.v15-panel-sub{font-size:.68rem;color:#7b8798;margin-bottom:.55rem}.v15-stack{height:14px;display:flex;border-radius:5px;overflow:hidden;background:#eef1f5;border:1px solid #e1e6ec;margin:.25rem 0 .72rem}.v15-stack>div{height:100%}.v15-condition{background:#f8fafc;border:1px solid #e1e6ee;border-radius:7px;padding:.58rem .62rem;min-height:92px;box-sizing:border-box}.v15-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:.3rem}.v15-condition-label{font-size:.59rem;font-weight:850;color:#475467;display:inline}.v15-condition-count{font-size:1.35rem;font-weight:900;color:#172b4d;line-height:1.1;margin-top:.32rem}.v15-condition-small{font-size:.58rem;color:#98a2b3;margin-top:.2rem;line-height:1.2}.v15-interpret{background:#eef6ff;border:1px solid #bfdbfe;border-radius:7px;padding:.55rem .62rem;margin-top:.55rem;color:#175cd3;font-size:.65rem;line-height:1.35}.v15-action-main{color:#fff;border-radius:8px;padding:.72rem .72rem;display:flex;align-items:center;gap:.65rem;min-height:86px;box-sizing:border-box}.v15-action-number{font-size:2.25rem;font-weight:900;line-height:1}.v15-action-title{font-size:.73rem;font-weight:850}.v15-action-small{font-size:.59rem;margin-top:.18rem;opacity:.92;line-height:1.25}.v15-action-icon{font-size:1.9rem;margin-left:auto;opacity:.95}.v15-mini{background:#f8fafc;border:1px solid #e2e8f0;border-radius:7px;padding:.5rem .48rem;min-height:70px;box-sizing:border-box;font-size:.54rem;color:#667085}.v15-mini strong{display:block;font-size:1.05rem;color:#172b4d;margin-top:.25rem}.v15-focus{background:#eef6ff;border:1px solid #bfdbfe;border-radius:7px;padding:.58rem .65rem;color:#175cd3;font-size:.68rem;line-height:1.35;margin-bottom:.55rem}.v15-priority{color:#fff;border-radius:8px;min-height:100px;padding:.62rem .65rem;box-sizing:border-box;box-shadow:0 2px 6px rgba(16,24,40,.12)}.v15-priority .vp-top{font-size:.65rem;font-weight:850}.v15-priority .vp-count{font-size:1.65rem;font-weight:900;line-height:1;margin-top:.28rem}.v15-priority .vp-desc{font-size:.58rem;margin-top:.3rem;line-height:1.15}.v15-dq{border:1px solid #dfe5ee;border-radius:7px;background:#f8fafc;min-height:76px;padding:.52rem .5rem;box-sizing:border-box}.v15-dq>div{font-size:.55rem;font-weight:800;color:#667085}.v15-dq strong{display:block;font-size:1.25rem;color:#172b4d;margin-top:.22rem}.v15-dq.high{background:#f0fdf4;border-color:#bbf7d0}.v15-dq.high strong{color:#07895a}.v15-dq.medium{background:#fff7ed;border-color:#fed7aa}.v15-dq.medium strong{color:#dc6803}.v15-dq.low{background:#fff5f5;border-color:#fecaca}.v15-dq.low strong{color:#d92d20}.v15-coverage{margin-top:.58rem}.v15-coverage>div:first-child{display:flex;justify-content:space-between;font-size:.61rem;color:#667085}.v15-coverage b{color:#07895a;font-size:.76rem}.v15-cover-track{height:8px;background:#e8edf3;border-radius:6px;overflow:hidden;margin:.3rem 0}.v15-cover-track>div{height:100%;background:#12b76a}.v15-coverage small{font-size:.55rem;color:#98a2b3}.v15-table{width:100%;border-collapse:collapse;font-size:.59rem;color:#344054}.v15-table th{background:#f4f7fa;color:#667085;text-align:left;font-weight:800;padding:.38rem .35rem;border-bottom:1px solid #dfe5ee}.v15-table td{padding:.4rem .35rem;border-bottom:1px solid #edf0f4;vertical-align:middle}.v15-table td span{color:#98a2b3;font-size:.53rem}.v15-status{font-weight:850}.v15-footer{display:flex;gap:1.1rem;flex-wrap:wrap;align-items:center;background:#f8fafc;border:1px solid #dfe5ee;border-radius:8px;padding:.58rem .7rem;margin-top:.7rem;font-size:.57rem;color:#667085}.v15-footer b{color:#172b4d}.v15-footer span:first-child{color:#07895a;font-weight:750}.v15-panel-head+div{box-sizing:border-box}@media(max-width:900px){.v15-title{font-size:1.35rem}.v15-period{margin-top:.2rem}.v15-action-main{min-height:78px}.v15-footer{gap:.6rem}}


/* =========================================================================
   Equipment Health v30 — VISUAL REFRESH
   Tujuan: hierarchy lebih besar, iconography lebih kuat, contextual colors,
   nuansa engineering condition/aging, tetap mempertahankan whitespace.
   Tidak mengubah kalkulasi, scoring, gate, atau data logic.
   ========================================================================= */

.eh22-header{margin-top:.25rem!important;margin-bottom:1.05rem!important}
.eh22-title{font-size:2.05rem!important;letter-spacing:-.025em!important}
.eh22-subtitle{font-size:.92rem!important;max-width:900px!important}
.eh22-live{font-size:.72rem!important;padding:.46rem .72rem!important}

/* Equipment hero — stronger engineering identity */
.eh22-hero{
    min-height:132px!important;
    border-radius:18px!important;
    padding:1.25rem 1.35rem!important;
    background:
      linear-gradient(135deg,#102b55 0%,#1e4f86 68%,#2b6ea6 100%)!important;
    box-shadow:0 10px 26px rgba(16,43,85,.16)!important;
    border:1px solid rgba(255,255,255,.08)!important;
    position:relative!important;
    overflow:hidden!important;
}
.eh22-hero:after{
    content:"";position:absolute;right:-70px;bottom:-85px;width:250px;height:250px;
    border:1px solid rgba(255,255,255,.10);border-radius:50%;
    box-shadow:0 0 0 26px rgba(255,255,255,.025),0 0 0 52px rgba(255,255,255,.018);
}
.eh22-eq-icon{
    width:68px!important;height:68px!important;border-radius:17px!important;
    font-size:2.05rem!important;background:rgba(255,255,255,.14)!important;
    border:1px solid rgba(255,255,255,.10)!important;
}
.eh22-code{font-size:1.55rem!important}
.eh22-name{font-size:.92rem!important}
.eh22-tags span{font-size:.65rem!important;padding:.27rem .52rem!important}
.eh22-status{font-size:.82rem!important;padding:.50rem .82rem!important}
.eh22-last{font-size:.70rem!important}

/* KPI strip — bigger, readable, unmistakable */
.eh22-kpi{
    min-height:128px!important;
    padding:1rem 1.05rem!important;
    border-radius:15px!important;
    box-shadow:0 5px 14px rgba(16,24,40,.055)!important;
    position:relative!important;
    overflow:hidden!important;
}
.eh22-kpi:before{
    content:"";position:absolute;left:0;top:0;bottom:0;width:5px;border-radius:15px 0 0 15px;
    background:#cbd5e1;
}
.eh22-kpi.blue:before{background:#2563eb}
.eh22-kpi.green:before,.eh22-kpi.healthy:before,.eh22-kpi.p4:before{background:#12b76a}
.eh22-kpi.orange:before,.eh22-kpi.attention:before,.eh22-kpi.p2:before{background:#f79009}
.eh22-kpi.deteriorating:before,.eh22-kpi.p3:before{background:#eab308}
.eh22-kpi.critical:before,.eh22-kpi.p1:before{background:#ef4444}
.eh22-kpi-label{font-size:.73rem!important}
.eh22-kpi-value{font-size:1.72rem!important;margin-top:.42rem!important}
.eh22-kpi-value small{font-size:.78rem!important}
.eh22-kpi-small{font-size:.72rem!important;line-height:1.35!important}

/* Decision / data quality blocks */
.eh22-decision{
    padding:.9rem 1rem!important;
    border-radius:13px!important;
    margin:.9rem 0!important;
}
.eh22-decision-icon{font-size:1.55rem!important}
.eh22-decision-title{font-size:.72rem!important}
.eh22-decision-text{font-size:.80rem!important}

/* Major section titles */
.eh25-section-title,.eh26-section-title,.eh28-section-title,.eh29-section-title{
    display:flex!important;align-items:center!important;gap:.68rem!important;
    font-size:1.08rem!important;font-weight:950!important;
    color:#172b4d!important;margin:1.35rem 0 .16rem!important;
    letter-spacing:.005em!important;
}
.eh25-section-sub,.eh26-section-sub,.eh28-section-sub,.eh29-section-sub{
    font-size:.76rem!important;color:#7a8699!important;
    line-height:1.45!important;margin-bottom:.72rem!important;
}
.eh-section-icon{
    width:36px;height:36px;min-width:36px;border-radius:11px;
    display:inline-flex;align-items:center;justify-content:center;
    font-size:1.12rem;box-shadow:0 4px 10px rgba(16,24,40,.08);
}
.eh-section-icon.blue{background:#e8f1ff;border:1px solid #c7dcff}
.eh-section-icon.teal{background:#e7f8f5;border:1px solid #b8ebe3}
.eh-section-icon.orange{background:#fff1df;border:1px solid #ffd7a3}
.eh-section-icon.purple{background:#f1eaff;border:1px solid #d9c8ff}

/* Parameter matrix — readable but still compact */
.eh25-matrix{
    border-radius:15px!important;
    box-shadow:0 7px 18px rgba(16,24,40,.055)!important;
    border-color:#d9e1eb!important;
}
.eh25-matrix-head,.eh25-matrix-row{
    padding:.78rem .85rem!important;
    gap:.7rem!important;
}
.eh25-matrix-head{
    font-size:.64rem!important;
    background:linear-gradient(180deg,#f7faff,#f1f5fa)!important;
}
.eh25-matrix-row{
    min-height:62px!important;
    font-size:.72rem!important;
}
.eh25-param b{font-size:.77rem!important}
.eh25-param small,.eh25-current small,.eh25-direction small,.eh25-deviation small{
    font-size:.62rem!important
}
.eh25-current b{font-size:.78rem!important}
.eh25-direction b{font-size:.68rem!important}
.eh25-deviation b{font-size:.73rem!important}
.eh25-confidence b{font-size:.65rem!important}
.eh25-pill,.eh25-quality{
    font-size:.61rem!important;padding:.28rem .52rem!important
}
.eh25-focus{
    margin:.7rem 0 1rem!important;padding:.72rem .82rem!important;
    border-radius:12px!important;font-size:.72rem!important
}

/* Operating Context — visual cards like a condition-monitoring cockpit */
.eh26-context-grid{
    gap:.78rem!important;margin-bottom:.6rem!important;
}
.eh26-context-card{
    min-height:126px!important;
    padding:.82rem .88rem!important;
    border-radius:15px!important;
    background:linear-gradient(180deg,#ffffff,#f8fbfd)!important;
    box-shadow:0 6px 16px rgba(16,24,40,.055)!important;
    border-color:#dce4ee!important;
    position:relative!important;
    overflow:hidden!important;
}
.eh26-context-card:after{
    content:"";position:absolute;right:-22px;top:-22px;width:82px;height:82px;
    border-radius:50%;border:1px solid rgba(37,99,235,.08);
}
.eh26-context-card.running{
    border-top:4px solid #12b76a!important;background:linear-gradient(180deg,#f9fffc,#effbf5)!important;
}
.eh26-context-card.stopped{
    border-top:4px solid #f79009!important;background:linear-gradient(180deg,#fffdf9,#fff6ea)!important;
}
.eh26-context-card.neutral{
    border-top:4px solid #64748b!important;background:linear-gradient(180deg,#fbfcfe,#f4f7fa)!important;
}
.eh26-context-top{display:flex;align-items:center;gap:.48rem}
.eh26-context-icon{
    width:30px;height:30px;min-width:30px;border-radius:9px;
    display:inline-flex;align-items:center;justify-content:center;
    background:#eaf1fb;border:1px solid #d7e3f3;font-size:.95rem;
}
.eh26-context-card.running .eh26-context-icon{background:#e5f8ee;border-color:#c3efd6}
.eh26-context-card.stopped .eh26-context-icon{background:#fff0dd;border-color:#ffd6a0}
.eh26-context-label{font-size:.61rem!important;letter-spacing:.035em!important}
.eh26-context-value{font-size:.98rem!important;margin-top:.48rem!important}
.eh26-context-sub{font-size:.63rem!important;margin-top:.28rem!important}
.eh26-context-note{
    padding:.68rem .8rem!important;border-radius:11px!important;
    font-size:.68rem!important;line-height:1.45!important
}

/* Maintenance Context — warm operational/aging color language */
.eh28-maint-grid{gap:.78rem!important;margin-bottom:.6rem!important}
.eh28-maint-grid .eh26-context-card:nth-child(1){border-top-color:#64748b!important}
.eh28-maint-grid .eh26-context-card:nth-child(2){border-top-color:#f79009!important}
.eh28-maint-grid .eh26-context-card:nth-child(3){border-top-color:#f97316!important}
.eh28-maint-grid .eh26-context-card:nth-child(4){border-top-color:#2563eb!important}
.eh28-maint-note{
    padding:.72rem .82rem!important;border-radius:12px!important;
    font-size:.68rem!important;line-height:1.45!important
}
.eh28-decision{
    padding:.82rem .9rem!important;border-radius:12px!important;margin:.62rem 0 .85rem!important;
}
.eh28-decision-title{font-size:.72rem!important}
.eh28-decision-text{font-size:.68rem!important}

/* Diagnosis — purple engineering-analysis identity */
.eh29-gate{
    padding:.78rem .9rem!important;border-radius:12px!important;
    font-size:.70rem!important;line-height:1.5!important;
}
.eh29-dx-card{
    min-height:205px!important;padding:.9rem!important;border-radius:15px!important;
    box-shadow:0 7px 18px rgba(16,24,40,.055)!important;
    border-top-width:4px!important;
}
.eh29-dx-card:nth-child(1){border-top-color:#2563eb!important;background:linear-gradient(180deg,#fff,#f7fbff)!important}
.eh29-dx-card:nth-child(2){border-top-color:#7c3aed!important;background:linear-gradient(180deg,#fff,#faf7ff)!important}
.eh29-dx-card:nth-child(3){border-top-color:#0f766e!important;background:linear-gradient(180deg,#fff,#f4fcfb)!important}
.eh29-dx-top{display:flex;align-items:center;gap:.45rem}
.eh29-dx-icon{
    width:34px;height:34px;min-width:34px;border-radius:10px;
    display:inline-flex;align-items:center;justify-content:center;
    background:#f0ebff;border:1px solid #ded2ff;font-size:1rem;
}
.eh29-dx-rank{font-size:.59rem!important}
.eh29-dx-title{font-size:.90rem!important;line-height:1.25!important;margin:.42rem 0 .45rem!important}
.eh29-dx-card li{font-size:.67rem!important;line-height:1.45!important;margin:.18rem 0!important}
.eh29-dx-caution{font-size:.62rem!important;padding:.5rem!important;line-height:1.4!important}
.eh29-panel{
    min-height:300px!important;padding:.9rem!important;border-radius:15px!important;
    box-shadow:0 6px 16px rgba(16,24,40,.045)!important;
}
.eh29-panel-title{font-size:.78rem!important}
.eh29-panel-sub{font-size:.64rem!important;line-height:1.4!important}
.eh29-check{font-size:.67rem!important;padding:.55rem 0!important}
.eh29-check span{font-size:.82rem!important}
.eh29-caution{font-size:.62rem!important}
.eh29-correlation{
    padding:.9rem!important;border-radius:15px!important;
    box-shadow:0 6px 16px rgba(16,24,40,.045)!important
}
.eh29-correlation table{font-size:.64rem!important}

/* Overview panels — each context gets its own subtle visual language */
.eh22-panel{
    border-radius:15px!important;
    padding:1rem 1.05rem!important;
    box-shadow:0 6px 16px rgba(16,24,40,.045)!important;
    border-color:#dce4ee!important;
}
.eh22-panel-head{
    font-size:.94rem!important;
    padding-bottom:.62rem!important;
    letter-spacing:.005em!important;
}
.eh22-panel-sub{font-size:.72rem!important;line-height:1.4!important;margin:.38rem 0 .62rem!important}
.eh-panel-condition{background:linear-gradient(180deg,#f7fffb,#ffffff)!important;border-top:4px solid #12b76a!important}
.eh-panel-alert{background:linear-gradient(180deg,#fffaf4,#ffffff)!important;border-top:4px solid #f79009!important}
.eh-panel-read{background:linear-gradient(180deg,#f7f9ff,#ffffff)!important;border-top:4px solid #4f46e5!important}
.eh-panel-trend{background:linear-gradient(180deg,#f4fbff,#ffffff)!important;border-top:4px solid #0284c7!important}
.eh-panel-evidence{background:linear-gradient(180deg,#f8fafc,#ffffff)!important;border-top:4px solid #64748b!important}
.eh-panel-action{background:linear-gradient(180deg,#fff9f0,#ffffff)!important;border-top:4px solid #f97316!important}

.eh22-dist-row{font-size:.73rem!important;padding:.58rem .45rem!important}
.eh22-dist-row strong{font-size:1.02rem!important}
.eh22-abnormal-row{padding:.62rem .45rem!important}
.eh22-abnormal-main>b{font-size:.75rem!important}
.eh22-tag{font-size:.61rem!important}
.eh22-status-pill{font-size:.58rem!important;padding:.22rem .4rem!important}
.eh22-abnormal-value b{font-size:.78rem!important}
.eh22-abnormal-value small{font-size:.58rem!important}
.eh22-read-card{padding:.8rem!important;border-radius:11px!important}
.eh22-read-title{font-size:.88rem!important}
.eh22-read-text{font-size:.72rem!important;line-height:1.5!important}
.eh22-read-small{font-size:.64rem!important}
.eh22-evidence-chip{min-height:78px!important;padding:.7rem .75rem!important;border-radius:11px!important}
.eh22-evidence-chip span{font-size:.59rem!important}
.eh22-evidence-chip b{font-size:.80rem!important}
.eh22-evidence-chip small{font-size:.62rem!important}
.eh22-evidence-row{font-size:.70rem!important;padding:.55rem 0!important}
.eh22-recommendation{
    min-height:145px!important;padding:1rem 1.05rem!important;border-radius:15px!important;
    box-shadow:0 6px 16px rgba(16,24,40,.04)!important
}
.eh22-rec-head{font-size:.72rem!important}
.eh22-rec-title{font-size:.88rem!important;line-height:1.45!important}
.eh22-rec-note{font-size:.67rem!important;line-height:1.45!important}
.eh22-panel .stButton>button{
    min-height:42px!important;border-radius:10px!important;font-size:.72rem!important
}
.eh22-disclaimer{font-size:.65rem!important;padding:.68rem .8rem!important;border-radius:11px!important}

/* Trend warning is intentionally prominent when evidence is stale */
.eh22-panel-trend + *{}
[data-testid="stAlert"]{
    border-radius:13px!important;
}
[data-testid="stAlert"] p{
    font-size:.78rem!important;line-height:1.5!important;
}

/* Streamlit selectors / inputs — make the controls easier to read */
.eh22-header + div{}
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"]{
    min-height:48px!important;
    font-size:.88rem!important;
}
[data-testid="stTextInput"] input{padding-left:.85rem!important}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div{
    font-size:.86rem!important;
}

/* Keep the intentional whitespace between blocks */
.eh22-hero{margin:.8rem 0 1rem!important}
.eh22-decision{margin:1rem 0 1.1rem!important}
.eh25-section-title{margin-top:1.45rem!important}
.eh26-section-title{margin-top:1.5rem!important}
.eh28-section-title{margin-top:1.5rem!important}
.eh29-section-title{margin-top:1.5rem!important}
.eh22-panel,.eh22-recommendation,.eh29-panel,.eh29-correlation{margin-bottom:.2rem!important}

/* Responsive: retain larger type without breaking the matrix */
@media(max-width:1100px){
    .eh22-title{font-size:1.8rem!important}
    .eh26-context-grid{grid-template-columns:repeat(2,1fr)!important}
}
@media(max-width:700px){
    .eh22-title{font-size:1.55rem!important}
    .eh22-hero{min-height:0!important}
    .eh26-context-grid,.eh28-maint-grid{grid-template-columns:1fr!important}
    .eh22-kpi{min-height:112px!important}
}


/* v31 Evidence Engine visual layer */
.eh29-evidence-badge{float:right;font-size:.56rem!important;padding:.26rem .48rem;border-radius:999px;background:#eef2f7;color:#64748b;border:1px solid #dbe3ec;letter-spacing:.04em}
.eh29-strength{display:flex;align-items:center;justify-content:space-between;margin:.65rem 0 .75rem;padding:.62rem .72rem;border-radius:10px;background:#f7f9fc;border:1px solid #e2e8f0;font-size:.62rem;color:#64748b}
.eh29-strength b{font-size:.72rem;letter-spacing:.04em}
.eh29-strength-strong{border-color:#b7e7cb;background:#effbf4;color:#087443}
.eh29-strength-moderate{border-color:#ffd59c;background:#fff8ed;color:#a85b00}
.eh29-strength-weak{border-color:#ffe2b7;background:#fffaf2;color:#9a6700}
.eh29-strength-low{border-color:#dce3ec;background:#f8fafc;color:#64748b}
.eh29-evidence-group{margin:.65rem 0 .8rem}
.eh29-group-title{display:flex;align-items:center;gap:.35rem;font-size:.62rem;font-weight:900;letter-spacing:.035em;color:#334155;margin-bottom:.45rem}
.eh29-group-title span{margin-left:auto;border-radius:999px;padding:.15rem .38rem;background:#eef2f7;color:#64748b;font-size:.55rem}
.eh29-evidence-item{padding:.62rem .68rem;margin:.42rem 0;border-radius:11px;border:1px solid #e2e8f0;background:#fff}
.eh29-evidence-item.support{border-left:4px solid #f79009;background:linear-gradient(90deg,#fffaf2,#fff)}
.eh29-evidence-item.contradict{border-left:4px solid #12b76a;background:linear-gradient(90deg,#f4fcf7,#fff)}
.eh29-evidence-item.context{border-left:4px solid #94a3b8;background:#fafbfd}
.eh29-evidence-item-top{display:flex;align-items:center;gap:.45rem}
.eh29-evidence-icon{width:27px;height:27px;min-width:27px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;background:#f1f5f9;font-size:.78rem}
.eh29-evidence-item-top b{display:block;font-size:.72rem;color:#23395d;line-height:1.2}
.eh29-evidence-item-top small{display:block;font-size:.57rem;color:#94a3b8;margin-top:.12rem}
.eh29-evidence-state{margin-left:auto;font-size:.52rem;font-weight:900;padding:.23rem .38rem;border-radius:999px;background:#eef2f7;color:#64748b}
.eh29-evidence-value{display:flex;align-items:baseline;gap:.25rem;margin:.42rem 0 .22rem;padding-left:2.05rem}
.eh29-evidence-value strong{font-size:.86rem;color:#172b4d}
.eh29-evidence-value span{font-size:.58rem;color:#64748b}
.eh29-evidence-metrics{margin-left:auto!important;font-size:.55rem!important;color:#64748b!important}
.eh29-evidence-reason{padding-left:2.05rem;font-size:.62rem;line-height:1.42;color:#475569}
.eh29-evidence-meta{padding-left:2.05rem;margin-top:.32rem;font-size:.53rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.025em}
.eh29-no-evidence{padding:.55rem .65rem;border-radius:9px;background:#f8fafc;color:#94a3b8;font-size:.60rem}
.eh29-evidence-foot{margin-top:.65rem;padding:.62rem .7rem;border-radius:10px;background:#fff8ed;border:1px solid #ffe0b5;color:#8a5a16;font-size:.58rem;line-height:1.45}
.eh29-correlation td small{display:block;color:#94a3b8;font-size:.53rem;margin-top:.12rem}
.eh29-corr-pill{display:inline-block;padding:.24rem .45rem;border-radius:999px;font-weight:900;font-size:.61rem}
.eh29-corr-pill.positive{background:#eaf8ef;color:#087443}
.eh29-corr-pill.negative{background:#fff0f0;color:#b42318}
.eh29-correlation table td{vertical-align:middle!important}


/* v32 Evidence Intelligence */
.eh29-strength.strength-historical,
.eh29-strength.strength-historical-weak,
.eh29-strength.strength-not-verifiable{
    background:linear-gradient(90deg,#fff7e8,#f8fafc)!important;
    border-color:#f4b860!important;
    color:#a15c00!important;
}
.eh29-evidence-badge{
    float:right!important;
    border-radius:999px!important;
    padding:.25rem .55rem!important;
    background:#f1f5f9!important;
    color:#64748b!important;
    font-size:.58rem!important;
    letter-spacing:.04em!important;
}
.eh29-evidence-item.support{
    border-left-color:#f79009!important;
    background:linear-gradient(180deg,#fffdf9,#ffffff)!important;
}
.eh29-evidence-item.contradict{
    border-left-color:#12b76a!important;
    background:linear-gradient(180deg,#f9fffc,#ffffff)!important;
}
.eh29-evidence-item.context{
    border-left-color:#94a3b8!important;
    background:linear-gradient(180deg,#fafbfc,#ffffff)!important;
}
.eh29-group-title{
    font-size:.68rem!important;
    font-weight:900!important;
    letter-spacing:.025em!important;
    margin:.9rem 0 .48rem!important;
}
.eh29-group-title span{
    float:right!important;
    min-width:22px!important;
    text-align:center!important;
    border-radius:999px!important;
    padding:.16rem .35rem!important;
    background:#eef2f7!important;
}
.eh29-evidence-reason{
    font-size:.70rem!important;
    line-height:1.48!important;
}
.eh29-evidence-meta{
    font-size:.57rem!important;
    letter-spacing:.02em!important;
}


/* ================================================================
   v33 — RESPONSIVE TYPOGRAPHY & BLOCK-FIT
   Prinsip:
   1) Tidak ada teks penting yang boleh keluar dari block.
   2) Nilai panjang boleh wrap; status/pill tetap terbaca.
   3) Ukuran font menyesuaikan lebar viewport.
   4) Hero, KPI, context, diagnosis, evidence, recommendation,
      dan tabel mendapat perlakuan yang konsisten.
   ================================================================ */

/* Global text safety inside the Equipment Health workspace */
.eh22-hero *,
.eh22-kpi *,
.eh22-panel *,
.eh22-decision *,
.eh25-matrix *,
.eh26-context-card *,
.eh29-card *,
.eh29-evidence-item *,
.eh29-strength *,
.eh29-correlation *,
.eh29-group-title *,
.eh29-evidence-badge *{
    min-width:0;
    box-sizing:border-box;
}

/* ---------- Hero equipment ---------- */
.eh22-hero{
    min-width:0;
    overflow:hidden;
}
.eh22-hero-left{
    min-width:0;
    flex:1 1 auto;
}
.eh22-hero-right{
    min-width:0;
    flex:0 1 42%;
    white-space:normal;
    overflow-wrap:anywhere;
}
.eh22-code{
    font-size:clamp(1.05rem,1.7vw,1.45rem);
    overflow-wrap:anywhere;
}
.eh22-name{
    max-width:100%;
    white-space:normal;
    overflow-wrap:anywhere;
    line-height:1.25;
}
.eh22-status{
    white-space:normal;
    overflow-wrap:anywhere;
    line-height:1.15;
    max-width:100%;
}
.eh22-last{
    white-space:normal;
    overflow-wrap:anywhere;
    line-height:1.3;
}

/* ---------- KPI cards ---------- */
.eh22-kpi{
    min-width:0;
    overflow:hidden;
}
.eh22-kpi-label{
    line-height:1.25;
    overflow-wrap:anywhere;
    word-break:normal;
}
.eh22-kpi-value{
    font-size:clamp(1.05rem,1.65vw,1.36rem);
    line-height:1.08;
    white-space:normal;
    overflow-wrap:anywhere;
    word-break:break-word;
    hyphens:auto;
}
.eh22-kpi-value small{
    display:inline;
    white-space:normal;
    overflow-wrap:anywhere;
}
.eh22-kpi-small{
    white-space:normal;
    overflow-wrap:anywhere;
    word-break:normal;
}

/* ---------- Decision / alert blocks ---------- */
.eh22-decision{
    min-width:0;
    align-items:flex-start;
}
.eh22-decision > div:last-child{
    min-width:0;
    flex:1 1 auto;
}
.eh22-decision-title,
.eh22-decision-text{
    white-space:normal;
    overflow-wrap:anywhere;
    word-break:normal;
}

/* ---------- Generic panels / headings ---------- */
.eh22-panel-head,
.eh22-panel-sub{
    white-space:normal;
    overflow-wrap:anywhere;
}
.eh22-panel-head{
    line-height:1.25;
}

/* ---------- Parameter matrix ---------- */
.eh25-matrix,
.eh25-matrix table,
.eh25-matrix td,
.eh25-matrix th{
    max-width:100%;
}
.eh25-matrix td,
.eh25-matrix th{
    white-space:normal !important;
    overflow-wrap:anywhere;
    word-break:normal;
    line-height:1.25;
}
.eh25-matrix td:first-child,
.eh25-matrix th:first-child{
    min-width:0;
}

/* ---------- Operating context cards ---------- */
.eh26-context-card{
    min-width:0;
    overflow:hidden;
}
.eh26-context-label,
.eh26-context-value,
.eh26-context-sub{
    white-space:normal !important;
    overflow-wrap:anywhere;
    word-break:normal;
}
.eh26-context-value{
    font-size:clamp(.82rem,1.25vw,1.08rem) !important;
    line-height:1.18 !important;
}
.eh26-context-sub{
    max-width:100%;
    overflow:hidden;
    text-overflow:ellipsis;
}

/* ---------- Maintenance / diagnosis cards ---------- */
.eh29-card{
    min-width:0;
    overflow:hidden;
}
.eh29-card *,
.eh29-rule *,
.eh29-diagnosis-card *{
    overflow-wrap:anywhere;
}
.eh29-card-title,
.eh29-title,
.eh29-diagnosis-title{
    white-space:normal !important;
    line-height:1.2 !important;
}
.eh29-card-sub,
.eh29-caution,
.eh29-evidence-reason{
    white-space:normal !important;
    line-height:1.4 !important;
    overflow-wrap:anywhere;
}

/* ---------- Evidence blocks ---------- */
.eh29-evidence-item{
    min-width:0;
    overflow:hidden;
}
.eh29-evidence-item *{
    max-width:100%;
}
.eh29-evidence-item.support,
.eh29-evidence-item.contradict,
.eh29-evidence-item.context{
    white-space:normal;
}
.eh29-evidence-meta{
    white-space:normal !important;
    overflow-wrap:anywhere;
    line-height:1.35 !important;
}
.eh29-evidence-badge{
    float:none !important;
    display:inline-block;
    max-width:100%;
    white-space:normal !important;
    overflow-wrap:anywhere;
}
.eh29-group-title{
    line-height:1.25 !important;
    white-space:normal !important;
    overflow-wrap:anywhere;
}
.eh29-group-title span{
    float:none !important;
    display:inline-block;
    margin-left:.25rem;
}

/* ---------- Strength banner ---------- */
.eh29-strength{
    min-width:0;
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:.5rem;
    flex-wrap:wrap;
}
.eh29-strength span,
.eh29-strength b{
    white-space:normal !important;
    overflow-wrap:anywhere;
}

/* ---------- Correlation table ---------- */
.eh29-correlation table,
.eh29-correlation td,
.eh29-correlation th{
    max-width:100%;
}
.eh29-correlation td,
.eh29-correlation th{
    white-space:normal !important;
    overflow-wrap:anywhere;
    line-height:1.25;
}

/* ---------- Engineering recommendation / next action ---------- */
.eh22-read-card *,
.eh22-recommendation *,
.eh22-next-action *,
.eh29-recommendation *{
    white-space:normal !important;
    overflow-wrap:anywhere;
}
.eh22-read-card,
.eh22-recommendation,
.eh22-next-action,
.eh29-recommendation{
    min-width:0;
    overflow:hidden;
}

/* ---------- Older health classes still present in the file ---------- */
.health-kpi,
.health-kpi *,
.health-v8-banner,
.health-v8-banner *,
.health-v8-table td,
.health-v8-table th{
    min-width:0;
}
.health-kpi-value{
    white-space:normal !important;
    overflow-wrap:anywhere;
    word-break:break-word;
}
.health-v8-banner-right{
    white-space:normal !important;
    overflow-wrap:anywhere;
}

/* ---------- Responsive breakpoints ---------- */
@media (max-width: 1100px){
    .eh22-hero{
        flex-direction:column;
        align-items:stretch;
    }
    .eh22-hero-right{
        flex:1 1 auto;
        text-align:left;
    }
    .eh22-status{
        display:inline-block;
    }
}

@media (max-width: 760px){
    .eh22-kpi{
        min-height:88px;
        padding:.62rem .68rem;
    }
    .eh22-kpi-label{
        font-size:.56rem;
    }
    .eh22-kpi-value{
        font-size:1.02rem;
    }
    .eh22-kpi-small{
        font-size:.57rem;
    }
    .eh22-hero{
        padding:.85rem .9rem;
    }
    .eh22-code{
        font-size:1.05rem;
    }
    .eh22-name{
        font-size:.70rem;
    }
    .eh22-status{
        font-size:.65rem;
    }
}

@media (max-width: 520px){
    .eh22-kpi{
        min-height:82px;
    }
    .eh22-kpi-value{
        font-size:.96rem;
    }
    .eh22-kpi-value small{
        font-size:.60rem;
    }
    .eh22-decision{
        gap:.5rem;
        padding:.58rem .62rem;
    }
}

/* Prevent long numeric values from visually escaping cards */
.eh22-kpi-value,
.eh26-context-value,
.eh29-evidence-item,
.eh29-card,
.eh22-decision-text,
.eh22-read-card,
.eh22-recommendation,
.eh22-next-action{
    overflow-wrap:anywhere;
    word-break:break-word;
}


/* ================================================================
   v34 — KPI STRIP ALIGNMENT
   Lima KPI dibuat sebagai satu visual strip yang sejajar:
   - tinggi card sama
   - label berada pada baseline yang sama
   - value memiliki area tinggi yang sama
   - secondary text memiliki area yang sama
   - long status wrap 1–2 baris tanpa memperbesar card
   ================================================================ */

.eh22-kpi{
    height:132px !important;
    min-height:132px !important;
    max-height:132px !important;
    width:100% !important;
    min-width:0 !important;
    overflow:hidden !important;
    display:flex !important;
    flex-direction:column !important;
    justify-content:flex-start !important;
    padding:.68rem .72rem !important;
    border-radius:12px !important;
}

/* Semua lima label memiliki ruang yang sama. */
.eh22-kpi-label{
    min-height:17px !important;
    height:17px !important;
    display:flex !important;
    align-items:flex-start !important;
    font-size:.58rem !important;
    line-height:1.15 !important;
    letter-spacing:.025em !important;
    white-space:normal !important;
    overflow:hidden !important;
    overflow-wrap:anywhere !important;
}

/* Area value dibuat sama tinggi sehingga subtitle selalu mulai sejajar. */
.eh22-kpi-value{
    min-height:43px !important;
    height:43px !important;
    max-height:43px !important;
    margin-top:.28rem !important;
    display:flex !important;
    align-items:flex-start !important;
    gap:.12rem !important;
    font-size:clamp(.98rem,1.28vw,1.18rem) !important;
    line-height:1.10 !important;
    white-space:normal !important;
    overflow:hidden !important;
    overflow-wrap:anywhere !important;
    word-break:normal !important;
}

/* Pisahkan status text panjang agar tetap terbaca dalam 2 baris. */
.eh22-kpi-value{
    text-overflow:clip !important;
}

/* Suffix / denominator tidak boleh memaksa lebar card. */
.eh22-kpi-value small{
    flex:0 1 auto !important;
    min-width:0 !important;
    max-width:45% !important;
    font-size:.62rem !important;
    line-height:1.15 !important;
    white-space:normal !important;
    overflow-wrap:anywhere !important;
}

/* Secondary description konsisten berada di bawah value. */
.eh22-kpi-small{
    min-height:30px !important;
    max-height:30px !important;
    margin-top:.08rem !important;
    font-size:.57rem !important;
    line-height:1.28 !important;
    white-space:normal !important;
    overflow:hidden !important;
    overflow-wrap:anywhere !important;
    word-break:normal !important;
}

/* Khusus value yang sangat panjang: tetap 2 baris maksimum. */
.eh22-kpi-value,
.eh22-kpi-value *{
    -webkit-line-clamp:2;
}

/* Parent Streamlit columns: jangan biarkan satu card mengubah tinggi strip. */
div[data-testid="stHorizontalBlock"]:has(.eh22-kpi){
    align-items:stretch !important;
}
div[data-testid="stHorizontalBlock"]:has(.eh22-kpi) > div[data-testid="column"]{
    min-width:0 !important;
    display:flex !important;
    align-items:stretch !important;
}
div[data-testid="stHorizontalBlock"]:has(.eh22-kpi) > div[data-testid="column"] > div{
    width:100% !important;
    min-width:0 !important;
}

/* Desktop: lima card harus terasa sebagai satu strip yang proporsional. */
@media (min-width: 1101px){
    .eh22-kpi{
        height:126px !important;
        min-height:126px !important;
        max-height:126px !important;
    }
    .eh22-kpi-label{font-size:.57rem !important;}
    .eh22-kpi-value{font-size:clamp(.92rem,1.16vw,1.10rem) !important;}
    .eh22-kpi-small{font-size:.55rem !important;}
}

/* Tablet/mobile: tetap sejajar dalam row ketika memungkinkan,
   tetapi tinggi card tidak berubah-ubah karena text. */
@media (max-width: 1100px){
    .eh22-kpi{
        height:124px !important;
        min-height:124px !important;
        max-height:124px !important;
    }
}

@media (max-width: 760px){
    .eh22-kpi{
        height:116px !important;
        min-height:116px !important;
        max-height:116px !important;
        padding:.58rem .62rem !important;
    }
    .eh22-kpi-label{
        min-height:15px !important;
        height:15px !important;
        font-size:.53rem !important;
    }
    .eh22-kpi-value{
        min-height:39px !important;
        height:39px !important;
        max-height:39px !important;
        font-size:.90rem !important;
    }
    .eh22-kpi-small{
        min-height:27px !important;
        max-height:27px !important;
        font-size:.52rem !important;
    }
}


/* v35 — Instrument Master / Tag Mapping */
.opp-page-title{font-size:1.55rem!important;font-weight:850!important;color:#182b49!important;letter-spacing:-.02em!important}
.opp-page-sub{font-size:.78rem!important;color:#7b8ba5!important;line-height:1.5!important;margin-bottom:1rem!important}
</style>""",unsafe_allow_html=True)

DB_PATH = ROOT / "data" / "plc_history.sqlite"
DB_SCHEMA_VERSION = 2


def _db_connect():
    """Open the persistent SQLite history database."""
    data_dir = ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    import sqlite3
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _json_safe_record(record):
    """Convert a pandas row into strict JSON-safe Python values."""
    safe = {}
    for key, value in record.items():
        if pd.isna(value) if not isinstance(value, (list, tuple, dict)) else False:
            safe[str(key)] = None
        elif isinstance(value, (pd.Timestamp, np.datetime64)):
            safe[str(key)] = pd.Timestamp(value).isoformat()
        elif isinstance(value, (np.integer,)):
            safe[str(key)] = int(value)
        elif isinstance(value, (np.floating,)):
            safe[str(key)] = None if not np.isfinite(value) else float(value)
        elif isinstance(value, (np.bool_,)):
            safe[str(key)] = bool(value)
        else:
            safe[str(key)] = value
    return safe


def _init_history_db():
    """Create the database and migrate legacy CSV archives once."""
    conn = _db_connect()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS plc_history (
                archive_time TEXT PRIMARY KEY,
                payload BLOB NOT NULL,
                source_file TEXT,
                imported_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS import_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file TEXT NOT NULL,
                imported_at TEXT NOT NULL,
                rows_received INTEGER NOT NULL,
                rows_inserted INTEGER NOT NULL,
                rows_duplicate INTEGER NOT NULL,
                rows_invalid INTEGER NOT NULL,
                first_timestamp TEXT,
                last_timestamp TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_plc_history_time ON plc_history(archive_time)")
        conn.execute("CREATE TABLE IF NOT EXISTS app_meta (key TEXT PRIMARY KEY, value TEXT)")
        conn.execute("INSERT OR IGNORE INTO app_meta(key,value) VALUES('schema_version',?)", (str(DB_SCHEMA_VERSION),))
        conn.commit()

        # Migrate any legacy v9 *.csv.gz rows that are not already in SQLite.
        # INSERT OR IGNORE makes this safe even if migration was partially completed.
        legacy_files = sorted((ROOT / "data").glob("*.csv.gz"))
        migrated = conn.execute("SELECT value FROM app_meta WHERE key='legacy_csv_migrated'").fetchone()
        if legacy_files and not migrated:
            import gzip, json
            now = pd.Timestamp.utcnow().isoformat()
            for f in legacy_files:
                try:
                    part = pd.read_csv(f, parse_dates=["ArchiveTime"])
                    if "ArchiveTime" not in part.columns:
                        continue
                    part["ArchiveTime"] = pd.to_datetime(part["ArchiveTime"], errors="coerce")
                    part = part.dropna(subset=["ArchiveTime"]).drop_duplicates("ArchiveTime", keep="last")
                    for _, row in part.iterrows():
                        ts = pd.Timestamp(row["ArchiveTime"]).isoformat()
                        raw = json.dumps(_json_safe_record(row.to_dict()), ensure_ascii=False, allow_nan=False).encode("utf-8")
                        blob = gzip.compress(raw, compresslevel=6)
                        conn.execute(
                            "INSERT OR IGNORE INTO plc_history(archive_time,payload,source_file,imported_at) VALUES(?,?,?,?)",
                            (ts, blob, f.name, now)
                        )
                except Exception:
                    continue
            conn.execute("INSERT OR REPLACE INTO app_meta(key,value) VALUES('legacy_csv_migrated','1')")
            conn.commit()
    finally:
        conn.close()


@st.cache_data(show_spinner=False)
def load_history():
    """Load the single persistent PLC history source used by all pages."""
    import gzip, json
    _init_history_db()
    conn = _db_connect()
    try:
        rows = conn.execute("SELECT archive_time, payload FROM plc_history ORDER BY archive_time").fetchall()
    finally:
        conn.close()

    if not rows:
        return pd.DataFrame(columns=["ArchiveTime"])

    records = []
    for ts, blob in rows:
        try:
            record = json.loads(gzip.decompress(blob).decode("utf-8"))
            record["ArchiveTime"] = pd.to_datetime(ts, errors="coerce")
            records.append(record)
        except Exception:
            continue
    if not records:
        return pd.DataFrame(columns=["ArchiveTime"])
    history = pd.DataFrame.from_records(records)
    history["ArchiveTime"] = pd.to_datetime(history["ArchiveTime"], errors="coerce")
    history = history.dropna(subset=["ArchiveTime"])
    return history.drop_duplicates("ArchiveTime", keep="last").sort_values("ArchiveTime").reset_index(drop=True)


def persist_daily_import(incoming, source_name="PLC_Import"):
    """Transactionally append only new PLC timestamps to SQLite.

    ArchiveTime is the unique key, making repeated uploads idempotent.
    """
    import gzip, json
    _init_history_db()
    incoming = incoming.copy()
    received = len(incoming)
    incoming["ArchiveTime"] = pd.to_datetime(incoming["ArchiveTime"], errors="coerce")
    invalid = int(incoming["ArchiveTime"].isna().sum())
    incoming = incoming.dropna(subset=["ArchiveTime"]).drop_duplicates("ArchiveTime", keep="last")

    conn = _db_connect()
    inserted = 0
    duplicate = 0
    now = pd.Timestamp.utcnow().isoformat()
    try:
        conn.execute("BEGIN IMMEDIATE")
        for _, row in incoming.sort_values("ArchiveTime").iterrows():
            ts = pd.Timestamp(row["ArchiveTime"]).isoformat()
            raw = json.dumps(_json_safe_record(row.to_dict()), ensure_ascii=False, allow_nan=False).encode("utf-8")
            blob = gzip.compress(raw, compresslevel=6)
            cur = conn.execute(
                "INSERT OR IGNORE INTO plc_history(archive_time,payload,source_file,imported_at) VALUES(?,?,?,?)",
                (ts, blob, Path(source_name).name, now)
            )
            if cur.rowcount == 1:
                inserted += 1
            else:
                duplicate += 1

        first_ts = incoming["ArchiveTime"].min().isoformat() if not incoming.empty else None
        last_ts = incoming["ArchiveTime"].max().isoformat() if not incoming.empty else None
        conn.execute(
            """INSERT INTO import_log
               (source_file, imported_at, rows_received, rows_inserted, rows_duplicate,
                rows_invalid, first_timestamp, last_timestamp)
               VALUES (?,?,?,?,?,?,?,?)""",
            (Path(source_name).name, now, received, inserted, duplicate, invalid, first_ts, last_ts)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return inserted, DB_PATH


def history_database_stats():
    """Return database status for the Data Import page."""
    _init_history_db()
    conn = _db_connect()
    try:
        row = conn.execute("SELECT COUNT(*), MIN(archive_time), MAX(archive_time) FROM plc_history").fetchone()
        imports = conn.execute("SELECT COUNT(*) FROM import_log").fetchone()[0]
        return int(row[0] or 0), row[1], row[2], int(imports or 0)
    finally:
        conn.close()

@st.cache_data

def recent_import_log(limit=10):
    """Return the most recent import batches for operational traceability."""
    _init_history_db()
    conn = _db_connect()
    try:
        rows = conn.execute(
            """SELECT imported_at, source_file, rows_received, rows_inserted, rows_duplicate,
                      rows_invalid, first_timestamp, last_timestamp
               FROM import_log ORDER BY id DESC LIMIT ?""",
            (int(limit),)
        ).fetchall()
    finally:
        conn.close()
    cols = ["Imported At", "Source File", "Rows Received", "Rows Inserted", "Rows Duplicate",
            "Rows Invalid", "First Timestamp", "Last Timestamp"]
    return pd.DataFrame(rows, columns=cols)



# --- Engineering Mapping Master ---------------------------------------------------
ENGINEERING_MAPPING_COLUMNS = [
    "PLC Tag", "Equipment Code", "Equipment", "Area", "Parameter", "Unit",
    "Mapping Status", "Identification Status", "Confidence", "Evidence",
    "Verified By", "Verified Date", "Source"
]

@st.cache_data
def load_engineering_mapping_master():
    """Load engineer-confirmed PLC-to-equipment mappings.

    This file is intentionally separate from PLC Historian and raw Tag Master.
    It is safe to version-control as an engineering configuration artifact.
    """
    path = ROOT / "config" / "engineering_mapping_master.csv"
    if not path.exists():
        return pd.DataFrame(columns=ENGINEERING_MAPPING_COLUMNS)
    try:
        m = pd.read_csv(path, dtype=str).fillna("")
        for c in ENGINEERING_MAPPING_COLUMNS:
            if c not in m.columns:
                m[c] = ""
        return m[ENGINEERING_MAPPING_COLUMNS].copy()
    except Exception:
        return pd.DataFrame(columns=ENGINEERING_MAPPING_COLUMNS)


def _mapping_store_init(existing_mapping):
    """Create session mapping store, preserving committed engineer mappings."""
    if "engineering_mapping_master" not in st.session_state:
        store = {}
        if isinstance(existing_mapping, pd.DataFrame) and not existing_mapping.empty:
            for _, r in existing_mapping.iterrows():
                tag = str(r.get("PLC Tag", "")).strip()
                if tag:
                    store[tag] = {c: str(r.get(c, "") or "").strip() for c in ENGINEERING_MAPPING_COLUMNS}
        st.session_state["engineering_mapping_master"] = store
    return st.session_state["engineering_mapping_master"]


def engineering_mapping_dataframe(store):
    if not store:
        return pd.DataFrame(columns=ENGINEERING_MAPPING_COLUMNS)
    rows = []
    for tag, rec in store.items():
        row = {c: str(rec.get(c, "") or "").strip() for c in ENGINEERING_MAPPING_COLUMNS}
        row["PLC Tag"] = row["PLC Tag"] or str(tag)
        rows.append(row)
    return pd.DataFrame(rows, columns=ENGINEERING_MAPPING_COLUMNS).sort_values("PLC Tag").reset_index(drop=True)


def apply_engineering_mappings(master, mapping_store):
    """Apply only engineer-saved mappings to the working Tag Master.

    Raw PLC history is never changed. The mapping is an overlay used by
    Equipment Health / Trend / Priority views.
    """
    out = master.copy()
    if not mapping_store:
        out["Engineering Mapping Status"] = ""
        out["Engineering Mapping Source"] = ""
        out["Engineering Mapping Verified By"] = ""
        out["Engineering Mapping Verified Date"] = ""
        return out
    mm = engineering_mapping_dataframe(mapping_store)
    if mm.empty:
        return out
    mm = mm.drop_duplicates("PLC Tag", keep="last").set_index("PLC Tag")
    for c in ["Engineering Mapping Status", "Engineering Mapping Source", "Engineering Mapping Verified By", "Engineering Mapping Verified Date"]:
        out[c] = ""
    for idx, r in out.iterrows():
        tag = str(r.get("PLC Tag", "")).strip()
        if not tag or tag not in mm.index:
            continue
        m = mm.loc[tag]
        status = str(m.get("Mapping Status", "")).strip()
        if status not in {"CONFIRMED", "VERIFIED"}:
            continue
        # Mapping master is authoritative only after engineer confirmation.
        if str(m.get("Equipment Code", "")).strip(): out.at[idx, "Equipment Code"] = str(m["Equipment Code"]).strip()
        if str(m.get("Equipment", "")).strip(): out.at[idx, "Equipment"] = str(m["Equipment"]).strip()
        if str(m.get("Area", "")).strip(): out.at[idx, "Area"] = str(m["Area"]).strip()
        if str(m.get("Parameter", "")).strip(): out.at[idx, "Suggested Parameter"] = str(m["Parameter"]).strip()
        if str(m.get("Unit", "")).strip(): out.at[idx, "Suggested Unit"] = str(m["Unit"]).strip()
        out.at[idx, "Engineering Mapping Status"] = status
        out.at[idx, "Engineering Mapping Source"] = str(m.get("Source", "Engineer Mapping Master")).strip()
        out.at[idx, "Engineering Mapping Verified By"] = str(m.get("Verified By", "")).strip()
        out.at[idx, "Engineering Mapping Verified Date"] = str(m.get("Verified Date", "")).strip()
    return out


def _mapping_candidate_label(code, name):
    code, name = str(code or "").strip(), str(name or "").strip()
    return f"{code} — {name}" if code and name else (code or name or "")


def _mapping_parse_candidate(label):
    text = str(label or "").strip()
    if " — " in text:
        code, name = text.split(" — ", 1)
        return code.strip(), name.strip()
    return text, ""


def build_mapping_review_queue(master, identification_report, mapping_store, instrument_master=None):
    """Build the engineer review queue without changing historian data.

    EXACT MATCH is considered auto-identified from the Instrument Master and is
    therefore not placed in the manual queue. Manual effort is reserved for
    POSSIBLE / REVIEW / NOT FOUND items, with additional equipment candidates
    generated from the existing Tag Master and equipment-code pattern.
    """
    rows = []
    report = identification_report.copy() if isinstance(identification_report, pd.DataFrame) else pd.DataFrame()
    by_tag = report.set_index("PLC Tag").to_dict("index") if not report.empty else {}
    for _, r in master.iterrows():
        tag = str(r.get("PLC Tag", "")).strip()
        if not tag:
            continue
        saved = mapping_store.get(tag, {}) if isinstance(mapping_store, dict) else {}
        saved_status = str(saved.get("Mapping Status", "")).strip()
        ident = by_tag.get(tag, {})
        ident_status = str(ident.get("Identification Status", r.get("Instrument Master Match", "NOT FOUND")) or "NOT FOUND")
        # Exact Instrument Master matches are automatically identified and do
        # not burden the daily/manual review queue.
        if ident_status == "EXACT MATCH" and saved_status not in {"SKIPPED"}:
            continue
        cand = _tm_mapping_candidate(tag, master, instrument_master, ident)
        rows.append({
            "PLC Tag": tag,
            "Identification Status": ident_status,
            "Candidate Tag": str(ident.get("Candidate Tag", r.get("Identification Candidate", "")) or ""),
            "Score": float(ident.get("Score", r.get("Identification Score", 0)) or 0),
            "Reason": str(ident.get("Reason", r.get("Identification Reason", "")) or ""),
            "Current Equipment Code": str(r.get("Equipment Code", "") or "").strip(),
            "Current Equipment": str(r.get("Equipment", "") or "").strip(),
            "Current Parameter": str(r.get("Suggested Parameter", "") or "").strip(),
            "Current Unit": str(r.get("Suggested Unit", "") or "").strip(),
            "Mapping Status": saved_status or "PENDING",
            "Mapping Candidate Code": str(cand.get("code", "") if cand else ""),
            "Mapping Candidate Equipment": str(cand.get("name", "") if cand else ""),
            "Mapping Candidate Area": str(cand.get("area", "") if cand else ""),
            "Mapping Candidate Source": str(cand.get("source", "") if cand else ""),
            "Mapping Candidate Confidence": float(cand.get("confidence", 0) if cand else 0),
            "Mapping Candidate Evidence": str(cand.get("evidence", "") if cand else ""),
        })
    q = pd.DataFrame(rows)
    if q.empty:
        return q
    q = q[~q["Mapping Status"].isin(["CONFIRMED", "VERIFIED"])].copy()
    order = {"REVIEW REQUIRED":1, "POSSIBLE MATCH":2, "NOT FOUND":3}
    q["_order"] = q["Identification Status"].map(order).fillna(9)
    # Within NOT FOUND, candidates backed by an existing equipment identity are
    # more actionable than a completely unresolved tag.
    q["_cand"] = q["Mapping Candidate Code"].astype(str).str.strip().ne("").astype(int)
    q = q.sort_values(["_order", "_cand", "Score", "PLC Tag"], ascending=[True, False, False, True])
    return q.drop(columns=["_order", "_cand"]).reset_index(drop=True)

def load_master():
    return pd.read_csv(ROOT / "config" / "tag_master.csv").fillna("")

@st.cache_data
def load_instrument_master():
    """Load the engineering Instrument Master without mixing it into PLC history."""
    csv_path = ROOT / "config" / "instrument_master.csv"
    xlsx_path = ROOT / "config" / "Instrument List All.xlsx"
    try:
        if csv_path.exists():
            im = pd.read_csv(csv_path, dtype=str).fillna("")
        elif xlsx_path.exists():
            # Fallback for users who prefer to deploy the original engineering workbook.
            im = pd.read_excel(xlsx_path, header=2, engine="openpyxl").fillna("")
            rename = {
                "ITEM NO.\n序号":"Item No", "TAG NO.\n位号":"Tag No",
                "SERVICE\n用途":"Service", "LOCATION\n位置":"Location",
                "LINE NUMBER\n管线号":"Line Number", "P&ID":"P&ID",
                "INSTRUMENT TYPE\n仪表类型":"Instrument Type",
                "REFERENCE DRAWING\n参照图纸":"Reference Drawing",
                "IO\nTYPE":"IO Type", "MANUFACTURER\n制造商":"Manufacturer",
                "MODEL NO.\n型号":"Model No", "SET\nVALUE\n设定值":"Set Value",
                "RANGE\n范围":"Range", "CALIBRATION RANGE\n校准范围":"Calibration Range",
                "UNIT\n单位":"Unit", "REV.\n版本":"Rev",
                "REMARKS\n备注":"Remarks", "Category":"Source Category", "Area":"Area",
            }
            im = im.rename(columns=rename)
            for c in im.columns:
                im[c] = im[c].astype(str).replace({"nan": ""}).str.strip()
        else:
            return pd.DataFrame()

        def _clean(v):
            if pd.isna(v):
                return ""
            return str(v).strip()

        def _norm_tag(v):
            return re.sub(r"\s+", "", _clean(v).upper())

        def _extract_eq(text):
            t = _clean(text).upper()
            m = re.search(r"(?<!\d)(\d{3})[-\s]?([A-Z]{1,5})[-\s]?(\d{1,3})(?!\d)", t)
            return f"{m.group(1)}-{m.group(2)}-{int(m.group(3)):02d}" if m else ""

        def _parameter(row):
            txt = (_clean(row.get("Instrument Type", "")) + " " + _clean(row.get("Service", ""))).lower()
            if any(k in txt for k in ["vibration", "accelerometer"]): return "Vibration"
            if any(k in txt for k in ["temperature", "thermocouple", "rtd", "pt100"]): return "Temperature"
            if "pressure" in txt: return "Pressure"
            if any(k in txt for k in ["flowmeter", "flow meter", "flow gauge", "flow transmitter", "flow switch"]): return "Flow"
            if any(k in txt for k in ["current transmitter", "motor current"]): return "Current"
            if any(k in txt for k in ["power transmitter", "power meter"]): return "Power"
            if any(k in txt for k in ["speed", "underspeed", "rpm"]): return "Speed"
            if any(k in txt for k in ["level transmitter", "level sensor", "level meter", "level gauge"]): return "Level"
            if "density" in txt: return "Density"
            if re.search(r"\bpH\b", _clean(row.get("Instrument Type", "")) + " " + _clean(row.get("Service", "")), re.I): return "pH"
            if "position" in txt: return "Position"
            return ""

        def _category(row):
            it = _clean(row.get("Instrument Type", "")).lower()
            io = _clean(row.get("IO Type", "")).upper()
            if any(k in it for k in ["pullwire","drift switch","underspeed","blocked chute","limit switch","float switch","flow switch","pressure switch","level switch","proximity switch","safety switch","trip","interlock"]):
                return "Protection / Interlock"
            if any(k in it for k in ["solenoid","on/off valve","air control valve","control valve","actuator","modulation valve"]):
                return "Control Element"
            if any(k in it for k in ["siren","beacon","traffic light","indicator","lamp"]):
                return "Indication / Alarm"
            if any(k in it for k in ["transmitter","meter","gauge","sensor","thermocouple","rtd","analyzer","detector"]):
                return "Condition / Measurement"
            if io in {"AI","AO"}:
                return "Condition / Measurement"
            if io in {"DI","DO"}:
                return "Protection / Interlock"
            return "Other"

        if "Tag No" not in im.columns:
            return pd.DataFrame()

        im["Normalized Tag"] = im["Tag No"].map(_norm_tag)
        im["Derived Equipment Code"] = im.apply(
            lambda r: _extract_eq(r.get("Service", "")) or _extract_eq(r.get("Tag No", "")), axis=1
        )
        if "Suggested Parameter" not in im.columns:
            im["Suggested Parameter"] = im.apply(_parameter, axis=1)
        if "Engineering Category" not in im.columns:
            im["Engineering Category"] = im.apply(_category, axis=1)
        return im
    except Exception:
        return pd.DataFrame()



# --- Stage 6: Intelligent Tag Identification -----------------------------------
def _tm_norm_tag(value):
    """Normalize a tag only for comparison; never modify the source tag."""
    if pd.isna(value):
        return ""
    return re.sub(r"[^A-Z0-9]", "", str(value).strip().upper())

def _tm_tag_parts(tag):
    """Return conservative tag structure: prefix, area and suffix."""
    t = _tm_norm_tag(tag)
    m = re.match(r"^([A-Z]+)(\d{3})([A-Z0-9]+)$", t)
    if not m:
        return "", "", t
    return m.group(1), m.group(2), m.group(3)

def _tm_suffix_tokens(suffix):
    return [int(x) for x in re.findall(r"\d+", str(suffix))]

def _tm_parameter_from_tag(tag):
    t = _tm_norm_tag(tag)
    for pattern, _, label, _unit in PARAM_RULES:
        if re.match(pattern, t):
            return label
    return ""

def _tm_unit_norm(value):
    if pd.isna(value):
        return ""
    u = str(value).strip().lower()
    replacements = {
        "m³/h": "m3/h", "m³ / h": "m3/h", "m3 / h": "m3/h",
        "°c": "c", "degc": "c", "℃": "c",
        "mm/s": "mm/s", "r/min": "rpm", "rev/min": "rpm",
        "nm³/h": "nm3/h", "nm3 / h": "nm3/h",
    }
    return replacements.get(u, re.sub(r"\s+", "", u))

def _tm_metadata_validation(source_parameter, source_unit, instrument_parameter, instrument_unit,
                            source_type="", instrument_type="", source_io="", instrument_io=""):
    """Validate source mapping against Instrument Master without silently overwriting it."""
    sp, su = str(source_parameter or "").strip(), str(source_unit or "").strip()
    ip, iu = str(instrument_parameter or "").strip(), str(instrument_unit or "").strip()
    st, it = str(source_type or "").strip(), str(instrument_type or "").strip()
    sio, iio = str(source_io or "").strip().upper(), str(instrument_io or "").strip().upper()
    issues = []
    if ip and sp and sp.lower() != ip.lower():
        issues.append("PARAMETER")
    if iu and su and _tm_unit_norm(su) != _tm_unit_norm(iu):
        issues.append("UNIT")
    if it and st and st.lower() != it.lower():
        issues.append("INSTRUMENT TYPE")
    if iio and sio and sio != iio:
        issues.append("IO TYPE")
    if not issues:
        if ip or iu or it or iio:
            return "VALID", "Metadata konsisten dengan Instrument Master"
        return "INCOMPLETE", "Instrument Master belum memiliki metadata yang cukup"
    return "REVIEW REQUIRED", "Konflik: " + ", ".join(issues)

def _tm_possible_match(plc_tag, instrument_master, min_score=0.90):
    """Find a conservative candidate for a non-exact PLC tag.

    A candidate is only considered when the Area is the same and the tag
    structure is sufficiently similar. This intentionally prefers false
    negatives over unsafe automatic matches.
    """
    from difflib import SequenceMatcher
    ptag = _tm_norm_tag(plc_tag)
    pprefix, parea, psuffix = _tm_tag_parts(ptag)
    if not ptag or not parea or instrument_master is None or instrument_master.empty:
        return None
    pparam = _tm_parameter_from_tag(ptag)
    candidates = []
    for _, r in instrument_master.iterrows():
        itag = _tm_norm_tag(r.get("Tag No", ""))
        if not itag or itag == ptag:
            continue
        iprefix, iarea, isuffix = _tm_tag_parts(itag)
        if iarea != parea:
            continue
        # Same prefix is the safest fuzzy path. A one-character prefix
        # difference is allowed only when the engineering parameter agrees.
        prefix_ok = iprefix == pprefix
        prefix_near = len(iprefix) == len(pprefix) and sum(a != b for a,b in zip(iprefix, pprefix)) == 1
        iparam = str(r.get("Suggested Parameter", "") or "").strip()
        if not prefix_ok and not (prefix_near and pparam and iparam and pparam.lower() == iparam.lower()):
            continue
        # Do not confuse adjacent physical instruments such as HP01 vs HP02.
        pnums, inums = _tm_suffix_tokens(psuffix), _tm_suffix_tokens(isuffix)
        if pnums and inums and pnums != inums:
            # Permit conservative naming differences such as zero-padding
            # (001 vs 01). One extra trailing channel/index of 1 is also
            # allowed, but adjacent physical instruments (01 vs 02) are not.
            pnorm, inorm = [int(x) for x in pnums], [int(x) for x in inums]
            prefix_seq = False
            if len(pnorm) > len(inorm):
                prefix_seq = pnorm[:len(inorm)] == inorm and all(x == 1 for x in pnorm[len(inorm):])
            elif len(inorm) > len(pnorm):
                prefix_seq = inorm[:len(pnorm)] == pnorm and all(x == 1 for x in inorm[len(pnorm):])
            if not prefix_seq and pnorm != inorm:
                continue
        ratio = SequenceMatcher(None, ptag, itag).ratio()
        if ratio < min_score:
            continue
        score = ratio + (0.015 if prefix_ok else 0.0)
        candidates.append((score, ratio, r))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    best = candidates[0]
    second = candidates[1][0] if len(candidates) > 1 else 0.0
    margin = best[0] - second
    # A candidate is not accepted as POSSIBLE MATCH when two candidates are
    # too close; that case becomes REVIEW REQUIRED.
    status = "POSSIBLE MATCH" if margin >= 0.025 else "REVIEW REQUIRED"
    r = best[2]
    reason = "Kemiripan tag + Area" if pprefix == _tm_tag_parts(_tm_norm_tag(r.get("Tag No", "")))[0] else "Kemiripan tag + Area + parameter"
    return {
        "status": status, "candidate_tag": str(r.get("Tag No", "")),
        "score": float(min(1.0, best[0])), "margin": float(margin), "reason": reason,
        "candidate": r,
    }


def _tm_equipment_candidates_from_master(plc_tag, master):
    """Suggest equipment from existing engineering Tag Master / equipment codes.

    This is a suggestion layer only. It never auto-confirms a mapping. The
    objective is to rescue PLC tags that are absent from Instrument Master but
    already carry a useful equipment identity in the engineering master.
    """
    if master is None or not hasattr(master, "columns") or master.empty:
        return []
    t = _tm_norm_tag(plc_tag)
    _, area, suffix = _tm_tag_parts(t)
    if not area:
        return []
    # Extract an equipment family + numeric sequence from the tag suffix.
    # Examples: TK024 -> TK + 24, ML02A -> ML + 2 (A is channel suffix).
    m = re.match(r"^([A-Z]{1,5})(\d+)", suffix)
    if not m:
        return []
    family = m.group(1)
    number = int(m.group(2))
    candidates = []
    for _, r in master.iterrows():
        code = str(r.get("Equipment Code", "") or "").strip()
        name = str(r.get("Equipment", "") or "").strip()
        if not code:
            continue
        c = _tm_norm_tag(code)
        cm = re.match(r"^(\d{3})([A-Z]{1,5})(\d+)$", c)
        if not cm:
            continue
        carea, cfam, cnum = cm.group(1), cm.group(2), int(cm.group(3))
        if carea != area or cfam != family or cnum != number:
            continue
        candidates.append((code, name, str(r.get("Area", area) or area).strip()))
    # unique equipment candidates
    seen, out = set(), []
    for x in candidates:
        if x[0] not in seen:
            seen.add(x[0]); out.append(x)
    return out


def _tm_current_master_candidate(plc_tag, master):
    """Return the existing Tag Master equipment assignment when available."""
    if master is None or not hasattr(master, "columns") or master.empty or "PLC Tag" not in master.columns:
        return None
    key = _tm_norm_tag(plc_tag)
    hits = master[master["PLC Tag"].astype(str).map(_tm_norm_tag) == key].copy()
    if hits.empty:
        return None
    for _, r in hits.iterrows():
        code = str(r.get("Equipment Code", "") or "").strip()
        name = str(r.get("Equipment", "") or "").strip()
        if code:
            return {"code": code, "name": name, "area": str(r.get("Area", "") or "").strip()}
    return None


def _tm_mapping_candidate(plc_tag, master, instrument_master, identification_item):
    """Build a practical equipment candidate for Mapping Review.

    Priority: Instrument Master candidate -> current Tag Master assignment ->
    Equipment Code pattern. All are suggestions until an engineer confirms.
    """
    item = identification_item or {}
    candidate_tag = str(item.get("Candidate Tag", "") or "").strip()
    if candidate_tag and instrument_master is not None and not instrument_master.empty:
        hits = instrument_master[instrument_master["Tag No"].astype(str).map(_tm_norm_tag) == _tm_norm_tag(candidate_tag)].copy()
        if not hits.empty:
            r = hits.iloc[0]
            return {
                "code": str(r.get("Derived Equipment Code", "") or "").strip(),
                "name": str(r.get("Service", "") or "").strip(),
                "area": str(r.get("Area", "") or "").strip(),
                "source": "Instrument Master",
                "confidence": float(item.get("Score", 0) or 0),
                "evidence": str(item.get("Reason", "") or "Instrument Master candidate"),
            }
    current = _tm_current_master_candidate(plc_tag, master)
    if current:
        return {**current, "source": "Tag Master", "confidence": 0.88,
                "evidence": "Equipment sudah tercatat di Tag Master"}
    pattern = _tm_equipment_candidates_from_master(plc_tag, master)
    if len(pattern) == 1:
        code, name, area = pattern[0]
        return {"code": code, "name": name, "area": area, "source": "Equipment Master + Tag Pattern",
                "confidence": 0.86, "evidence": "Area + equipment family + equipment number konsisten"}
    return None


def _tm_equipment_candidate_options(plc_tag, master):
    """Return candidate equipment list for manual selection, ranked by tag pattern."""
    rows = _tm_equipment_candidates_from_master(plc_tag, master)
    return rows

def build_tag_identification_report(plc_history, instrument_master):
    """Create engineer-reviewable identification status for every PLC historian tag."""
    if plc_history is None or not hasattr(plc_history, "columns"):
        return pd.DataFrame(columns=["PLC Tag","Identification Status","Candidate Tag","Score","Reason"])
    plc_tags = [str(c).strip() for c in plc_history.columns if str(c).strip() and str(c).strip().lower() != "archivetime"]
    if instrument_master is None or instrument_master.empty:
        return pd.DataFrame({"PLC Tag": plc_tags, "Identification Status": ["NOT FOUND"]*len(plc_tags), "Candidate Tag":"", "Score":0.0, "Reason":"Instrument Master belum tersedia"})
    im_keys = {}
    for _, r in instrument_master.iterrows():
        k = _tm_norm_tag(r.get("Tag No", ""))
        if k:
            im_keys.setdefault(k, []).append(r)
    rows = []
    for tag in plc_tags:
        key = _tm_norm_tag(tag)
        exact_rows = im_keys.get(key, [])
        if len(exact_rows) == 1:
            rows.append({"PLC Tag":tag,"Identification Status":"EXACT MATCH","Candidate Tag":str(exact_rows[0].get("Tag No","")),"Score":1.0,"Reason":"Normalized Tag No sama persis"})
        elif len(exact_rows) > 1:
            rows.append({"PLC Tag":tag,"Identification Status":"REVIEW REQUIRED","Candidate Tag":"; ".join(str(x.get("Tag No","")) for x in exact_rows),"Score":1.0,"Reason":"Duplicate Tag No di Instrument Master"})
        else:
            cand = _tm_possible_match(tag, instrument_master)
            if cand:
                rows.append({"PLC Tag":tag,"Identification Status":cand["status"],"Candidate Tag":cand["candidate_tag"],"Score":cand["score"],"Reason":cand["reason"]})
            else:
                rows.append({"PLC Tag":tag,"Identification Status":"NOT FOUND","Candidate Tag":"","Score":0.0,"Reason":"Tidak ada candidate yang cukup kuat untuk disarankan"})
    return pd.DataFrame(rows)


def enrich_tag_master_with_instruments(master, instrument_master):
    """Attach Instrument Master evidence while preserving source mapping values."""
    out = master.copy()
    new_cols = [
        "Instrument Master Match", "Instrument Service", "Instrument Type Master",
        "Instrument IO Type", "Instrument Unit Master", "Instrument Engineering Category",
        "Instrument Equipment Code", "Instrument Master Parameter", "Instrument Master Source",
        "Identification Score", "Identification Candidate", "Identification Reason",
        "Metadata Validation", "Metadata Validation Detail"
    ]
    if instrument_master is None or instrument_master.empty:
        for c in new_cols: out[c] = ""
        return out

    im = instrument_master.copy()
    im["_key"] = im.get("Normalized Tag", im.get("Tag No", "")).map(_tm_norm_tag)
    im = im[im["_key"].ne("")].copy()
    # Build an identification report from the PLC tags already present in the tag master.
    plc_tags = [str(x).strip() for x in out.get("PLC Tag", pd.Series(dtype=str)).tolist() if str(x).strip()]
    fake = pd.DataFrame(columns=plc_tags)
    report = build_tag_identification_report(fake, instrument_master)
    rmap = report.set_index("PLC Tag").to_dict("index") if not report.empty else {}
    im_first = im.drop_duplicates("_key", keep="first").set_index("_key")

    # Pandas 3 / Arrow-backed string columns reject float assignment if a new
    # column is first initialized with a string scalar.  Create explicit
    # dtypes for the enrichment columns instead.
    score_col = "Identification Score"
    for c in new_cols:
        if c == score_col:
            out[c] = pd.Series(0.0, index=out.index, dtype="float64")
        else:
            out[c] = pd.Series("", index=out.index, dtype="object")
    for idx, row in out.iterrows():
        tag = str(row.get("PLC Tag", "")).strip()
        key = _tm_norm_tag(tag)
        info = rmap.get(tag, {})
        status = info.get("Identification Status", "NOT FOUND")
        out.at[idx, "Instrument Master Match"] = status
        out.at[idx, "Identification Score"] = info.get("Score", 0.0)
        out.at[idx, "Identification Candidate"] = info.get("Candidate Tag", "")
        out.at[idx, "Identification Reason"] = info.get("Reason", "")
        candidate_key = _tm_norm_tag(info.get("Candidate Tag", "").split(";",1)[0])
        mr = im_first.loc[candidate_key] if candidate_key and candidate_key in im_first.index else None
        if mr is not None and status in {"EXACT MATCH", "POSSIBLE MATCH"}:
            for col, field in [("Instrument Service","Service"),("Instrument Type Master","Instrument Type"),("Instrument IO Type","IO Type"),("Instrument Unit Master","Unit"),("Instrument Engineering Category","Engineering Category"),("Instrument Equipment Code","Derived Equipment Code"),("Instrument Master Parameter","Suggested Parameter")]:
                out.at[idx,col] = str(mr.get(field, "") or "").strip()
            out.at[idx,"Instrument Master Source"] = "Instrument Master"
            mv, md = _tm_metadata_validation(
                row.get("Suggested Parameter", ""), row.get("Suggested Unit", ""),
                mr.get("Suggested Parameter", ""), mr.get("Unit", ""),
                row.get("Instrument Type", ""), mr.get("Instrument Type", ""),
                row.get("IO Type", ""), mr.get("IO Type", ""),
            )
            out.at[idx,"Metadata Validation"] = mv
            out.at[idx,"Metadata Validation Detail"] = md
        elif status == "REVIEW REQUIRED" and candidate_key in im_first.index:
            mr = im_first.loc[candidate_key]
            out.at[idx,"Instrument Service"] = str(mr.get("Service", "") or "").strip()
            out.at[idx,"Instrument Type Master"] = str(mr.get("Instrument Type", "") or "").strip()
            out.at[idx,"Instrument IO Type"] = str(mr.get("IO Type", "") or "").strip()
            out.at[idx,"Instrument Unit Master"] = str(mr.get("Unit", "") or "").strip()
            out.at[idx,"Instrument Engineering Category"] = str(mr.get("Engineering Category", "") or "").strip()
            out.at[idx,"Instrument Equipment Code"] = str(mr.get("Derived Equipment Code", "") or "").strip()
            out.at[idx,"Instrument Master Parameter"] = str(mr.get("Suggested Parameter", "") or "").strip()
            out.at[idx,"Metadata Validation"] = "REVIEW REQUIRED"
            out.at[idx,"Metadata Validation Detail"] = "Candidate belum cukup unik untuk automatic mapping"
        else:
            out.at[idx,"Metadata Validation"] = "NOT FOUND"
            out.at[idx,"Metadata Validation Detail"] = "Tidak ada Instrument Master mapping yang cukup kuat"

    # Only blank source fields may be enriched from an exact match.
    exact_mask = out["Instrument Master Match"].eq("EXACT MATCH")
    if "Instrument Type" in out.columns:
        mask = exact_mask & out["Instrument Type"].astype(str).str.strip().eq("")
        out.loc[mask, "Instrument Type"] = out.loc[mask, "Instrument Type Master"]
    if "Suggested Parameter" in out.columns:
        mask = exact_mask & out["Suggested Parameter"].astype(str).str.strip().eq("")
        out.loc[mask, "Suggested Parameter"] = out.loc[mask, "Instrument Master Parameter"]
    if "Suggested Unit" in out.columns:
        mask = exact_mask & out["Suggested Unit"].astype(str).str.strip().eq("")
        out.loc[mask, "Suggested Unit"] = out.loc[mask, "Instrument Unit Master"]
    return out


def instrument_master_gap_report(plc_history, instrument_master):
    """Compare PLC historian tags with Instrument Master and expose review candidates."""
    report = build_tag_identification_report(plc_history, instrument_master)
    if report.empty:
        return {"instrument_tags":set(),"plc_tags":set(),"matched":set(),"instrument_only":set(),"plc_only":set(),"duplicate_tags":pd.DataFrame(),"identification":report}
    im_tags = {_tm_norm_tag(x) for x in instrument_master.get("Tag No", pd.Series(dtype=str)).tolist() if str(x).strip()}
    plc_tags = {_tm_norm_tag(x) for x in report["PLC Tag"].tolist() if str(x).strip()}
    matched = set(report.loc[report["Identification Status"] == "EXACT MATCH", "PLC Tag"].map(_tm_norm_tag))
    candidate = set(report.loc[report["Identification Status"].isin(["POSSIBLE MATCH","REVIEW REQUIRED"]), "PLC Tag"].map(_tm_norm_tag))
    duplicate_tags = pd.DataFrame()
    if "Tag No" in instrument_master.columns:
        tmp = instrument_master.copy(); tmp["_Normalized"] = tmp["Tag No"].map(_tm_norm_tag)
        dup = tmp[tmp["_Normalized"].duplicated(keep=False) & tmp["_Normalized"].ne("")]
        if not dup.empty: duplicate_tags = dup.sort_values("_Normalized")
    return {
        "instrument_tags": im_tags, "plc_tags": plc_tags, "matched": matched,
        "instrument_only": im_tags - plc_tags, "plc_only": plc_tags - im_tags,
        "candidate": candidate, "duplicate_tags": duplicate_tags, "identification": report
    }


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


def normalize_area_label(value):
    """Normalize Area labels for display/filtering without changing equipment identity."""
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    m = re.fullmatch(r"(?:AREA\s*)?(\d+)(?:\.0+)?", text, flags=re.I)
    if m:
        return f"Area {m.group(1)}"
    return text


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



# --- Equipment Health v23: data freshness / quality helpers --------------------
EH_SITE_TZ = ZoneInfo("Asia/Makassar")  # Sumbawa / WITA

def _eh_now_local():
    return datetime.now(EH_SITE_TZ)

def _eh_freshness(ts):
    """Classify recency of the latest PLC timestamp for engineering use."""
    if pd.isna(ts):
        return {"state": "NO DATA", "class": "nodata", "hours": np.nan, "label": "No timestamp"}
    t = pd.Timestamp(ts)
    if t.tzinfo is None:
        t = t.tz_localize(EH_SITE_TZ)
    else:
        t = t.tz_convert(EH_SITE_TZ)
    now = pd.Timestamp(_eh_now_local())
    age_h = max(0.0, (now - t).total_seconds() / 3600.0)
    if age_h <= 1:
        state, cls = "LIVE", "live"
    elif age_h <= 6:
        state, cls = "RECENT", "recent"
    elif age_h <= 24:
        state, cls = "AGING", "aging"
    elif age_h <= 168:
        state, cls = "STALE", "stale"
    else:
        state, cls = "NO RECENT DATA", "nodata"
    return {"state": state, "class": cls, "hours": age_h, "label": t.strftime("%d %b %Y · %H:%M WITA")}

def _eh_parameter_quality(df, tag, min_points=20):
    """Return transparent data-quality evidence for one PLC tag.

    Data quality is separate from condition. Stale/no-data evidence is never
    presented as a Normal condition.
    """
    base = {
        "status": "MISSING TAG", "class": "bad", "valid": 0, "unique": 0,
        "latest": pd.NaT, "fresh_pct": 0.0, "label": "MISSING TAG",
        "verified": False, "flatline": False,
    }
    if tag not in df.columns or "ArchiveTime" not in df.columns:
        return base

    x = pd.DataFrame({
        "ts": pd.to_datetime(df["ArchiveTime"], errors="coerce"),
        "v": pd.to_numeric(df[tag], errors="coerce"),
    }).replace([np.inf, -np.inf], np.nan).dropna(
        subset=["ts", "v"]
    ).sort_values("ts")

    n = len(x)
    if n == 0:
        base.update({"status": "NO VALID DATA", "label": "NO VALID DATA"})
        return base

    latest = x["ts"].iloc[-1]
    freshness = _eh_freshness(latest)
    unique = int(x["v"].nunique(dropna=True))
    flatline = n >= min_points and unique <= 1

    ts_utc = pd.to_datetime(x["ts"], errors="coerce", utc=True)
    now_utc = pd.Timestamp.now(tz="UTC")
    recent_cut = now_utc - pd.Timedelta(hours=24)
    fresh_pct = float((ts_utc >= recent_cut).mean() * 100)

    if flatline:
        status, cls, label, verified = "FLATLINE", "warning", "FLATLINE — VERIFY OPERATING STATE", False
    elif n < min_points:
        status, cls, label, verified = "INSUFFICIENT", "warning", f"INSUFFICIENT DATA · {n} pts", False
    elif freshness["state"] in {"STALE", "NO RECENT DATA"}:
        status, cls, label, verified = freshness["state"], "warning", freshness["state"], False
    elif freshness["state"] == "NO DATA":
        status, cls, label, verified = "NO DATA", "bad", "NO DATA", False
    else:
        status, cls, label, verified = "VALID", "good", "VALID", True

    return {
        "status": status, "class": cls, "valid": n, "unique": unique,
        "latest": latest, "fresh_pct": fresh_pct, "label": label,
        "verified": verified, "flatline": flatline,
    }


def _eh_recommendation(row, quality, freshness_state):
    """Recommendation must reflect condition AND evidence quality."""
    if quality["status"] in {"NO VALID DATA", "MISSING TAG"} or freshness_state == "NO DATA":
        return "Data tidak tersedia — verify PLC tag, historian connection and instrument signal before assessing equipment condition."
    if quality["status"] == "INSUFFICIENT":
        return "Bangun historical evidence yang memadai sebelum intervention; verifikasi ketersediaan signal dan operating context."
    if quality["status"] == "FLATLINE":
        return "Verifikasi operating state Equipment terlebih dahulu. If the equipment should be running, verify instrument signal, pump/motor status and valve position before treating the flatline as an instrumentation issue."
    if freshness_state in {"STALE", "NO RECENT DATA"}:
        return "Refresh data PLC/historian sebelum mengambil keputusan maintenance; current equipment condition cannot be verified from stale evidence."
    if freshness_state == "AGING":
        return "Current evidence mulai usang. Recheck PLC signal sebelum intervention jika keputusan bersifat time-sensitive."
    condition = str(row.get("Condition", "Normal"))
    if condition == "Normal":
        return "Tidak diperlukan intervention. Lanjutkan routine monitoring; no abnormal deviation is detected against the current historical screening envelope."
    if condition == "Deteriorating":
        return str(row.get("Action", "Monitor the trend and verify whether deterioration persists.")) + " Konfirmasi persistence sebelum intervention."
    if condition == "Attention":
        return str(row.get("Action", "Lakukan focused engineering verification."))
    return "Lakukan engineering verification segera. Validate the signal against field condition, process state and applicable OEM/design limits before maintenance action."

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
instrument_master = load_instrument_master()
engineering_mapping = load_engineering_mapping_master()
_mapping_store_init(engineering_mapping)
master = canonicalize_equipment_master(load_master(), equipment_reference)
master = enrich_tag_master_with_instruments(master, instrument_master)
master = apply_engineering_mappings(master, st.session_state.get("engineering_mapping_master", {}))
required = ["Area", "Equipment Code", "Equipment", "Instrument Tag", "Suggested Parameter", "Suggested Unit",
            "IO Type", "Instrument Type", "Calibration Range", "Evidence", "Reference Source", "Confidence", "Mapping Status",
            "Instrument Master Match", "Instrument Service", "Instrument Type Master", "Instrument IO Type",
            "Instrument Unit Master", "Instrument Engineering Category", "Instrument Equipment Code",
            "Instrument Master Parameter", "Instrument Master Source", "Identification Score",
            "Identification Candidate", "Identification Reason", "Metadata Validation", "Metadata Validation Detail",
            "Engineering Mapping Status", "Engineering Mapping Source", "Engineering Mapping Verified By",
            "Engineering Mapping Verified Date"]
for col in required:
    if col not in master.columns:
        master[col] = ""

# Normalize only after all reference/equipment mapping is complete.
# This removes duplicate Area options such as 130 / 130.0 / Area 130.
master["Area"] = master["Area"].apply(normalize_area_label)

def _dashboard_href(nav_label, value=None):
    """Build a browser link so the entire dashboard block is clickable."""
    params = f"?opp_nav={quote(nav_label)}"
    if value:
        params += f"&opp_value={quote(str(value))}"
    return params

_dashboard_targets = {
    "⌂  Dashboard", "〽  Equipment Health", "⚠  Maintenance Priority",
    "✓  Action Center", "⌑  Tag Master", "↗  Engineering Trend", "⇧  Data Import"
}
if "opp_nav" in st.query_params:
    _qnav = str(st.query_params.get("opp_nav", ""))
    _qval = str(st.query_params.get("opp_value", "")) or None
    if _qnav in _dashboard_targets:
        st.session_state["main_navigation"] = _qnav
        if _qnav == "⚠  Maintenance Priority" and _qval:
            if _qval in {"P1", "P2", "P3", "P4"}:
                st.session_state["priority_level_v2"] = _qval
                st.session_state["priority_condition_v2"] = "All"
            else:
                st.session_state["priority_condition_v2"] = _qval
        elif _qnav == "〽  Equipment Health" and _qval:
            st.session_state["health_area"] = _qval
        st.query_params.clear()

def _navigate_dashboard(nav_label, value=None):
    """Navigate immediately and optionally prepare a destination filter."""
    st.session_state["main_navigation"] = nav_label
    if nav_label == "⚠  Maintenance Priority" and value:
        if value in {"P1", "P2", "P3", "P4"}:
            st.session_state["priority_level_v2"] = value
            st.session_state["priority_condition_v2"] = "All"
        else:
            st.session_state["priority_condition_v2"] = value
    elif nav_label == "〽  Equipment Health" and value:
        st.session_state["health_area"] = value

# ===== LEFT SIDEBAR — reference design =====

# V19 SIDEBAR — clean navigation and useful system context only.
# The non-functional Quick Filter section has been removed.
st.sidebar.markdown(
    '<div class="opp-brand-v19"><div class="opp-brand-row">'
    '<div class="brand-gear-v19">⚙</div><div>'
    '<div class="opp-brand-title-v19">OPP</div>'
    '<div class="opp-brand-sub-v19">Engineering Monitoring</div>'
    '</div></div></div>',
    unsafe_allow_html=True
)

nav_options = {
    "⌂  Dashboard": "Dashboard",
    "♧  Equipment Health": "Equipment Health",
    "⚠  Maintenance Priority": "Maintenance Priority",
    "↗  Action Center": "Action Center",
    "◆  Tag Master": "Tag Master",
    "▥  Engineering Trend": "Engineering Trend",
    "▣  Data Import": "Data Import",
}
selected_nav = st.sidebar.radio("NAVIGATION", list(nav_options.keys()), key="main_navigation")
page = nav_options[selected_nav]

# Data coverage — useful context for the historical screening engine.
_sidebar_min_dt = _sidebar_max_dt = None
_sidebar_data_days = 0
_sidebar_unique_days = 0
if not df.empty and "ArchiveTime" in df.columns:
    _sidebar_dt = pd.to_datetime(df["ArchiveTime"], errors="coerce").dropna()
    if len(_sidebar_dt):
        _sidebar_min_dt = _sidebar_dt.min()
        _sidebar_max_dt = _sidebar_dt.max()
        _sidebar_data_days = max(1, (_sidebar_max_dt.normalize() - _sidebar_min_dt.normalize()).days + 1)
        _sidebar_unique_days = _sidebar_dt.dt.normalize().nunique()
_sidebar_cov = (_sidebar_unique_days / _sidebar_data_days * 100) if _sidebar_data_days else 0

st.sidebar.markdown(
    '<div class="sidebar-divider-v19"></div>'
    '<div class="sidebar-section-title-v19">DATA COVERAGE</div>',
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    f'<div class="coverage-date-v19">'
    f'<div><span class="coverage-icon-v19">▣</span>'
    f'<b>{_sidebar_min_dt.strftime("%d %b %Y") if _sidebar_min_dt is not None else "—"}</b>'
    f'<small>First Data</small></div>'
    f'<div><span class="coverage-icon-v19">▣</span>'
    f'<b>{_sidebar_max_dt.strftime("%d %b %Y") if _sidebar_max_dt is not None else "—"}</b>'
    f'<small>Latest Data</small></div>'
    f'</div>'
    f'<div class="coverage-summary-v21">'
    f'<div class="coverage-ring-v21"><span>{_sidebar_cov:.1f}%</span></div>'
    f'<div class="coverage-copy-v21">'
    f'<div class="coverage-label-v21">Data Coverage</div>'
    f'<div class="coverage-value-v21">{_sidebar_unique_days:,} / {_sidebar_data_days:,} Days</div>'
    f'<div class="coverage-note-v21">Historical data available</div>'
    f'</div></div>',
    unsafe_allow_html=True,
)

_sidebar_last_updated = None
try:
    _sidebar_log = recent_import_log(1)
    if not _sidebar_log.empty and "Imported At" in _sidebar_log.columns:
        _sidebar_last_updated = pd.to_datetime(_sidebar_log.iloc[0]["Imported At"], errors="coerce")
except Exception:
    pass
if _sidebar_last_updated is None or pd.isna(_sidebar_last_updated):
    _sidebar_last_updated = _sidebar_max_dt

st.sidebar.markdown(
    '<div class="sidebar-divider-v19 compact"></div>'
    '<div class="sidebar-section-title-v19">SYSTEM STATUS</div>',
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    f'<div class="system-status-v19">'
    f'<div class="status-row-v19"><span class="status-dot-v19"></span><b>Connected</b>'
    f'<span class="status-live-v19">LIVE</span></div>'
    f'<div class="status-update-v19">Last updated&nbsp;&nbsp;'
    f'<b>{_sidebar_last_updated.strftime("%d %b %Y %H:%M") if _sidebar_last_updated is not None and pd.notna(_sidebar_last_updated) else "—"}</b>'
    f'</div></div>',
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    '<div class="sidebar-footer-v19"><span>OPP Engineering Monitoring</span>'
    '<span>Decision Support System</span></div>',
    unsafe_allow_html=True,
)

high = int((master["Confidence"] == "High").sum())
medium = int((master["Confidence"] == "Medium").sum())
low = int((master["Confidence"] == "Low").sum())


# -------------------------------------------------------------------------
# Equipment Health v26 — Operating Context helpers
# These helpers only use signals that actually exist in the selected
# equipment's monitored parameter set. Missing context is never guessed.
# -------------------------------------------------------------------------

def _eh_find_context_signal(health_df, role, equipment_name=""):
    """Select a context signal using role + equipment-aware scoring.

    Keyword matches are weighted by semantic specificity. Generic words such
    as 'flow', 'current' and 'pressure' receive lower weight than explicit
    phrases such as 'mill feed', 'motor current' or 'discharge pressure'.
    """
    if health_df is None or health_df.empty:
        return None

    eq = str(equipment_name).lower()
    role_terms = {
        "feed": [
            ("mill feed", 20), ("ore feed", 18), ("feed rate", 17),
            ("throughput", 14), ("process feed", 16), ("feed", 8),
            ("flow", 4), ("rate", 3),
        ],
        "load": [
            ("main motor current", 24), ("mill motor current", 24),
            ("motor current", 20), ("motor load", 18), ("motor power", 18),
            ("power", 9), ("load", 8), ("current", 4), ("torque", 7),
        ],
        "speed": [
            ("mill speed", 22), ("motor speed", 20), ("speed", 12),
            ("rpm", 12), ("frequency", 8), ("hz", 5),
        ],
        "pressure": [
            ("discharge pressure", 22), ("mill discharge pressure", 25),
            ("suction pressure", 20), ("pump discharge pressure", 23),
            ("pressure", 8),
        ],
        "temperature": [
            ("bearing temperature", 24), ("motor temperature", 22),
            ("gearbox temperature", 22), ("oil temperature", 20),
            ("temperature", 8),
        ],
        "vibration": [
            ("bearing vibration", 24), ("motor vibration", 22),
            ("vibration", 14), ("velocity", 8), ("acceleration", 6),
        ],
        "status": [
            ("run status", 24), ("running status", 24),
            ("equipment status", 24), ("motor status", 22),
            ("pump status", 22), ("run feedback", 22),
            ("run fb", 20), ("on/off", 18), ("status", 8),
        ],
    }

    # Equipment-specific semantic boosts.
    boosts = []
    if "sag mill" in eq or "ball mill" in eq or "mill" in eq:
        boosts = {
            "feed": ["mill feed", "ore feed", "feed rate"],
            "load": ["mill motor current", "main motor current", "motor current"],
            "speed": ["mill speed", "motor speed"],
            "pressure": ["mill discharge pressure"],
            "temperature": ["bearing temperature", "gearbox temperature"],
            "vibration": ["bearing vibration"],
        }.get(role, [])
    elif "pump" in eq:
        boosts = {
            "feed": ["flow", "flow rate"],
            "load": ["motor current", "motor load"],
            "speed": ["pump speed", "motor speed"],
            "pressure": ["discharge pressure", "suction pressure"],
            "temperature": ["bearing temperature", "motor temperature"],
            "vibration": ["bearing vibration", "pump vibration"],
        }.get(role, [])
    elif "crusher" in eq:
        boosts = {
            "feed": ["feed rate", "ore feed", "throughput"],
            "load": ["motor current", "motor load"],
            "speed": ["crusher speed", "motor speed"],
            "pressure": ["hydraulic pressure", "discharge pressure"],
            "temperature": ["bearing temperature"],
            "vibration": ["bearing vibration"],
        }.get(role, [])

    candidates = []
    terms = role_terms.get(role, [])
    for _, r in health_df.iterrows():
        p = str(r.get("Parameter", "")).lower()
        tag = str(r.get("PLC Tag", "")).lower()
        combined = f"{p} {tag}"
        score = 0
        matched = []
        for term, weight in terms:
            if term in p:
                score += weight
                matched.append(term)
            elif term in tag:
                score += max(1, weight // 2)
                matched.append(term + " [tag]")

        for boost in boosts:
            if boost in combined:
                score += 8

        # Avoid treating a parameter as context solely because it shares the
        # same broad keyword with another role.
        if score > 0:
            candidates.append((score, len(matched), r))

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: (-x[0], -x[1], str(x[2].get("Parameter", "")))
    )
    return candidates[0][2]


def _eh_context_value(row, stale=False):
    """Display current value or explicitly mark it as last-valid evidence."""
    if row is None:
        return "NOT AVAILABLE"
    try:
        value = float(row.get("Current", np.nan))
        if not np.isfinite(value):
            return "NOT AVAILABLE"
        unit = str(row.get("Unit", "") or "")
        prefix = "LAST VALID · " if stale else ""
        return f"{prefix}{value:,.3f} {unit}".strip()
    except Exception:
        return "NOT AVAILABLE"


def _eh_context_operating_state(health_df, equipment_name=""):
    """Infer state only from an explicit status/run-feedback signal."""
    row = _eh_find_context_signal(health_df, "status", equipment_name)
    if row is None:
        return "NOT VERIFIED", "No explicit run/status signal in monitored tags"
    try:
        value = float(row.get("Current", np.nan))
        if not np.isfinite(value):
            return "NOT VERIFIED", f'{row.get("Parameter", "Status")} has no valid value'
        if value > 0.5:
            return "RUNNING", f'{row.get("Parameter", "Status")} = {value:g}'
        return "STOPPED / OFF", f'{row.get("Parameter", "Status")} = {value:g}'
    except Exception:
        return "NOT VERIFIED", f'{row.get("Parameter", "Status")} could not be interpreted'


def _eh_context_card(title, value, subtitle, cls="neutral"):
    title_u = str(title).upper()
    icon_map = {
        "OPERATING STATE": "⚙️",
        "MILL FEED / PROCESS FEED": "⛏️",
        "MAIN MOTOR LOAD": "⚡",
        "MILL SPEED": "🌀",
        "DISCHARGE PRESSURE": "💧",
        "PRESSURE": "💧",
        "CRITICALITY EQUIPMENT": "🎯",
        "HISTORICAL FINDINGS": "🔎",
        "ACTION TERBUKA": "🛠️",
        "RIWAYAT MAINTENANCE": "📋",
    }
    icon = next((v for k, v in icon_map.items() if k in title_u), "●")
    return (
        f'<div class="eh26-context-card {cls}">'
        f'<div class="eh26-context-top"><span class="eh26-context-icon">{icon}</span>'
        f'<div class="eh26-context-label">{title}</div></div>'
        f'<div class="eh26-context-value">{value}</div>'
        f'<div class="eh26-context-sub">{subtitle}</div>'
        f'</div>'
    )



# -------------------------------------------------------------------------
# Equipment Health v29 — Engineering Diagnosis / Root Cause Assist
# -------------------------------------------------------------------------
# This is a differential-diagnosis assistant, NOT an automatic root-cause
# predictor. It ranks plausible mechanisms from available signal evidence and
# explicitly asks for field/process verification before intervention.
# -------------------------------------------------------------------------
EH29_RULES = [
    {
        "id": "MECH_BEARING",
        "title": "Bearing / rotating mechanical condition",
        "families": {"vibration", "temperature"},
        "keywords": ["bearing", "lubric", "alignment", "looseness"],
        "checks": [
            "Check bearing vibration and temperature at the affected bearing location.",
            "Verify lubrication quantity, condition and lubrication interval.",
            "Inspect coupling/alignment and signs of mechanical looseness.",
            "Compare drive-end and non-drive-end behaviour where measurements exist.",
        ],
        "caution": "Do not attribute high temperature or vibration to bearing damage without confirming operating load, lubrication and field condition.",
    },
    {
        "id": "MECH_LOAD",
        "title": "Mechanical load / resistance increase",
        "families": {"load", "vibration", "speed"},
        "keywords": ["load", "resistance", "friction", "material", "blockage"],
        "checks": [
            "Verify motor current/load against normal operating demand.",
            "Check for mechanical resistance, rubbing, blockage or abnormal material loading.",
            "Compare speed feedback with commanded/required speed.",
            "Inspect drive train, coupling and rotating clearances if the load remains elevated.",
        ],
        "caution": "High current alone does not prove a mechanical fault; process loading and operating setpoint must be checked first.",
    },
    {
        "id": "FLOW_RESTRICTION",
        "title": "Flow restriction / valve / downstream resistance",
        "families": {"flow", "pressure"},
        "keywords": ["restriction", "valve", "line", "blockage"],
        "checks": [
            "Verify upstream and downstream pressure against the process operating point.",
            "Check valve position/feedback and confirm the valve is responding to command.",
            "Inspect line, strainer, screen or downstream path for restriction.",
            "Confirm the process demand and whether the equipment is actually required to deliver flow.",
        ],
        "caution": "A low/high flow pattern must be interpreted together with pressure and process demand.",
    },
    {
        "id": "PUMP_PERFORMANCE",
        "title": "Pump / hydraulic performance",
        "families": {"flow", "pressure", "load"},
        "keywords": ["pump", "cavitation", "suction", "discharge", "impeller"],
        "checks": [
            "Verify suction condition and discharge pressure at the operating point.",
            "Check pump flow against the applicable pump curve and process demand.",
            "Inspect valve lineup, suction restriction and possible air ingress.",
            "If indicated by the process, inspect for cavitation, impeller wear or recirculation.",
        ],
        "caution": "Use the pump curve and actual process conditions before concluding pump degradation.",
    },
    {
        "id": "DRIVE_CONTROL",
        "title": "Drive / speed-control / instrumentation issue",
        "families": {"speed", "load", "flow"},
        "keywords": ["drive", "feedback", "setpoint", "instrument"],
        "checks": [
            "Compare command/setpoint with actual feedback where both are available.",
            "Verify VSD/drive alarms, permissives and operating mode.",
            "Check instrument health, calibration status and signal wiring/communication.",
            "Confirm that the process demand is consistent with the commanded operating point.",
        ],
        "caution": "A speed or flow deviation may originate in the process, drive or measurement chain.",
    },
    {
        "id": "THERMAL",
        "title": "Thermal / cooling / lubrication condition",
        "families": {"temperature", "load"},
        "keywords": ["cooling", "lubrication", "ambient", "heat"],
        "checks": [
            "Verify temperature against load and ambient/process conditions.",
            "Check cooling fan, cooling water/air and heat-transfer path where applicable.",
            "Verify lubrication condition and correct lubricant for the component.",
            "Confirm that the temperature sensor is healthy and physically representative.",
        ],
        "caution": "Temperature must be interpreted against load and ambient/process conditions, not as an isolated threshold.",
    },
    {
        "id": "INSTRUMENTATION",
        "title": "Instrumentation / signal-quality issue",
        "families": {"flatline", "quality"},
        "keywords": ["flatline", "stale", "signal", "instrument", "communication"],
        "checks": [
            "Verify PLC tag update rate and historian timestamp freshness.",
            "Compare the signal with local indication or a secondary measurement where available.",
            "Check transmitter power, wiring, communication and calibration status.",
            "Confirm equipment operating state before interpreting a zero/constant signal.",
        ],
        "caution": "Signal-quality evidence can invalidate an otherwise plausible equipment diagnosis.",
    },
]


def _eh29_family(parameter="", tag=""):
    """Classify a signal into an engineering parameter family."""
    s=f"{parameter} {tag}".upper()
    if any(k in s for k in ["VIBRATION","VIB","VELOCITY","ACCEL"]):
        return "vibration"
    if any(k in s for k in ["TEMPERATURE","TEMP","TIT"]):
        return "temperature"
    if any(k in s for k in ["CURRENT","AMP","AMPERE","POWER","PWR","LOAD","TORQUE","IIT"]):
        return "load"
    if any(k in s for k in ["SPEED","RPM","VSD","FREQUENCY","HZ"]):
        return "speed"
    if any(k in s for k in ["PRESSURE","PRESS","PIT"]):
        return "pressure"
    if any(k in s for k in ["FLOW","FLOWMETER","FIT","FQI","RATE","FEED"]):
        return "flow"
    return "other"


def _eh29_direction_value(row):
    d=str(row.get("Direction","Stable"))
    return 1 if d=="Increasing" else -1 if d=="Decreasing" else 0


def _eh29_evidence_reason(row, dx_id, relation):
    """Return a concise engineering explanation for one evidence row.

    relation is one of SUPPORTING / CONTRADICTING / CONTEXT. The wording is
    intentionally evidence-based: it describes the observed screening pattern
    and does not claim a confirmed failure mechanism.
    """
    p=str(row.get("Parameter","Signal"))
    cond=str(row.get("Condition","Normal"))
    direction=str(row.get("Direction","Stable"))
    shift=float(row.get("Shift %",0.0) or 0.0)
    dev=float(row.get("Deviation Sigma",0.0) or 0.0)
    side=str(row.get("Deviation Side","Within baseline"))
    outside=float(row.get("Outside Fraction",0.0) or 0.0)*100.0

    if relation=="SUPPORTING":
        if dev>0:
            side_txt="di bawah" if side=="Below baseline" else "di atas" if side=="Above baseline" else "di luar"
            return f"{p} berada {side_txt} historical envelope ({dev:.2f}σ; outside {outside:.0f}%)."
        if direction!="Stable" and abs(shift)>=5:
            return f"{p} menunjukkan trend {direction.lower()} dengan recent shift {shift:+.1f}%."
        return f"{p} memberikan context yang konsisten dengan hipotesis {dx_id.replace('_',' ').lower()}."

    if relation=="CONTRADICTING":
        if cond=="Normal" and direction=="Stable":
            return f"{p} masih Normal dan Stable; pola pendukung untuk hipotesis belum terlihat pada signal ini."
        if cond=="Normal":
            return f"{p} masih dalam historical envelope meskipun terdapat shift {shift:+.1f}%; evidence terhadap hipotesis masih lemah."
        return f"{p} tidak menunjukkan pola yang diharapkan untuk hipotesis ini."

    if dev>0:
        return f"{p} memiliki historical deviation {dev:.2f}σ; gunakan sebagai context, bukan bukti sebab-akibat."
    return f"{p} memberikan operating context tambahan; belum cukup untuk mengonfirmasi mekanisme."


def _eh32_equipment_role(equipment_name="", equipment_code=""):
    """Return a conservative equipment role from explicit equipment naming.

    This is a semantic routing aid, not an equipment master replacement.
    Unknown equipment remains 'generic' rather than being guessed.
    """
    txt = f"{equipment_name} {equipment_code}".upper()
    if any(k in txt for k in ["PUMP", "PMP"]):
        return "pump"
    if any(k in txt for k in ["SAG MILL", "BALL MILL", "MILL"]):
        return "mill"
    if any(k in txt for k in ["CRUSHER", "JAW", "CONE CRUSH"]):
        return "crusher"
    if any(k in txt for k in ["CONVEYOR", "CV-", "BELT"]):
        return "conveyor"
    if any(k in txt for k in ["THICKENER"]):
        return "thickener"
    if any(k in txt for k in ["FILTER PRESS", "FILTERPRESS"]):
        return "filter_press"
    if any(k in txt for k in ["COMPRESSOR"]):
        return "compressor"
    if any(k in txt for k in ["FAN", "BLOWER"]):
        return "fan"
    return "generic"


def _eh32_signal_role(parameter="", tag="", equipment_role="generic"):
    """Map a signal to an engineering role without assuming service from
    generic words alone. The original parameter family remains authoritative.
    """
    p = str(parameter or "").upper()
    t = str(tag or "").upper()
    fam = _eh29_family(parameter, tag)

    service = "other"
    if "PROCESS WATER" in p or "WATER" in p:
        service = "process_water"
    elif any(k in p for k in ["ORE FEED", "MILL FEED", "FEED RATE", "ORE"]):
        service = "ore_feed"
    elif "SLURRY" in p:
        service = "slurry"
    elif "DISCHARGE" in p and fam == "pressure":
        service = "discharge_pressure"
    elif "SUCTION" in p and fam == "pressure":
        service = "suction_pressure"

    return {"family": fam, "service": service}


def _eh32_diagnosis_factor(dx_id, equipment_role):
    """Conservative equipment-role weighting for diagnosis ranking."""
    factors = {
        "mill": {
            "MECH_BEARING": 1.15, "MECH_LOAD": 1.20, "FLOW_RESTRICTION": 0.90,
            "PUMP_PERFORMANCE": 0.45, "DRIVE_CONTROL": 1.10,
            "THERMAL": 1.05, "INSTRUMENTATION": 1.00,
        },
        "pump": {
            "MECH_BEARING": 1.05, "MECH_LOAD": 0.95, "FLOW_RESTRICTION": 1.15,
            "PUMP_PERFORMANCE": 1.35, "DRIVE_CONTROL": 1.10,
            "THERMAL": 1.00, "INSTRUMENTATION": 1.00,
        },
        "crusher": {
            "MECH_BEARING": 1.15, "MECH_LOAD": 1.25, "FLOW_RESTRICTION": 0.95,
            "PUMP_PERFORMANCE": 0.40, "DRIVE_CONTROL": 1.05,
            "THERMAL": 1.00, "INSTRUMENTATION": 1.00,
        },
        "conveyor": {
            "MECH_BEARING": 1.15, "MECH_LOAD": 1.20, "FLOW_RESTRICTION": 0.55,
            "PUMP_PERFORMANCE": 0.30, "DRIVE_CONTROL": 1.15,
            "THERMAL": 1.00, "INSTRUMENTATION": 1.00,
        },
        "filter_press": {
            "MECH_BEARING": 1.00, "MECH_LOAD": 1.10, "FLOW_RESTRICTION": 1.00,
            "PUMP_PERFORMANCE": 0.70, "DRIVE_CONTROL": 1.00,
            "THERMAL": 0.90, "INSTRUMENTATION": 1.00,
        },
    }
    return factors.get(equipment_role, {}).get(dx_id, 1.0)


def _eh32_is_meaningful_abnormal(rec):
    """A signal is abnormal only when the existing screening says so.

    Deviation alone is not enough: small positive sigma inside a historical
    envelope must not become 'supporting evidence'.
    """
    return str(rec.get("Condition", "Normal")) in {"Critical", "Attention", "Deteriorating"}


def _eh32_trend_support(rec, minimum_shift=5.0):
    direction = str(rec.get("Direction", "Stable"))
    shift = float(rec.get("Shift %", 0.0) or 0.0)
    return direction != "Stable" and abs(shift) >= minimum_shift


def _eh32_build_evidence(health, df, diagnosis, quality_map=None,
                         freshness_state="VERIFIED", equipment_name="",
                         equipment_code=""):
    """Build strict evidence classes for a diagnostic hypothesis.

    Supporting evidence must contain an observed abnormal pattern that is
    mechanically/process-relevant to the hypothesis. Relevant-but-normal
    signals are context, not support. Contradicting evidence is used only
    when the signal provides a meaningful counter-pattern.

    If the equipment evidence is stale, the result is explicitly historical
    and the strength is capped so it cannot be presented as current evidence.
    """
    empty = {"supporting": [], "contradicting": [], "context": [],
             "strength": "LOW", "current_verifiable": False}
    if health is None or health.empty:
        return empty

    dx_id = diagnosis.get("id", "")
    fams = next((r["families"] for r in EH29_RULES if r["id"] == dx_id), set())
    eq_role = _eh32_equipment_role(equipment_name, equipment_code)
    stale = freshness_state in {"STALE", "NO RECENT DATA", "NO DATA"}

    rows = []
    for _, rr in health.iterrows():
        fam = _eh29_family(rr.get("Parameter", ""), rr.get("PLC Tag", ""))
        if dx_id != "INSTRUMENTATION" and fam not in fams:
            continue
        q = (quality_map or {}).get(str(rr.get("PLC Tag", "")), {})
        rec = dict(rr)
        rec["Family"] = fam
        rec["SignalRole"] = _eh32_signal_role(
            rr.get("Parameter", ""), rr.get("PLC Tag", ""), eq_role
        )
        rec["Quality Label"] = q.get("label", q.get("status", "UNKNOWN"))
        rec["Verified"] = bool(q.get("verified", False)) and not stale
        rec["Timestamp"] = q.get("latest", pd.NaT)
        rows.append(rec)

    supporting, contradicting, context = [], [], []

    def add(rec, relation, reason, strength=1):
        item = {
            "Parameter": str(rec.get("Parameter", "Signal")),
            "Tag": str(rec.get("PLC Tag", "")),
            "Current": float(rec.get("Current", 0.0) or 0.0),
            "Unit": str(rec.get("Unit", "")),
            "Condition": str(rec.get("Condition", "Normal")),
            "Direction": str(rec.get("Direction", "Stable")),
            "Shift": float(rec.get("Shift %", 0.0) or 0.0),
            "Deviation": float(rec.get("Deviation Sigma", 0.0) or 0.0),
            "Outside": float(rec.get("Outside Fraction", 0.0) or 0.0) * 100.0,
            "Quality": str(rec.get("Quality Label", "UNKNOWN")),
            "Verified": bool(rec.get("Verified", False)),
            "Timestamp": rec.get("Timestamp", pd.NaT),
            "Reason": reason,
            "Strength": strength,
            "Service": rec.get("SignalRole", {}).get("service", "other"),
        }
        target = {
            "SUPPORTING": supporting,
            "CONTRADICTING": contradicting,
            "CONTEXT": context,
        }.get(relation)
        if target is not None:
            target.append(item)

    abnormal = {"Critical", "Attention", "Deteriorating"}

    for rec in rows:
        fam = rec["Family"]
        cond = str(rec.get("Condition", "Normal"))
        direction = str(rec.get("Direction", "Stable"))
        shift = float(rec.get("Shift %", 0.0) or 0.0)
        abnormal_now = cond in abnormal
        trend_now = _eh32_trend_support(rec)
        service = rec.get("SignalRole", {}).get("service", "other")

        rel = "CONTEXT"
        strength = 1

        if dx_id == "PUMP_PERFORMANCE":
            # Pump performance is strong only for actual pump equipment.
            role_penalty = eq_role not in {"pump"}
            if role_penalty and eq_role in {"mill", "crusher", "conveyor"}:
                rel = "CONTEXT"
            elif fam == "flow" and abnormal_now:
                rel, strength = "SUPPORTING", 3
            elif fam == "pressure" and abnormal_now and (
                str(rec.get("Deviation Side")) == "Above baseline"
                or direction == "Increasing"
            ):
                rel, strength = "SUPPORTING", 3
            elif fam == "load" and trend_now and shift >= 5:
                rel, strength = "SUPPORTING", 2
            elif fam in {"flow", "pressure", "load"} and abnormal_now:
                rel, strength = "CONTEXT", 1
            else:
                rel = "CONTEXT"

        elif dx_id == "FLOW_RESTRICTION":
            if fam == "flow" and abnormal_now and (
                str(rec.get("Deviation Side")) == "Below baseline"
                or direction == "Decreasing"
            ):
                rel, strength = "SUPPORTING", 3
            elif fam == "pressure" and abnormal_now and (
                str(rec.get("Deviation Side")) == "Above baseline"
                or direction == "Increasing"
            ):
                rel, strength = "SUPPORTING", 3
            elif fam in {"flow", "pressure"} and abnormal_now:
                rel, strength = "CONTEXT", 1
            elif fam in {"flow", "pressure"} and cond == "Normal" and direction == "Stable":
                rel, strength = "CONTEXT", 1

        elif dx_id == "MECH_BEARING":
            if fam in {"vibration", "temperature"} and abnormal_now:
                rel, strength = "SUPPORTING", 3
            elif fam in {"vibration", "temperature"} and trend_now:
                rel, strength = "SUPPORTING", 2
            else:
                rel = "CONTEXT"

        elif dx_id == "MECH_LOAD":
            if fam == "load" and trend_now and shift >= 5:
                rel, strength = "SUPPORTING", 3
            elif fam == "vibration" and trend_now and shift >= 5:
                rel, strength = "SUPPORTING", 2
            elif fam == "speed" and trend_now and shift <= -5:
                rel, strength = "SUPPORTING", 2
            else:
                rel = "CONTEXT"

        elif dx_id == "DRIVE_CONTROL":
            if fam == "speed" and (abnormal_now or trend_now):
                rel, strength = "SUPPORTING", 3
            elif fam in {"load", "flow"} and (abnormal_now or trend_now):
                rel, strength = "SUPPORTING", 2
            else:
                rel = "CONTEXT"

        elif dx_id == "THERMAL":
            if fam == "temperature" and abnormal_now:
                rel, strength = "SUPPORTING", 3
            elif fam == "temperature" and trend_now:
                rel, strength = "SUPPORTING", 2
            elif fam == "load" and trend_now and shift >= 5:
                rel, strength = "SUPPORTING", 2
            else:
                rel = "CONTEXT"

        elif dx_id == "INSTRUMENTATION":
            qlabel = str(rec.get("Quality Label", "UNKNOWN")).upper()
            if qlabel in {
                "STALE", "NO RECENT DATA", "NO VALID DATA", "MISSING TAG",
                "FLATLINE", "INSUFFICIENT"
            } or not rec.get("Verified", False):
                rel, strength = "SUPPORTING", 3
            else:
                rel = "CONTEXT"

        add(rec, rel, _eh29_evidence_reason(rec, dx_id, rel), strength)

    # Hydraulic paired-pattern enhancement is only valid when the signal
    # directions actually form low-flow/high-pressure behaviour.
    if dx_id in {"PUMP_PERFORMANCE", "FLOW_RESTRICTION"}:
        low_flow = any(
            r["Family"] == "flow" and
            _eh32_is_meaningful_abnormal(r) and
            (
                str(r.get("Deviation Side")) == "Below baseline"
                or str(r.get("Direction")) == "Decreasing"
            )
            for r in rows
        )
        high_pressure = any(
            r["Family"] == "pressure" and
            _eh32_is_meaningful_abnormal(r) and
            (
                str(r.get("Deviation Side")) == "Above baseline"
                or str(r.get("Direction")) == "Increasing"
            )
            for r in rows
        )
        if low_flow and high_pressure:
            for r in supporting:
                if r["Family"] in {"flow", "pressure"}:
                    r["Reason"] = "Pola low-flow / high-pressure mendukung investigasi hydraulic resistance."
                    r["Strength"] = max(r["Strength"], 3)

    # Contradicting evidence should be rare and meaningful. For hydraulic
    # hypotheses, an explicitly abnormal counter-pattern is stronger than a
    # normal signal. Normal/stable signals stay in context.
    if dx_id == "PUMP_PERFORMANCE":
        if not any(x["Family"] == "pressure" for x in supporting):
            for r in rows:
                if r["Family"] == "pressure" and _eh32_is_meaningful_abnormal(r):
                    add(
                        r, "CONTEXT",
                        "Pressure menunjukkan kondisi abnormal, tetapi pola ini belum cukup spesifik untuk pump performance.",
                        1,
                    )

    # Unique evidence rows by tag, keeping the strongest relation.
    def dedupe(items):
        best = {}
        for x in items:
            key = x["Tag"] or x["Parameter"]
            if key not in best or x["Strength"] > best[key]["Strength"]:
                best[key] = x
        return list(best.values())

    supporting = dedupe(supporting)
    contradicting = dedupe(contradicting)
    context = dedupe(context)

    supporting.sort(key=lambda x: (-x["Strength"], -abs(x["Deviation"]), -abs(x["Shift"])))
    contradicting.sort(key=lambda x: (-x["Strength"], -abs(x["Deviation"]), -abs(x["Shift"])))
    context.sort(key=lambda x: (-abs(x["Deviation"]), -abs(x["Shift"])))

    supporting = supporting[:5]
    contradicting = contradicting[:4]
    context = context[:4]

    score = sum(x["Strength"] for x in supporting)
    oppose = sum(x["Strength"] for x in contradicting)

    if stale:
        # Never represent stale evidence as current STRONG/MODERATE evidence.
        if score >= 4:
            strength = "HISTORICAL"
        elif score > 0:
            strength = "HISTORICAL-WEAK"
        else:
            strength = "NOT VERIFIABLE"
    else:
        if score >= 7 and score > oppose + 2:
            strength = "STRONG"
        elif score >= 4 and score >= oppose:
            strength = "MODERATE"
        elif score > 0:
            strength = "WEAK"
        else:
            strength = "LOW"

    return {
        "supporting": supporting,
        "contradicting": contradicting,
        "context": context,
        "strength": strength,
        "current_verifiable": not stale,
    }


def _eh29_build_context(health):
    ctx={}
    for _,r in health.iterrows():
        fam=_eh29_family(r.get("Parameter",""),r.get("PLC Tag",""))
        ctx.setdefault(fam,[]).append(r)
    return ctx


def _eh29_rank_diagnoses(health, quality_gate=False, parameter_quality_gate=False,
                          equipment_name="", equipment_code=""):
    """Rank differential mechanisms from available evidence.

    Scores are evidence-ranking scores, not probabilities. Equipment-aware
    weighting prevents generic flow/pressure signals from making a pump
    diagnosis dominate a mill/crusher/conveyor without a service relationship.
    """
    if health is None or health.empty:
        return []

    ctx = _eh29_build_context(health)
    bad = health[health["Condition"].isin(["Critical", "Attention", "Deteriorating"])].copy()
    abnormal_fams = set(
        _eh29_family(r.get("Parameter", ""), r.get("PLC Tag", ""))
        for _, r in bad.iterrows()
    )
    eq_role = _eh32_equipment_role(equipment_name, equipment_code)

    flatline_n = 0
    for _, r in health.iterrows():
        tag = str(r.get("PLC Tag", ""))
        q = _eh_parameter_quality(df, tag) if "df" in globals() else {}
        if q.get("flatline", False) or q.get("status") in {
            "STALE", "NO RECENT DATA", "NO VALID DATA", "MISSING TAG"
        }:
            flatline_n += 1

    results = []
    for rule in EH29_RULES:
        dx_id = rule["id"]
        score = 0.0
        evidence = []
        families = rule["families"]

        present = families & set(ctx.keys())
        abnormal = families & abnormal_fams
        score += 18 * len(abnormal) + 5 * len(present)

        if dx_id == "MECH_BEARING" and "vibration" in ctx and "temperature" in ctx:
            if any(str(x.get("Condition")) in {"Critical", "Attention", "Deteriorating"} for x in ctx["vibration"]):
                score += 22; evidence.append("abnormal vibration signal")
            if any(str(x.get("Condition")) in {"Critical", "Attention", "Deteriorating"} for x in ctx["temperature"]):
                score += 18; evidence.append("abnormal temperature signal")

        elif dx_id == "MECH_LOAD":
            if "load" in ctx and any(_eh29_direction_value(x) > 0 and abs(float(x.get("Shift %",0) or 0)) >= 5 for x in ctx["load"]):
                score += 18; evidence.append("increasing load/current")
            if "vibration" in ctx and any(_eh29_direction_value(x) > 0 and abs(float(x.get("Shift %",0) or 0)) >= 5 for x in ctx["vibration"]):
                score += 15; evidence.append("increasing vibration")
            if "speed" in ctx and any(_eh29_direction_value(x) < 0 and abs(float(x.get("Shift %",0) or 0)) >= 5 for x in ctx["speed"]):
                score += 10; evidence.append("decreasing speed")

        elif dx_id == "FLOW_RESTRICTION":
            if "flow" in ctx and "pressure" in ctx:
                score += 8; evidence.append("flow + pressure context available")
                low_flow = any(
                    _eh32_is_meaningful_abnormal(x) and
                    (_eh29_direction_value(x) < 0 or x.get("Deviation Side") == "Below baseline")
                    for x in ctx["flow"]
                )
                high_press = any(
                    _eh32_is_meaningful_abnormal(x) and
                    (_eh29_direction_value(x) > 0 or x.get("Deviation Side") == "Above baseline")
                    for x in ctx["pressure"]
                )
                if low_flow and high_press:
                    score += 30; evidence.append("low-flow / high-pressure pattern")

        elif dx_id == "PUMP_PERFORMANCE":
            if eq_role == "pump":
                if {"flow", "pressure"}.issubset(ctx):
                    score += 22; evidence.append("pump flow + pressure context")
                if "load" in ctx:
                    score += 6; evidence.append("pump load context")
            elif eq_role in {"mill", "crusher", "conveyor"}:
                # A mill having flow/pressure signals does not make it a pump.
                score *= 0.45
                evidence.append("equipment is not identified as a pump; hydraulic signals treated as context")
            else:
                if {"flow", "pressure"}.issubset(ctx):
                    score += 10; evidence.append("flow + pressure context")

        elif dx_id == "DRIVE_CONTROL":
            if "speed" in ctx:
                score += 14; evidence.append("speed feedback available")
            if "load" in ctx:
                score += 8; evidence.append("load feedback available")
            if "flow" in ctx:
                score += 7; evidence.append("process response signal available")

        elif dx_id == "THERMAL":
            if "temperature" in ctx and any(str(x.get("Condition")) != "Normal" for x in ctx["temperature"]):
                score += 22; evidence.append("temperature deviation")
            if "load" in ctx and any(
                _eh29_direction_value(x) > 0 and abs(float(x.get("Shift %",0) or 0)) >= 5
                for x in ctx["load"]
            ):
                score += 14; evidence.append("increasing load context")

        elif dx_id == "INSTRUMENTATION":
            score += min(flatline_n * 12, 36)
            if quality_gate:
                score += 25; evidence.append("equipment data is stale/unverified")
            if parameter_quality_gate:
                score += 18; evidence.append("parameter data-quality issue")
            if flatline_n:
                evidence.append(f"{flatline_n} signal(s) require quality verification")

        score *= _eh32_diagnosis_factor(dx_id, eq_role)

        if score >= 18:
            evidence = list(dict.fromkeys(evidence))
            results.append({
                "id": dx_id,
                "title": rule["title"],
                "score": min(100, int(round(score))),
                "evidence": evidence,
                "checks": rule["checks"],
                "caution": rule["caution"],
            })

    results.sort(key=lambda x: (-x["score"], x["title"]))
    return results[:5]


def _eh29_correlation_evidence(health, df, max_pairs=5):
    """Find useful co-movement among distinct engineering signal families.

    Pairs are unique (A,B is the same as B,A), same-signal/same-family
    relationships are excluded, and ranking favors engineering-relevant
    relationships. Correlation remains supporting evidence, not causality.
    """
    if health is None or health.empty or df is None or df.empty or "ArchiveTime" not in df.columns:
        return []

    tags = [str(x) for x in health["PLC Tag"].tolist() if str(x) in df.columns]
    tags = list(dict.fromkeys(tags))
    if len(tags) < 2:
        return []

    meta = {}
    for _, r in health.iterrows():
        tag = str(r.get("PLC Tag", ""))
        meta[tag] = {
            "parameter": str(r.get("Parameter", tag)),
            "family": _eh29_family(r.get("Parameter", ""), tag),
            "condition": str(r.get("Condition", "Normal")),
            "shift": float(r.get("Shift %", 0.0) or 0.0),
            "deviation": float(r.get("Deviation Sigma", 0.0) or 0.0),
        }

    work = pd.DataFrame({"ArchiveTime": pd.to_datetime(df["ArchiveTime"], errors="coerce")})
    for tag in tags:
        work[tag] = pd.to_numeric(df[tag], errors="coerce")

    preferred = {
        frozenset({"flow", "pressure"}): 1.35,
        frozenset({"load", "vibration"}): 1.30,
        frozenset({"vibration", "temperature"}): 1.25,
        frozenset({"load", "speed"}): 1.20,
        frozenset({"flow", "load"}): 1.10,
        frozenset({"pressure", "load"}): 1.05,
        frozenset({"flow", "speed"}): 1.00,
        frozenset({"pressure", "speed"}): .95,
    }

    pairs = []
    seen_pairs = set()

    for i, a in enumerate(tags):
        fa = meta.get(a, {}).get("family", "other")
        for b in tags[i + 1:]:
            fb = meta.get(b, {}).get("family", "other")
            if a == b or fa == fb or fa == "other" or fb == "other":
                continue

            # Canonical tag pair prevents A-B / B-A duplicates even if input
            # order changes in the future.
            key = tuple(sorted((a, b)))
            if key in seen_pairs:
                continue
            seen_pairs.add(key)

            pair = work[[a, b]].dropna()
            if len(pair) < 30:
                continue
            if pair[a].nunique() < 2 or pair[b].nunique() < 2:
                continue

            corr = float(pair[a].corr(pair[b]))
            if not np.isfinite(corr) or abs(corr) < 0.70:
                continue

            pref = preferred.get(frozenset({fa, fb}), 0.85)
            abnormal_bonus = 1.0
            if meta.get(a, {}).get("condition") in {"Critical", "Attention", "Deteriorating"}:
                abnormal_bonus += .20
            if meta.get(b, {}).get("condition") in {"Critical", "Attention", "Deteriorating"}:
                abnormal_bonus += .20

            rank = abs(corr) * pref * abnormal_bonus
            pairs.append((
                rank, corr,
                meta[a]["parameter"], meta[b]["parameter"],
                a, b, len(pair), fa, fb
            ))

    pairs.sort(key=lambda x: (-x[0], -abs(x[1])))
    return pairs[:max_pairs]



if page == "Dashboard":
    # -------------------------------------------------------------------------
    # Dashboard v15 — executive engineering view.
    # IMPORTANT: all engineering calculations remain in the existing engines
    # build_equipment_screening() and build_action_findings(). This block is
    # visualisation/navigation only.
    # -------------------------------------------------------------------------
    screening = build_equipment_screening(master, df)
    findings = build_action_findings(master, df)
    if not findings.empty:
        store = ensure_action_store(findings)
        action_df = actions_dataframe(store)
        open_count = int((action_df["Status"] != "CLOSED").sum()) if not action_df.empty else 0
    else:
        action_df = pd.DataFrame()
        open_count = 0

    # Header data period — derived from actual historical ArchiveTime.
    min_dt = max_dt = None
    data_days = 0
    coverage_pct = None
    if not df.empty and "ArchiveTime" in df.columns:
        dt = pd.to_datetime(df["ArchiveTime"], errors="coerce").dropna()
        if len(dt):
            min_dt, max_dt = dt.min(), dt.max()
            data_days = max(1, (max_dt.normalize() - min_dt.normalize()).days + 1)
            unique_days = dt.dt.normalize().nunique()
            coverage_pct = unique_days / data_days * 100

    if screening.empty:
        st.markdown(
            '<div class="v15-header"><div><div class="v15-title">⚙️ OPP Engineering Monitoring Dashboard <span class="v15-live">● LIVE</span></div>'
            '<div class="v15-subtitle">Engineering decision support for plant condition, equipment health and maintenance follow-up.</div></div></div>',
            unsafe_allow_html=True,
        )
        st.warning("No equipment has sufficient historical numeric data for screening.")
    else:
        total_eq = len(screening)
        healthy = int((screening["Condition"] == "HEALTHY").sum())
        deteriorating = int((screening["Condition"] == "DETERIORATING").sum())
        attention = int((screening["Condition"] == "ATTENTION").sum())
        critical = int((screening["Condition"] == "CRITICAL").sum())
        nonhealthy = total_eq - healthy
        p1n = int((screening["Screening Priority"] == "P1").sum())
        p2n = int((screening["Screening Priority"] == "P2").sum())
        p3n = int((screening["Screening Priority"] == "P3").sum())
        p4n = int((screening["Screening Priority"] == "P4").sum())

        # Header + period controls.
        hleft, hmid, hright = st.columns([1.7, 1.0, .7], gap="medium")
        with hleft:
            st.markdown(
                '<div class="v15-header"><div class="v15-title">⚙️ OPP Engineering Monitoring Dashboard <span class="v15-live">● LIVE</span></div>'
                '<div class="v15-subtitle">Plant condition overview — identify the signal, understand the risk, then drill down only when needed.</div></div>',
                unsafe_allow_html=True,
            )
        with hmid:
            period_text = f"{min_dt.strftime('%d %b %Y')} – {max_dt.strftime('%d %b %Y')}" if min_dt is not None else "No historical period"
            st.markdown(
                f'<div class="v15-period"><div class="v15-period-label">📅 DATA PERIOD</div><div class="v15-period-value">{period_text}</div>'
                f'<div class="v15-period-small">{data_days:,} days of history</div></div>', unsafe_allow_html=True)
        with hright:
            if st.button("↻ Refresh Data", key="dash_refresh_v15", width='stretch'):
                load_history.clear()
                st.rerun()

        # Executive KPI strip.
        k1, k2, k3, k4, k5 = st.columns(5, gap="medium")
        kpi_data = [
            (k1, "#1769E0", "🔧", "SCREENED EQUIPMENT", total_eq, "Equipment with sufficient PLC history"),
            (k2, "#0A9F78", "✓", "HEALTHY EQUIPMENT", healthy, f"{healthy/max(total_eq,1)*100:.1f}% of screened"),
            (k3, "#F28C00", "⚠", "REQUIRES ATTENTION", nonhealthy, f"{nonhealthy/max(total_eq,1)*100:.1f}% outside healthy"),
            (k4, "#E63950", "●", "P1 IMMEDIATE REVIEW", p1n, "Highest screening urgency"),
            (k5, "#6246C9", "🛠", "OPEN ENGINEERING FINDINGS", open_count, "Awaiting engineering follow-up"),
        ]
        kpi_targets = [
            "〽  Equipment Health", "⚠  Maintenance Priority", "⚠  Maintenance Priority",
            "⚠  Maintenance Priority", "✓  Action Center"
        ]
        kpi_values = [None, "P4", "ATTENTION", "P1", None]
        for col, color, icon, title, value, small, target, target_value in [
            (*item, kpi_targets[i], kpi_values[i]) for i, item in enumerate(kpi_data)
        ]:
            col.markdown(
                f'<a class="v16-click" href="{_dashboard_href(target, target_value)}">'
                f'<div class="v15-kpi" style="background:{color}"><div class="v15-kpi-top"><span>{icon}</span>{title}</div>'
                f'<div class="v15-kpi-value">{value:,}</div><div class="v15-kpi-small">{small}</div><div class="v16-arrow">›</div></div></a>',
                unsafe_allow_html=True)

        # ---------------- Plant Condition + Action Center ----------------
        left, right = st.columns([1.55, 1], gap="medium")
        with left:
            with st.container(border=True, key="dash_v15_condition"):
                st.markdown('<div class="v15-panel-head">🩺 PLANT CONDITION OVERVIEW <span>• current screening state</span></div>', unsafe_allow_html=True)
                st.markdown('<div class="v15-panel-sub">Click a status below to open the relevant engineering worklist.</div>', unsafe_allow_html=True)
                # Solid stacked condition bar: simple and immediately readable.
                parts = [
                    ("#12B76A", healthy, "Healthy"), ("#F5B82E", deteriorating, "Deteriorating"),
                    ("#F79009", attention, "Attention"), ("#E63950", critical, "Critical")]
                segs = []
                for color, n, _ in parts:
                    if n:
                        segs.append(f'<div style="width:{n/max(total_eq,1)*100:.2f}%;background:{color}"></div>')
                st.markdown(f'<div class="v15-stack">{"".join(segs)}</div>', unsafe_allow_html=True)
                c1,c2,c3,c4 = st.columns(4, gap="medium")
                cards = [
                    (c1,"#12B76A","HEALTHY",healthy,"Routine condition",None),
                    (c2,"#F5B82E","DETERIORATING",deteriorating,"Watch trend", "DETERIORATING"),
                    (c3,"#F79009","ATTENTION",attention,"Engineering review", "ATTENTION"),
                    (c4,"#E63950","CRITICAL",critical,"Highest concern", "CRITICAL"),
                ]
                for col,color,label,n,desc,target in cards:
                    target_nav = "⚠  Maintenance Priority" if target else "〽  Equipment Health"
                    target_val = target if target else None
                    col.markdown(
                        f'<a class="v16-click" href="{_dashboard_href(target_nav, target_val)}">'
                        f'<div class="v15-condition"><div class="v15-dot" style="background:{color}"></div>'
                        f'<div class="v15-condition-label">{label}</div><div class="v15-condition-count">{n:,}</div>'
                        f'<div class="v15-condition-small">{n/max(total_eq,1)*100:.1f}% · {desc}</div>'
                        f'<div class="v16-arrow v16-condition-arrow">›</div></div></a>',
                        unsafe_allow_html=True)
                st.markdown(f'<div class="v15-interpret"><b>Engineering read:</b> {nonhealthy:,} of {total_eq:,} screened equipment are outside the healthy screening state. Priority attention is concentrated in P1/P2 items.</div>', unsafe_allow_html=True)

        with right:
            with st.container(border=True, key="dash_v15_actions"):
                st.markdown('<div class="v15-panel-head">🛠 ACTION CENTER <span>• engineering follow-up</span></div>', unsafe_allow_html=True)
                st.markdown(
                    f'<a class="v16-click" href="{_dashboard_href("✓  Action Center")}">'
                    f'<div class="v15-action-main" style="background:#6246C9"><div class="v15-action-number">{open_count:,}</div>'
                    f'<div><div class="v15-action-title">OPEN ENGINEERING FINDINGS</div><div class="v15-action-small">Findings awaiting investigation, action or verification.</div></div>'
                    f'<div class="v15-action-icon">☑</div><div class="v16-arrow">›</div></div></a>',
                    unsafe_allow_html=True)
                a1,a2,a3,a4 = st.columns(4, gap="medium")
                status_counts = {s:int((action_df["Status"]==s).sum()) if not action_df.empty and "Status" in action_df else 0 for s in ACTION_STATUSES}
                for col, label, n, color, icon in [
                    (a1,"OPEN",status_counts["OPEN"],"#1769E0","🔎"),(a2,"INVESTIGATION",status_counts["INVESTIGATION"],"#F28C00","🧭"),
                    (a3,"ACTION",status_counts["ACTION"],"#E63950","🔧"),(a4,"VERIFICATION",status_counts["VERIFICATION"],"#6246C9","✓")]:
                    col.markdown(f'<div class="v15-mini" style="border-top:4px solid {color}"><div>{icon} {label}</div><strong>{n:,}</strong></div>', unsafe_allow_html=True)

        st.markdown('<div class="v15-row-gap"></div>', unsafe_allow_html=True)

        # ---------------- Engineering Focus + Data Quality ----------------
        left, right = st.columns([1.55, 1], gap="medium")
        with left:
            with st.container(border=True, key="dash_v15_focus"):
                st.markdown('<div class="v15-panel-head">🎯 ENGINEERING FOCUS <span>• what should be looked at first?</span></div>', unsafe_allow_html=True)
                lead = "P1 immediate review" if p1n else "P2 planned inspection" if p2n else "routine monitoring"
                st.markdown(f'<div class="v15-focus"><b>{nonhealthy:,} equipment</b> are outside the healthy screening state. Current screening focus: <b>{lead}</b>.</div>', unsafe_allow_html=True)
                q1,q2,q3,q4 = st.columns(4, gap="medium")
                for col, p, n, desc, color in [
                    (q1,"P1",p1n,"Immediate Review","#E63950"),(q2,"P2",p2n,"Planned Inspection","#F79009"),
                    (q3,"P3",p3n,"Monitoring","#D9A514"),(q4,"P4",p4n,"Routine","#12A66F")]:
                    col.markdown(
                        f'<a class="v16-click" href="{_dashboard_href("⚠  Maintenance Priority", p)}">'
                        f'<div class="v15-priority" style="background:{color}"><div class="vp-top">● {p}</div>'
                        f'<div class="vp-count">{n:,}</div><div class="vp-desc">{desc}</div><div class="v16-arrow">›</div></div></a>',
                        unsafe_allow_html=True)

        with right:
            with st.container(border=True, key="dash_v15_quality"):
                st.markdown('<div class="v15-panel-head">📊 DATA QUALITY & COVERAGE <span>• mapping evidence</span></div>', unsafe_allow_html=True)
                d1,d2,d3,d4 = st.columns(4, gap="medium")
                for col,label,n,cls in [(d1,"PLC TAGS",len(master),"neutral"),(d2,"HIGH",high,"high"),(d3,"MEDIUM",medium,"medium"),(d4,"LOW",low,"low")]:
                    col.markdown(f'<div class="v15-dq {cls}"><div>{label}</div><strong>{n:,}</strong></div>', unsafe_allow_html=True)
                cov = f"{coverage_pct:.1f}%" if coverage_pct is not None else "—"
                st.markdown(f'<div class="v15-coverage"><div><span>Historical data coverage</span><b>{cov}</b></div><div class="v15-cover-track"><div style="width:{min(100,max(0,coverage_pct or 0)):.1f}%"></div></div><small>{data_days:,} calendar days in history • coverage is based on days containing PLC records</small></div>', unsafe_allow_html=True)
                st.markdown(
                    f'<a class="v16-panel-link" href="{_dashboard_href("⇧  Data Import")}">'
                    f'<div class="v16-linkbar">📊 Open Data Import / Coverage <b>›</b></div></a>',
                    unsafe_allow_html=True)

        st.markdown('<div class="v15-row-gap"></div>', unsafe_allow_html=True)

        # ---------------- Equipment Health Summary + Screening Overview ----------------
        left, right = st.columns([1.25, 1], gap="medium")
        with left:
            with st.container(border=True, key="dash_v15_health_summary"):
                st.markdown('<div class="v15-panel-head">🔧 EQUIPMENT HEALTH SUMMARY <span>• highest concern first</span></div>', unsafe_allow_html=True)
                view = screening.copy()
                order = {"P1":1,"P2":2,"P3":3,"P4":4}
                view["_p"] = view["Screening Priority"].map(order).fillna(9)
                view = view.sort_values(["_p","Health","Top Shift %"], ascending=[True,True,False]).head(6)
                area_map = master[["Equipment Code","Area"]].drop_duplicates("Equipment Code")
                view = view.merge(area_map,on="Equipment Code",how="left")
                rows = []
                for _,r in view.iterrows():
                    color = {"P1":"#E63950","P2":"#F79009","P3":"#D9A514","P4":"#12A66F"}.get(r["Screening Priority"],"#667085")
                    rows.append(f'<tr><td><b>{r["Equipment Code"]}</b><br><span>{str(r["Equipment"])[:28]}</span></td><td>{str(r.get("Area",""))}</td><td><b>{int(r["Health"])}%</b></td><td><span class="v15-status" style="color:{color}">{r["Condition"]}</span></td><td><b style="color:{color}">{r["Screening Priority"]}</b></td></tr>')
                table = '<table class="v15-table"><thead><tr><th>Equipment</th><th>Area</th><th>Health</th><th>Condition</th><th>Priority</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table>'
                st.markdown(table, unsafe_allow_html=True)
                st.markdown(
                    f'<a class="v16-panel-link" href="{_dashboard_href("〽  Equipment Health")}">'
                    f'<div class="v16-linkbar">🔧 Open Equipment Health <b>›</b></div></a>',
                    unsafe_allow_html=True)

        with right:
            with st.container(border=True, key="dash_v15_trend_panel"):
                st.markdown('<div class="v15-panel-head">📈 SCREENING OVERVIEW <span>• recent historical signal</span></div>', unsafe_allow_html=True)
                if not df.empty and "ArchiveTime" in df.columns:
                    tmp = df[["ArchiveTime"]].copy()
                    tmp["Date"] = pd.to_datetime(tmp["ArchiveTime"],errors="coerce").dt.normalize()
                    daily = tmp.dropna().groupby("Date").size().tail(14)
                    if len(daily):
                        chart = daily.rename("PLC Records")
                        st.line_chart(chart, height=185, width='stretch')
                        st.caption("Record volume by day — use Engineering Trend for parameter-level behaviour.")
                    else:
                        st.info("No recent historical record series available.")
                else:
                    st.info("No historical data available.")
                st.markdown(
                    f'<a class="v16-panel-link" href="{_dashboard_href("↗  Engineering Trend")}">'
                    f'<div class="v16-linkbar">📈 Open Engineering Trend <b>›</b></div></a>',
                    unsafe_allow_html=True)

        # Footer status strip.
        st.markdown(
            f'<div class="v15-footer"><span>🟢 Database / history connected</span><span><b>{len(df):,}</b> historical records</span>'
            f'<span>First data: <b>{min_dt.strftime("%d %b %Y %H:%M") if min_dt is not None else "—"}</b></span>'
            f'<span>Latest data: <b>{max_dt.strftime("%d %b %Y %H:%M") if max_dt is not None else "—"}</b></span>'
            f'<span>📌 Screening engine: <b>P05–P95 + shift + outside fraction + confidence + validated criticality</b></span></div>',
            unsafe_allow_html=True,
        )

        st.caption("Engineering screening is decision support only — not an alarm/trip limit or failure prediction. Validate abnormal signals against OEM/design limits, process condition, field inspection and engineering judgement.")

elif page == "Equipment Health":
    # -------------------------------------------------------------------------
    # Equipment Health v22 — premium engineering decision workspace.
    #
    # Engineering logic is intentionally kept on the existing screening engine:
    # baseline_condition(), infer_parameter(), parameter_action(), and the
    # equipment screening engine above. This page adds a clearer decision flow,
    # richer evidence, and direct navigation without changing the calculations.
    # -------------------------------------------------------------------------
    st.markdown(
        '<div class="eh22-header">'
        '<div><div class="eh22-title">🩺 Equipment Health</div>'
        '<div class="eh22-subtitle">Condition-based engineering workspace — identify the abnormal signal, quantify the deviation, and decide the next verification.</div></div>'
        '<div class="eh22-live">● PEMANTAUAN LANGSUNG</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    screening = build_equipment_screening(master, df)

    if screening.empty:
        st.markdown(
            '<div class="eh22-empty"><div class="eh22-empty-icon">◌</div>'
            '<b>No equipment is currently eligible for health screening</b>'
            '<span>More historical numeric PLC data is required before an equipment condition can be assessed.</span></div>',
            unsafe_allow_html=True,
        )
    else:
        # --- Equipment selector: search first, then select. -------------------
        eq_master = master[["Equipment Code", "Equipment", "Area"]].copy()
        eq_master["Equipment Code"] = eq_master["Equipment Code"].astype(str)
        eq_master["Equipment"] = eq_master["Equipment"].fillna("").astype(str)
        eq_master["Area"] = eq_master["Area"].fillna("").astype(str)
        eq_master = eq_master.drop_duplicates("Equipment Code")

        screen_codes = set(screening["Equipment Code"].astype(str))
        eq_master = eq_master[eq_master["Equipment Code"].isin(screen_codes)].copy()

        c_search, c_area, c_eq = st.columns([1.25, .8, 1.55], gap="medium")
        with c_search:
            eq_search = st.text_input(
                "Search equipment",
                placeholder="Code or equipment name…",
                key="eh22_search",
            )
        with c_area:
            eh_areas = ["All Areas"] + sorted([x for x in eq_master["Area"].unique() if x.strip()])
            eh_area = st.selectbox("Area", eh_areas, key="eh22_area")
        with c_eq:
            eq_pool = eq_master.copy()
            if eh_area != "All Areas":
                eq_pool = eq_pool[eq_pool["Area"] == eh_area]
            if eq_search.strip():
                q = eq_search.strip().lower()
                eq_pool = eq_pool[
                    eq_pool["Equipment Code"].str.lower().str.contains(q, na=False)
                    | eq_pool["Equipment"].str.lower().str.contains(q, na=False)
                ]

            eq_codes = eq_pool["Equipment Code"].tolist()
            if not eq_codes:
                st.warning("No equipment matches the current search / area.")
                eq_codes = eq_master["Equipment Code"].tolist()

            default_eq = st.session_state.get("health_selected_eq")
            if default_eq not in eq_codes:
                default_eq = eq_codes[0]

            eq_labels = {
                str(r["Equipment Code"]):
                    f'{r["Equipment Code"]}  ·  {r["Equipment"] or "Equipment description not yet mapped"}'
                for _, r in eq_pool.iterrows()
            }
            selected_eq = st.selectbox(
                "Equipment",
                eq_codes,
                index=eq_codes.index(default_eq),
                format_func=lambda x: eq_labels.get(str(x), str(x)),
                key="eh22_selected_eq",
            )
            # Keep compatibility with Dashboard/other navigation hand-offs.
            st.session_state["health_selected_eq"] = selected_eq

        ev = master[master["Equipment Code"].astype(str) == str(selected_eq)].copy()
        eq_name_series = ev["Equipment"].fillna("").astype(str).str.strip()
        eq_name = eq_name_series[eq_name_series != ""].iloc[0] if (eq_name_series != "").any() else "Equipment description not yet mapped"
        eq_area = str(ev["Area"].iloc[0]).strip() if len(ev) else "—"

        # --- Build parameter-level evidence using the existing baseline engine.
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
            parameter, unit, source = infer_parameter(
                tag,
                meta.get("Suggested Parameter", ""),
                meta.get("Suggested Unit", ""),
                meta.get("Instrument Type", ""),
            )
            rows.append({
                "PLC Tag": tag,
                "Parameter": parameter,
                "Unit": unit,
                "Parameter Source": source,
                **stats,
                "Confidence": str(meta.get("Confidence", "") or "Low"),
                "Action": parameter_action(parameter, tag),
            })

        if not rows:
            st.markdown(
                f'<div class="eh22-empty"><div class="eh22-empty-icon">⚙</div>'
                f'<b>{selected_eq} — insufficient evidence</b>'
                f'<span>No sufficient historical numeric data is available for this equipment.</span></div>',
                unsafe_allow_html=True,
            )
        else:
            health = pd.DataFrame(rows)

            # Existing condition labels are preserved exactly.
            critical = int((health["Condition"] == "Critical").sum())
            attention = int((health["Condition"] == "Attention").sum())
            deteriorating = int((health["Condition"] == "Deteriorating").sum())
            normal = int((health["Condition"] == "Normal").sum())
            abnormal = critical + attention + deteriorating
            total_params = len(health)

            # -----------------------------------------------------------------
            # Data freshness / quality gate. A historical envelope is not proof
            # of current equipment health when the latest PLC evidence is old.
            # -----------------------------------------------------------------
            eq_tags = [str(x).strip() for x in ev.get("PLC Tag", pd.Series(dtype=str)).fillna("") if str(x).strip()]
            eq_tags = list(dict.fromkeys(eq_tags))
            quality_map = {tag: _eh_parameter_quality(df, tag) for tag in eq_tags}
            latest_candidates = [q["latest"] for q in quality_map.values() if pd.notna(q["latest"])]
            eq_latest = max(latest_candidates) if latest_candidates else pd.NaT
            freshness = _eh_freshness(eq_latest)
            quality_warnings = [
                (tag, q) for tag, q in quality_map.items()
                if not q.get("verified", False)
            ]
            analyzable = sum(1 for q in quality_map.values() if q["valid"] >= 20)
            coverage_pct = analyzable / max(len(eq_tags), 1) * 100
            quality_gate = freshness["state"] in {"STALE", "NO RECENT DATA", "NO DATA"}
            parameter_quality_gate = any(
                q["status"] in {"NO VALID DATA", "MISSING TAG", "FLATLINE", "INSUFFICIENT"}
                for q in quality_map.values()
            )
            verified_tags = {tag for tag, q in quality_map.items() if q.get("verified", False)}
            unverified_count = max(0, total_params - len(verified_tags))

            # Historical condition remains available for analysis, but the
            # engineer-facing page never calls stale/unverified data Normal.
            visible_normal = normal if not quality_gate and not parameter_quality_gate else 0
            visible_deteriorating = deteriorating if not quality_gate and not parameter_quality_gate else 0
            visible_attention = attention if not quality_gate and not parameter_quality_gate else 0
            visible_critical = critical if not quality_gate and not parameter_quality_gate else 0

            # Existing page score logic is preserved only when current evidence
            # is recent enough to justify a present-state screening statement.
            severity = {"Normal": 0, "Deteriorating": 12, "Attention": 25, "Critical": 50}
            conf_weight = {"High": 1.0, "Medium": .85, "Low": .65}
            health["Penalty"] = [
                min(
                    60,
                    (
                        severity.get(r.Condition, 0)
                        + min(r["Outside Fraction"] * 12, 8)
                    ) * conf_weight.get(r.Confidence, .65),
                )
                for _, r in health.iterrows()
            ]
            raw_score = 100 - float(health["Penalty"].mean())

            if quality_gate:
                overall, risk, priority, icon, cap = "UNVERIFIED", "DATA QUALITY", "P4", (
                    "⚪" if freshness["state"] == "NO RECENT DATA" else "🟠"
                ), None
                score = None
            elif parameter_quality_gate:
                overall, risk, priority, icon, cap = "UNVERIFIED", "DATA QUALITY", "P4", "🟡", None
                score = None
            elif critical:
                overall, risk, priority, icon, cap = "CRITICAL", "HIGH", "P1", "🔴", 69
                score = int(round(max(0, min(cap, raw_score))))
            elif attention:
                overall, risk, priority, icon, cap = "ATTENTION", "MEDIUM", "P2", "🟠", 89
                score = int(round(max(0, min(cap, raw_score))))
            elif deteriorating:
                overall, risk, priority, icon, cap = "DETERIORATING", "MEDIUM-LOW", "P3", "🟡", 94
                score = int(round(max(0, min(cap, raw_score))))
            else:
                overall, risk, priority, icon, cap = "HEALTHY", "LOW", "P4", "🟢", 100
                score = int(round(max(0, min(cap, raw_score))))

            # Current data timestamp is equipment-specific, not plant-wide.
            last_label = freshness["label"] if pd.notna(eq_latest) else "No valid PLC timestamp"
            if pd.notna(freshness["hours"]):
                age_h = float(freshness["hours"])
                data_age_label = f"{age_h/24.0:.0f} days" if age_h >= 24 else f"{age_h:.1f} h"
            else:
                data_age_label = "—"

            # Primary abnormal signal.
            flagged = health[health["Condition"] != "Normal"].copy()
            condition_order = {"Critical": 0, "Attention": 1, "Deteriorating": 2}
            if not flagged.empty:
                flagged["_condition_order"] = flagged["Condition"].map(condition_order).fillna(9)
                sort_cols = [c for c in ["_condition_order", "Deviation Sigma", "Outside Fraction"] if c in flagged.columns]
                asc = [True] + [False] * (len(sort_cols) - 1)
                flagged = flagged.sort_values(sort_cols, ascending=asc)
                primary = flagged.iloc[0]
                selected_tag_default = str(primary["PLC Tag"])
            else:
                selected_tag_default = str(health.iloc[0]["PLC Tag"])

            # -----------------------------------------------------------------
            # Equipment identity / status hero
            # -----------------------------------------------------------------
            status_cls = overall.lower().replace(" ", "-")
            st.markdown(
                f'<div class="eh22-hero">'
                f'<div class="eh22-hero-left"><div class="eh22-eq-icon">⚙</div>'
                f'<div><div class="eh22-code">{selected_eq}</div>'
                f'<div class="eh22-name">{eq_name}</div>'
                f'<div class="eh22-tags"><span>AREA {eq_area}</span><span>{total_params} ANALYZABLE PARAMETERS</span><span>{len(eq_tags)} CONFIGURED TAGS</span></div></div></div>'
                f'<div class="eh22-hero-right"><div class="eh22-status {status_cls}">{icon} {priority} · {overall}</div>'
                f'<div class="eh22-last">{freshness["state"]} · {last_label}</div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # -----------------------------------------------------------------
            # Decision KPI strip
            # -----------------------------------------------------------------
            k1, k2, k3, k4, k5 = st.columns(5, gap="medium")
            confidence_counts = health["Confidence"].value_counts()
            confidence_mode = str(confidence_counts.idxmax()) if len(confidence_counts) else "—"
            confidence_n = int(confidence_counts.max()) if len(confidence_counts) else 0
            score_value = str(score) if score is not None else "N/A"
            score_small = "Screening berdasarkan current evidence" if score is not None else "Score kondisi saat ini tidak ditampilkan"
            freshness_cls = {"LIVE":"green", "RECENT":"green", "AGING":"orange", "STALE":"orange", "NO RECENT DATA":"critical", "NO DATA":"critical"}.get(freshness["state"], "orange")
            historical_flags = int(abnormal)
            current_verified_abnormal = int(
                (health["Condition"].isin(["Deteriorating", "Attention", "Critical"])
                 & health["PLC Tag"].map(lambda t: quality_map.get(str(t), {}).get("verified", False))).sum()
            )
            kpis = [
                (k1, "CONDITION SCORE", score_value, "/ 100" if score is not None else "", score_small, "blue" if score is not None else "critical"),
                (k2, "KONDISI SAAT INI", f"{icon} {overall}", "", f"{unverified_count} parameter belum terverifikasi" if quality_gate or parameter_quality_gate else f"{current_verified_abnormal} parameter abnormal", status_cls),
                (k3, "HISTORICAL FLAGS", f"{historical_flags}", f"/ {total_params}", "hanya historical screening", "orange" if historical_flags else "green"),
                (k4, "PRIORITY", priority, "", f"{risk}", priority.lower()),
                (k5, "KESEGARAN DATA", freshness["state"], "", f"{analyzable}/{max(len(eq_tags),1)} tag yang dapat dianalisis · {coverage_pct:.0f}%", freshness_cls),
            ]
            for col, label, value, suffix, small, cls in kpis:
                col.markdown(
                    f'<div class="eh22-kpi {cls}"><div class="eh22-kpi-label">{label}</div>'
                    f'<div class="eh22-kpi-value">{value}<small>{suffix}</small></div>'
                    f'<div class="eh22-kpi-small">{small}</div></div>',
                    unsafe_allow_html=True,
                )

            # -----------------------------------------------------------------
            # Decision banner: answer "what do I need to know first?"
            # -----------------------------------------------------------------
            if quality_gate:
                decision_text = (
                    f'<b>Do not make a current maintenance decision from this screen.</b> Latest equipment evidence is '
                    f'<b>{freshness["state"].lower()}</b> ({data_age_label} old). Refresh PLC/historian data first.'
                    if pd.notna(freshness["hours"]) else
                    '<b>Current evidence unavailable.</b> Verify PLC/historian connectivity and tag mapping before assessing equipment condition.'
                )
                st.markdown(
                    f'<div class="eh22-decision"><div class="eh22-decision-icon">⚠</div>'
                    f'<div><div class="eh22-decision-title">KESEGARAN DATA GATE</div>'
                    f'<div class="eh22-decision-text">{decision_text}</div></div></div>',
                    unsafe_allow_html=True,
                )
            elif parameter_quality_gate:
                bad = quality_warnings[0][1] if quality_warnings else None
                qtext = bad["status"] if bad else "Parameter data quality requires review"
                st.markdown(
                    f'<div class="eh22-decision"><div class="eh22-decision-icon">⚠</div>'
                    f'<div><div class="eh22-decision-title">DATA QUALITY REVIEW</div>'
                    f'<div class="eh22-decision-text"><b>{qtext}.</b> Verify equipment operating state and instrument signal before interpreting the historical envelope.</div></div></div>',
                    unsafe_allow_html=True,
                )
            elif not flagged.empty:
                p = flagged.iloc[0]
                if p["Condition"] == "Critical":
                    decision_text = f'<b>Immediate engineering review.</b> {p["Parameter"]} is the leading abnormal signal with {p["Shift %"]:+.1f}% recent shift and {p["Deviation Sigma"]:.2f}σ deviation.'
                elif p["Condition"] == "Attention":
                    decision_text = f'<b>Plan focused inspection.</b> The leading signal is {p["Parameter"]} with {p["Shift %"]:+.1f}% recent shift. Verify process and field condition before intervention.'
                else:
                    decision_text = f'<b>Watch deterioration.</b> {p["Parameter"]} is outside the normal historical behaviour. Confirm whether the shift is process-driven or equipment-driven.'
                st.markdown(
                    f'<div class="eh22-decision"><div class="eh22-decision-icon">{icon}</div>'
                    f'<div><div class="eh22-decision-title">ENGINEERING DECISION SIGNAL</div>'
                    f'<div class="eh22-decision-text">{decision_text}</div></div></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="eh22-decision healthy"><div class="eh22-decision-icon">✓</div>'
                    '<div><div class="eh22-decision-title">NO ABNORMAL SIGNAL DETECTED</div>'
                    '<div class="eh22-decision-text"><b>Routine monitoring.</b> Current PLC behaviour remains within the historical screening envelope.</div></div></div>',
                    unsafe_allow_html=True,
                )

            # -----------------------------------------------------------------
            # Stage 2 — Parameter Health Matrix
            # -----------------------------------------------------------------
            st.markdown(
                '<div class="eh25-section-title"><span class="eh-section-icon blue">📋</span><span>MATRIX HEALTH PARAMETER</span></div>'
                '<div class="eh25-section-sub">Engineer view — top signals first; current condition is separated from historical screening</div>',
                unsafe_allow_html=True,
            )

            matrix_rows = []
            for _, rr in health.iterrows():
                tag = str(rr["PLC Tag"])
                q = quality_map.get(tag, {})
                qlabel = q.get("label", q.get("status", "UNKNOWN"))
                display_condition = (
                    str(rr["Condition"]).upper()
                    if q.get("verified", False) and not quality_gate and not parameter_quality_gate
                    else "UNVERIFIED"
                )
                matrix_rows.append({
                    "PLC Tag": tag,
                    "Parameter": str(rr["Parameter"]),
                    "Current": float(rr["Current"]),
                    "Unit": str(rr["Unit"]),
                    "Condition": display_condition,
                    "Historical": str(rr["Condition"]).upper(),
                    "Direction": str(rr.get("Direction", "Stable")),
                    "Shift": float(rr.get("Shift %", 0.0)),
                    "Deviation": float(rr.get("Deviation Sigma", 0.0)),
                    "Outside": float(rr.get("Outside Fraction", 0.0)) * 100.0,
                    "Confidence": str(rr["Confidence"]),
                    "Data Quality": qlabel,
                })

            matrix_df = pd.DataFrame(matrix_rows)
            condition_rank = {
                "CRITICAL": 0, "ATTENTION": 1, "DETERIORATING": 2,
                "UNVERIFIED": 3, "NORMAL": 4
            }
            matrix_df["_rank"] = matrix_df["Condition"].map(condition_rank).fillna(9)
            matrix_df["_signal_score"] = (
                matrix_df["Deviation"].abs() * 3
                + matrix_df["Outside"] / 10
                + matrix_df["Shift"].abs() / 10
                + matrix_df["_rank"].replace({4: 0, 3: 1, 2: 2, 1: 3, 0: 4})
            )
            matrix_df = matrix_df.sort_values(
                ["_rank", "_signal_score"],
                ascending=[True, False]
            ).drop(columns=["_rank", "_signal_score"])

            def _matrix_condition_badge(value):
                v = str(value).upper()
                cls = {
                    "CRITICAL": "critical", "ATTENTION": "attention",
                    "DETERIORATING": "deteriorating", "NORMAL": "normal",
                    "UNVERIFIED": "unverified",
                }.get(v, "unverified")
                return f'<span class="eh25-pill {cls}">{v}</span>'

            def _matrix_quality_badge(value):
                v = str(value).upper()
                if v == "VALID":
                    cls = "valid"
                elif "FLATLINE" in v:
                    cls = "flatline"
                elif "NO DATA" in v or "MISSING" in v:
                    cls = "bad"
                else:
                    cls = "warn"
                return f'<span class="eh25-quality {cls}">{v}</span>'

            def _render_matrix(frame):
                html_rows = []
                for _, rr in frame.iterrows():
                    html_rows.append(
                        '<div class="eh25-matrix-row">'
                        f'<div class="eh25-param"><b>{rr["Parameter"]}</b><small>{rr["PLC Tag"]}</small></div>'
                        f'<div class="eh25-current"><b>{rr["Current"]:.3f}</b><small>{rr["Unit"]}</small></div>'
                        f'<div>{_matrix_condition_badge(rr["Condition"])}</div>'
                        f'<div class="eh25-direction"><b>{rr["Direction"]}</b><small>Shift {rr["Shift"]:+.1f}%</small></div>'
                        f'<div class="eh25-deviation"><b>{rr["Deviation"]:.2f}σ</b><small>Outside {rr["Outside"]:.0f}%</small></div>'
                        f'<div>{_matrix_quality_badge(rr["Data Quality"])}</div>'
                        f'<div class="eh25-confidence"><b>{rr["Confidence"]}</b></div>'
                        '</div>'
                    )
                return ''.join(html_rows) if html_rows else '<div class="eh25-empty">Tidak tersedia evidence parameter.</div>'

            matrix_header = (
                '<div class="eh25-matrix">'
                '<div class="eh25-matrix-head">'
                '<div>PARAMETER / TAG</div><div>CURRENT</div><div>CONDITION</div>'
                '<div>TREND</div><div>DEVIATION</div><div>DATA QUALITY</div><div>CONF.</div>'
                '</div>'
            )
            top_n = min(10, len(matrix_df))
            st.markdown(
                matrix_header + _render_matrix(matrix_df.head(top_n)) + '</div>',
                unsafe_allow_html=True
            )

            if len(matrix_df) > top_n:
                with st.expander(f"📋 Lihat semua {len(matrix_df)} parameter yang dimonitor", expanded=False):
                    st.markdown(
                        matrix_header + _render_matrix(matrix_df) + '</div>',
                        unsafe_allow_html=True
                    )

            verified_abnormal = matrix_df[
                matrix_df["Condition"].isin(["CRITICAL", "ATTENTION", "DETERIORATING"])
            ]
            if not verified_abnormal.empty:
                top = verified_abnormal.iloc[0]
                st.markdown(
                    f'<div class="eh25-focus">'
                    f'<b>ENGINEERING FOCUS:</b> {top["Parameter"]} ({top["PLC Tag"]}) — '
                    f'{top["Condition"]}, {top["Deviation"]:.2f}σ deviation, '
                    f'{top["Shift"]:+.1f}% recent shift.</div>',
                    unsafe_allow_html=True,
                )
            elif unverified_count:
                st.markdown(
                    f'<div class="eh25-focus neutral">'
                    f'<b>DATA FOCUS:</b> {unverified_count} parameter(s) are unverified. '
                    f'Historical flags must not be interpreted as current equipment abnormality.</div>',
                    unsafe_allow_html=True,
                )

            # -----------------------------------------------------------------
            # Stage 3 — Operating Context
            # -----------------------------------------------------------------
            op_state, op_state_note = _eh_context_operating_state(health, eq_name)
            context_stale = freshness["state"] in {"STALE", "NO RECENT DATA", "NO DATA"}

            flow_row = _eh_find_context_signal(health, "feed", eq_name)
            load_row = _eh_find_context_signal(health, "load", eq_name)
            speed_row = _eh_find_context_signal(health, "speed", eq_name)
            pressure_row = _eh_find_context_signal(health, "pressure", eq_name)

            context_note = (
                "Values are current screening evidence."
                if not context_stale
                else "Values below are last-valid historical evidence only; they are not the present operating state."
            )

            st.markdown(
                '<div class="eh26-section-title"><span class="eh-section-icon teal">⚙️</span><span>KONTEKS OPERASI</span></div>'
                '<div class="eh26-section-sub">Use operating context to distinguish equipment behaviour from process/load effects</div>',
                unsafe_allow_html=True,
            )

            state_title = "OPERATING STATE" if not context_stale else "OPERATING STATE · NOT VERIFIED"
            cards = [
                _eh_context_card(
                    state_title,
                    op_state if not context_stale else "NOT VERIFIED",
                    op_state_note,
                    "running" if op_state == "RUNNING" and not context_stale else "stopped" if op_state.startswith("STOPPED") and not context_stale else "neutral"
                ),
                _eh_context_card(
                    "MILL FEED / PROCESS FEED" if ("mill" in eq_name.lower()) else "FLOW / FEED",
                    _eh_context_value(flow_row, context_stale),
                    str(flow_row.get("Parameter")) if flow_row is not None else "No relevant feed/flow signal mapped",
                ),
                _eh_context_card(
                    "MAIN MOTOR LOAD" if ("mill" in eq_name.lower() or "crusher" in eq_name.lower()) else "LOAD / CURRENT",
                    _eh_context_value(load_row, context_stale),
                    str(load_row.get("Parameter")) if load_row is not None else "No relevant motor/load signal mapped",
                ),
                _eh_context_card(
                    "MILL SPEED" if "mill" in eq_name.lower() else "SPEED",
                    _eh_context_value(speed_row, context_stale),
                    str(speed_row.get("Parameter")) if speed_row is not None else "No relevant speed signal mapped",
                ),
                _eh_context_card(
                    "DISCHARGE PRESSURE" if ("mill" in eq_name.lower() or "pump" in eq_name.lower()) else "PRESSURE",
                    _eh_context_value(pressure_row, context_stale),
                    str(pressure_row.get("Parameter")) if pressure_row is not None else "No relevant pressure signal mapped",
                ),
            ]

            st.markdown(
                '<div class="eh26-context-grid">' + ''.join(cards) + '</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="eh26-context-note">ⓘ <b>{freshness["state"]}</b> · {context_note} '
                f'Context signals are selected using equipment-aware semantic matching; a broad keyword match is not treated as a valid engineering mapping.</div>',
                unsafe_allow_html=True,
            )

            # -----------------------------------------------------------------
            # Stage 4 — Maintenance Context
            # -----------------------------------------------------------------
            # This section deliberately distinguishes:
            #   1) validated criticality,
            #   2) PLC-derived historical findings,
            #   3) Action Center workflow state,
            #   4) actual maintenance history.
            # The app does not invent PM/breakdown/running-hour history when
            # those sources are not connected.
            # -----------------------------------------------------------------
            criticality_df_ctx = st.session_state.get("validated_criticality", pd.DataFrame())
            criticality_value = "NOT CONFIGURED"
            criticality_basis = "No validated criticality master loaded"
            if (
                isinstance(criticality_df_ctx, pd.DataFrame)
                and not criticality_df_ctx.empty
                and {"Equipment Code", "Criticality"}.issubset(criticality_df_ctx.columns)
            ):
                _crit_rows = criticality_df_ctx[
                    criticality_df_ctx["Equipment Code"].apply(normalize_equipment_code)
                    == normalize_equipment_code(selected_eq)
                ]
                if not _crit_rows.empty:
                    _crit_val = str(_crit_rows.iloc[0]["Criticality"]).strip()
                    if _crit_val:
                        criticality_value = _crit_val.upper()
                        if "Criticality Basis" in _crit_rows.columns:
                            criticality_basis = str(_crit_rows.iloc[0].get("Criticality Basis", "")).strip() or "Validated criticality master"
                        else:
                            criticality_basis = "Validated criticality master"

            try:
                eq_findings_ctx = build_action_findings(
                    master[master["Equipment Code"].astype(str) == str(selected_eq)],
                    df,
                    criticality_df_ctx
                )
            except Exception:
                eq_findings_ctx = pd.DataFrame()

            open_action_count = 0
            action_status_summary = "NO ACTIVE FINDING"
            if not eq_findings_ctx.empty:
                action_store_ctx = ensure_action_store(eq_findings_ctx)
                eq_ids = set(eq_findings_ctx["Finding ID"].astype(str))
                eq_actions = [
                    v for k, v in action_store_ctx.items()
                    if str(k) in eq_ids
                ]
                open_action_count = sum(
                    1 for a in eq_actions
                    if str(a.get("Status", "OPEN")).upper() != "CLOSED"
                )
                if open_action_count:
                    statuses = pd.Series(
                        [str(a.get("Status", "OPEN")).upper() for a in eq_actions]
                    ).value_counts()
                    action_status_summary = " · ".join(
                        f"{k}: {int(v)}" for k, v in statuses.items()
                    )

            historical_finding_count = int(len(eq_findings_ctx))
            maintenance_history_connected = bool(
                st.session_state.get("maintenance_history_connected", False)
            )

            st.markdown(
                '<div class="eh28-section-title"><span class="eh-section-icon orange">🛠️</span><span>MAINTENANCE CONTEXT</span></div>'
                '<div class="eh28-section-sub">Connect condition evidence with maintenance priority and workflow — without inventing maintenance history</div>',
                unsafe_allow_html=True,
            )

            maintenance_cards = [
                _eh_context_card(
                    "CRITICALITY EQUIPMENT",
                    criticality_value,
                    criticality_basis,
                    "running" if criticality_value in {"CRITICAL", "VERY HIGH", "HIGH"} else "neutral"
                ),
                _eh_context_card(
                    "HISTORICAL FINDINGS",
                    f"{historical_finding_count}",
                    "PLC screening findings available for this equipment",
                    "stopped" if historical_finding_count else "neutral"
                ),
                _eh_context_card(
                    "ACTION TERBUKA",
                    f"{open_action_count}",
                    action_status_summary,
                    "stopped" if open_action_count else "neutral"
                ),
                _eh_context_card(
                    "RIWAYAT MAINTENANCE",
                    "CONNECTED" if maintenance_history_connected else "NOT CONNECTED",
                    "Source available to this screen" if maintenance_history_connected else "Riwayat PM / breakdown / work order belum terhubung",
                    "running" if maintenance_history_connected else "neutral"
                ),
            ]
            st.markdown(
                '<div class="eh28-maint-grid">' + ''.join(maintenance_cards) + '</div>',
                unsafe_allow_html=True,
            )

            if not maintenance_history_connected:
                st.markdown(
                    '<div class="eh28-maint-note">ⓘ <b>Kesenjangan maintenance history:</b> this screen currently cannot confirm '
                    'last PM, last breakdown, running hours, work order age or repeat-failure history. '
                    'Those items should be connected before using maintenance history as evidence.</div>',
                    unsafe_allow_html=True,
                )
            elif open_action_count:
                st.markdown(
                    f'<div class="eh28-maint-note active">⚡ <b>Action Center:</b> {open_action_count} active finding(s) '
                    f'are already associated with this equipment. Review the existing investigation/action status before creating duplicate work.</div>',
                    unsafe_allow_html=True,
                )

            # Maintenance decision bridge — concise and explicit.
            if freshness["state"] in {"STALE", "NO RECENT DATA", "NO DATA"}:
                maint_decision_title = "REFRESH EVIDENCE TERLEBIH DAHULU"
                maint_decision_text = "Kondisi PLC saat ini belum terverifikasi. Jangan melakukan eskalasi maintenance hanya berdasarkan historical screening."
                maint_decision_cls = "blocked"
            elif historical_finding_count and open_action_count:
                maint_decision_title = "LANJUTKAN INVESTIGATION YANG ADA"
                maint_decision_text = "Historical PLC finding sudah memiliki record aktif di Action Center. Verifikasi investigation yang ada sebelum membuat action baru."
                maint_decision_cls = "active"
            elif historical_finding_count:
                maint_decision_title = "VERIFIKASI HISTORICAL FINDING"
                maint_decision_text = "Terdapat historical finding dari PLC. Konfirmasi persistence, operating context, dan field condition sebelum intervention maintenance."
                maint_decision_cls = "review"
            else:
                maint_decision_title = "ROUTINE MAINTENANCE PATH"
                maint_decision_text = "Tidak ada historical finding dari PLC untuk Equipment ini. Lanjutkan maintenance strategy yang telah disetujui."
                maint_decision_cls = "normal"

            st.markdown(
                f'<div class="eh28-decision {maint_decision_cls}">'
                f'<div class="eh28-decision-title">{maint_decision_title}</div>'
                f'<div class="eh28-decision-text">{maint_decision_text}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # -----------------------------------------------------------------
            # Stage 5 — Engineering Diagnosis / Root Cause Assist
            # -----------------------------------------------------------------
            diagnoses = _eh29_rank_diagnoses(
                health,
                quality_gate=quality_gate,
                parameter_quality_gate=parameter_quality_gate,
                equipment_name=eq_name,
                equipment_code=str(selected_eq),
            )
            corr_pairs = _eh29_correlation_evidence(health, df)

            st.markdown(
                '<div class="eh29-section-title"><span class="eh-section-icon purple">🧠</span><span>DIAGNOSIS ENGINEERING</span></div>'
                '<div class="eh29-section-sub">Differential diagnosis — peringkat kemungkinan mekanisme berdasarkan signal evidence; lakukan Field Verification sebelum intervention</div>',
                unsafe_allow_html=True,
            )

            if quality_gate or parameter_quality_gate:
                st.markdown(
                    '<div class="eh29-gate">⚠ <b>DIAGNOSTIC GATE:</b> current evidence is not sufficiently verified. '
                    'The cards below are <b>historical / diagnostic hypotheses only</b>; do not treat them as present equipment failure conclusions.</div>',
                    unsafe_allow_html=True,
                )

            if not diagnoses:
                st.markdown(
                    '<div class="eh29-empty"><b>Belum ada hipotesis diagnosis yang cukup kuat.</b> '
                    'Diperlukan verified signal evidence tambahan atau hubungan antar-parameter yang lebih jelas.</div>',
                    unsafe_allow_html=True,
                )
            else:
                dcols=st.columns(min(3,len(diagnoses)), gap="medium")
                for j,diag in enumerate(diagnoses[:3]):
                    evidence_html="".join(f'<li>{x}</li>' for x in diag["evidence"]) or "<li>Context evidence available</li>"
                    dx_icon = {
                        "MECH_BEARING": "🔩",
                        "MECH_LOAD": "⚙️",
                        "FLOW_RESTRICTION": "💧",
                        "PUMP_HYDRAULIC": "🚿",
                        "DRIVE_CONTROL": "⚡",
                        "THERMAL_LUBE": "🌡️",
                        "INSTRUMENTATION": "📡",
                    }.get(diag.get("id"), "🧠")
                    dcols[j].markdown(
                        f'<div class="eh29-dx-card">'
                        f'<div class="eh29-dx-top"><span class="eh29-dx-icon">{dx_icon}</span>'
                        f'<div class="eh29-dx-rank">#{j+1} · EVIDENCE SCORE {diag["score"]}/100</div></div>'
                        f'<div class="eh29-dx-title">{diag["title"]}</div>'
                        f'<ul>{evidence_html}</ul>'
                        f'<div class="eh29-dx-caution">⚠ {diag["caution"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                selected_dx=st.selectbox(
                    "🔎 Investigate diagnostic hypothesis",
                    [d["id"] for d in diagnoses],
                    format_func=lambda x: next((d["title"] for d in diagnoses if d["id"]==x),x),
                    key=f"eh29_dx_{selected_eq}",
                )
                dx=next(d for d in diagnoses if d["id"]==selected_dx)

                evidence = _eh32_build_evidence(
                    health, df, dx,
                    quality_map=quality_map,
                    freshness_state=freshness["state"],
                    equipment_name=eq_name,
                    equipment_code=str(selected_eq),
                )

                dx1,dx2=st.columns([1.15,1.0],gap="medium")
                with dx1:
                    evidence_label = "HISTORICAL EVIDENCE" if quality_gate or parameter_quality_gate else "EVIDENCE"
                    st.markdown(
                        f'<div class="eh29-panel eh29-evidence-panel">'
                        f'<div class="eh29-panel-title">🔎 BUKTI PENDUKUNG <span class="eh29-evidence-badge">{evidence_label}</span></div>'
                        f'<div class="eh29-panel-sub">Evidence yang mendukung, melemahkan, atau memberi context terhadap hipotesis <b>{dx["title"]}</b></div>'
                        f'<div class="eh29-strength strength-{evidence["strength"].lower()}">'
                        f'<span>KEKUATAN EVIDENCE</span><b>{evidence["strength"]}</b></div>',
                        unsafe_allow_html=True,
                    )

                    def render_evidence_group(title, items, cls, icon):
                        if not items:
                            return f'<div class="eh29-evidence-group {cls}"><div class="eh29-group-title">{icon} {title}</div><div class="eh29-no-evidence">Tidak ada signal yang cukup untuk kelompok ini.</div></div>'
                        cards=[]
                        for ev in items:
                            verified_txt="VERIFIED" if ev["Verified"] else "HISTORICAL"
                            dev_txt=f'{ev["Deviation"]:.2f}σ' if np.isfinite(ev["Deviation"]) else "—"
                            shift_txt=f'{ev["Shift"]:+.1f}%'
                            ts=ev.get("Timestamp",pd.NaT)
                            ts_txt=pd.to_datetime(ts,errors="coerce").strftime("%d %b %Y · %H:%M") if pd.notna(ts) else "Timestamp tidak tersedia"
                            cards.append(
                                f'<div class="eh29-evidence-item {cls}">'
                                f'<div class="eh29-evidence-item-top"><span class="eh29-evidence-icon">{icon}</span>'
                                f'<div><b>{ev["Parameter"]}</b><small>{ev["Tag"]}</small></div>'
                                f'<span class="eh29-evidence-state">{ev["Condition"].upper()}</span></div>'
                                f'<div class="eh29-evidence-value"><strong>{ev["Current"]:,.3f}</strong> <span>{ev["Unit"]}</span>'
                                f'<span class="eh29-evidence-metrics">Shift {shift_txt} · Dev {dev_txt}</span></div>'
                                f'<div class="eh29-evidence-reason">{ev["Reason"]}</div>'
                                f'<div class="eh29-evidence-meta">{verified_txt} · {ev["Quality"]} · PLC {ts_txt}</div>'
                                f'</div>'
                            )
                        return f'<div class="eh29-evidence-group {cls}"><div class="eh29-group-title">{icon} {title} <span>{len(items)}</span></div>{"".join(cards)}</div>'

                    evidence_html=(
                        render_evidence_group("SUPPORTING EVIDENCE", evidence["supporting"], "support", "🟠")
                        + render_evidence_group("CONTRADICTING EVIDENCE", evidence["contradicting"], "contradict", "🟢")
                        + render_evidence_group("CONTEXT EVIDENCE", evidence["context"], "context", "⚪")
                    )
                    st.markdown(evidence_html,unsafe_allow_html=True)
                    st.markdown(
                        '<div class="eh29-evidence-foot">'
                        '<b>Catatan engineering:</b> Evidence ini adalah decision-support. Ia tidak membuktikan root cause dan tidak menggantikan Field Verification, process condition check, OEM/design limit, atau maintenance history.'
                        '</div></div>',unsafe_allow_html=True
                    )

                with dx2:
                    checks="".join(
                        f'<div class="eh29-check"><span>□</span><div>{c}</div></div>'
                        for c in dx["checks"]
                    )
                    st.markdown(
                        f'<div class="eh29-panel"><div class="eh29-panel-title">🛠 CHECKLIST FIELD VERIFICATION</div>'
                        f'<div class="eh29-panel-sub">Gunakan pemeriksaan berikut untuk mengonfirmasi atau menolak hipotesis</div>'
                        f'{checks}'
                        f'<div class="eh29-caution"><b>Catatan engineering:</b> {dx["caution"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

            if corr_pairs:
                corr_html="".join(
                    f'<tr><td><b>{a}</b><small>{ta}</small></td><td><b>{b}</b><small>{tb}</small></td><td><span class="eh29-corr-pill {"positive" if corr>=0 else "negative"}">{corr:+.2f}</span></td><td>{n:,}</td></tr>'
                    for _,corr,a,b,ta,tb,n,fa,fb in corr_pairs
                )
                st.markdown(
                    '<div class="eh29-correlation">'
                    '<div class="eh29-panel-title">🔗 HUBUNGAN ANTAR-SIGNAL</div>'
                    '<div class="eh29-panel-sub">Co-movement historis antar <b>signal family yang berbeda</b> (|r| ≥ 0.70). Signal yang sama atau satu family tidak ditampilkan agar hubungan lebih relevan untuk maintenance.</div>'
                    '<table><thead><tr><th>Signal A</th><th>Signal B</th><th>Correlation r</th><th>Samples</th></tr></thead>'
                    f'<tbody>{corr_html}</tbody></table></div>',
                    unsafe_allow_html=True,
                )

            # -----------------------------------------------------------------
            # Diagnostic overview
            # -----------------------------------------------------------------
            d_left, d_mid, d_right = st.columns([.85, 1.55, 1.0], gap="medium")

            with d_left:
                st.markdown(
                    '<div class="eh22-panel eh-panel-condition"><div class="eh22-panel-head">📊 CONDITION MIX</div>'
                    '<div class="eh22-panel-sub">Parameter-level screening state</div>',
                    unsafe_allow_html=True,
                )
                for label, n, cls in [
                    ("VERIFIED NORMAL", visible_normal, "normal"),
                    ("DETERIORATING", visible_deteriorating, "deteriorating"),
                    ("ATTENTION", visible_attention, "attention"),
                    ("CRITICAL", visible_critical, "critical"),
                    ("UNVERIFIED", unverified_count, "unverified"),
                ]:
                    pct = n / max(total_params, 1) * 100
                    st.markdown(
                        f'<div class="eh22-dist-row"><div><span class="eh22-mini-dot {cls}"></span><b>{label}</b></div>'
                        f'<strong>{n}</strong><small>{pct:.0f}%</small></div>',
                        unsafe_allow_html=True,
                    )
                st.markdown(
                    f'<div class="eh22-panel-sub" style="margin-top:8px;">'
                    f'Data quality: {len(verified_tags)}/{max(len(eq_tags),1)} tags verified</div>',
                    unsafe_allow_html=True,
                )
                st.markdown('</div>', unsafe_allow_html=True)

            with d_mid:
                st.markdown(
                    '<div class="eh22-panel eh-panel-alert"><div class="eh22-panel-head">⚠ ABNORMAL PARAMETERS</div>'
                    '<div class="eh22-panel-sub">Ranked by condition severity and deviation</div>',
                    unsafe_allow_html=True,
                )
                if quality_gate or parameter_quality_gate:
                    st.markdown(
                        f'<div class="eh22-no-issue" style="border-left:4px solid #f59e0b;">'
                        f'⚪ Current condition is <b>unverified</b>. Historical screening is available, '
                        f'but {unverified_count} parameter(s) do not have sufficiently current/verified evidence.</div>',
                        unsafe_allow_html=True,
                    )
                elif flagged.empty:
                    st.markdown('<div class="eh22-no-issue">✓ All parameter yang dimonitor are currently within historical screening range.</div>', unsafe_allow_html=True)
                else:
                    for _, rr in flagged.head(5).iterrows():
                        cls = str(rr["Condition"]).lower()
                        st.markdown(
                            f'<div class="eh22-abnormal-row">'
                            f'<div class="eh22-abnormal-main"><span class="eh22-status-pill {cls}">{rr["Condition"]}</span>'
                            f'<b>{rr["Parameter"]}</b><span class="eh22-tag">{rr["PLC Tag"]}</span></div>'
                            f'<div class="eh22-abnormal-value"><b>{rr["Shift %"]:+.1f}%</b><small>{rr["Deviation Sigma"]:.2f}σ</small></div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                st.markdown('</div>', unsafe_allow_html=True)

            with d_right:
                st.markdown(
                    '<div class="eh22-panel eh-panel-read"><div class="eh22-panel-head">🧠 ENGINEERING READ</div>'
                    '<div class="eh22-panel-sub">What the screening suggests</div>',
                    unsafe_allow_html=True,
                )
                if quality_gate:
                    read_title = "Current state not verified"
                    read_text = "Historical behaviour is available, but the latest PLC evidence is too old for a present-state health conclusion."
                elif parameter_quality_gate:
                    read_title = "Data quality requires review"
                    read_text = "One or more configured signals may be flatlined, missing or otherwise unsuitable for a current health conclusion."
                elif flagged.empty:
                    read_title = "Stable historical behaviour"
                    read_text = "No parameter is currently outside the historical screening state."
                else:
                    read_title = str(primary["Parameter"])
                    read_text = (
                        f'Historical screening: {primary["Condition"]} · {primary["Direction"]} behaviour · '
                        f'last valid value {primary["Current"]:.3f} {primary["Unit"]} versus historical '
                        f'P05–P95 {primary["Baseline Low"]:.3f}–{primary["Baseline High"]:.3f}.'
                    )
                st.markdown(
                    f'<div class="eh22-read-card"><div class="eh22-read-title">{read_title}</div>'
                    f'<div class="eh22-read-text">{read_text}</div>'
                    f'<div class="eh22-read-rule"></div>'
                    f'<div class="eh22-read-small">Evidence confidence: <b>{primary["Confidence"] if not flagged.empty else health["Confidence"].value_counts().idxmax()}</b></div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

            # -----------------------------------------------------------------
            # Parameter investigation — selector drives evidence below.
            # -----------------------------------------------------------------
            investigation_options = flagged["PLC Tag"].tolist() if not flagged.empty else health["PLC Tag"].tolist()
            if selected_tag_default not in investigation_options:
                selected_tag_default = investigation_options[0]

            i1, i2 = st.columns([1.35, .75], gap="medium")
            with i1:
                selected_tag = st.selectbox(
                    "🔎 Investigate parameter",
                    investigation_options,
                    index=investigation_options.index(selected_tag_default),
                    format_func=lambda x: (
                        f'{x} — {health.loc[health["PLC Tag"] == x, "Parameter"].iloc[0]}'
                    ),
                    key=f"eh22_parameter_{selected_eq}",
                )
            selected_row = health[health["PLC Tag"] == selected_tag].iloc[0]
            with i2:
                selected_q = _eh_parameter_quality(df, selected_tag)
                selected_current_state = (
                    str(selected_row["Condition"])
                    if selected_q.get("verified", False) and not quality_gate and not parameter_quality_gate
                    else "UNVERIFIED"
                )
                st.markdown(
                    f'<div class="eh22-evidence-chip"><span>SIGNAL TERPILIH</span>'
                    f'<b>{selected_current_state}</b>'
                    f'<small>Historical screening: {selected_row["Condition"]} · {selected_row["Confidence"]} confidence · {selected_q["label"]}</small></div>',
                    unsafe_allow_html=True,
                )

            # -----------------------------------------------------------------
            # Trend + evidence cards
            # -----------------------------------------------------------------
            trend, evidence = st.columns([1.65, .85], gap="medium")
            with trend:
                trend_df = df[["ArchiveTime", selected_tag]].copy() if selected_tag in df.columns else pd.DataFrame()
                if not trend_df.empty:
                    trend_df[selected_tag] = pd.to_numeric(trend_df[selected_tag], errors="coerce")
                    trend_df = trend_df.dropna().sort_values("ArchiveTime").set_index("ArchiveTime")

                selected_quality_for_trend = _eh_parameter_quality(df, selected_tag)
                trend_quality_text = selected_quality_for_trend["label"].lower()

                st.markdown(
                    f'<div class="eh22-panel eh-panel-trend"><div class="eh22-panel-head">📈 PARAMETER TREND</div>'
                    f'<div class="eh22-panel-sub">{selected_row["Parameter"]} · historical screening envelope P05–P95 · data {trend_quality_text}</div>',
                    unsafe_allow_html=True,
                )

                if selected_quality_for_trend["status"] in {"STALE", "NO RECENT DATA", "NO DATA"}:
                    st.markdown(
                        '<div style="padding:10px 12px;border:1px solid #fed7aa;background:#fff7ed;border-radius:8px;'
                        'color:#9a3412;font-size:12px;font-weight:600;margin-bottom:8px;">'
                        '⚠ CURRENT DATA TIDAK TERSEDIA · Historical behaviour is shown for reference only. '
                        'The last valid PLC point must not be interpreted as the present equipment state.</div>',
                        unsafe_allow_html=True,
                    )
                elif selected_quality_for_trend["status"] == "FLATLINE":
                    st.markdown(
                        '<div style="padding:10px 12px;border:1px solid #fde68a;background:#fffbeb;border-radius:8px;'
                        'color:#92400e;font-size:12px;font-weight:600;margin-bottom:8px;">'
                        '⚠ FLATLINE · Verifikasi apakah Equipment sedang beroperasi sebelum menginterpretasikan signal zero/constant.</div>',
                        unsafe_allow_html=True,
                    )

                if not trend_df.empty:
                    plot_df = pd.DataFrame(
                        {
                            "Actual": trend_df[selected_tag],
                            "P05": float(selected_row["Baseline Low"]),
                            "P95": float(selected_row["Baseline High"]),
                        },
                        index=trend_df.index,
                    )
                    st.line_chart(plot_df, height=265, width="stretch")
                else:
                    st.info("Tidak tersedia historical trend yang valid untuk PLC tag ini.")
                st.markdown('</div>', unsafe_allow_html=True)

            with evidence:
                st.markdown(
                    '<div class="eh22-panel eh-panel-evidence"><div class="eh22-panel-head">📐 ENGINEERING EVIDENCE</div>'
                    '<div class="eh22-panel-sub">Latest signal versus historical behaviour</div>',
                    unsafe_allow_html=True,
                )
                selected_quality_for_evidence = _eh_parameter_quality(df, selected_tag)
                selected_last = selected_quality_for_evidence.get("latest", pd.NaT)
                selected_freshness = _eh_freshness(selected_last)
                selected_age = selected_freshness["hours"]
                selected_age_label = (
                    f'{selected_age/24.0:.0f} days' if pd.notna(selected_age) and selected_age >= 24
                    else f'{selected_age:.1f} h' if pd.notna(selected_age)
                    else "—"
                )
                evidence_items = [
                    ("Current / last valid", f'{selected_row["Current"]:.3f} {selected_row["Unit"]}'),
                    ("Historical P05", f'{selected_row["Baseline Low"]:.3f} {selected_row["Unit"]}'),
                    ("Historical P95", f'{selected_row["Baseline High"]:.3f} {selected_row["Unit"]}'),
                    ("Recent Shift", f'{selected_row["Shift %"]:+.1f}%'),
                    ("Deviation", f'{selected_row["Deviation Sigma"]:.2f}σ'),
                    ("Outside Fraction", f'{selected_row["Outside Fraction"]*100:.1f}%'),
                    ("Last valid PLC", selected_freshness["label"] if pd.notna(selected_last) else "No valid timestamp"),
                    ("Usia data", selected_age_label),
                ]
                for lab, val in evidence_items:
                    st.markdown(
                        f'<div class="eh22-evidence-row"><span>{lab}</span><b>{val}</b></div>',
                        unsafe_allow_html=True,
                    )
                st.markdown('</div>', unsafe_allow_html=True)

            # -----------------------------------------------------------------
            # Recommendation + direct actions
            # -----------------------------------------------------------------
            rec_left, rec_right = st.columns([1.5, 1], gap="medium")
            with rec_left:
                selected_quality = _eh_parameter_quality(df, selected_tag)
                selected_reco = _eh_recommendation(selected_row, selected_quality, freshness["state"])
                st.markdown(
                    f'<div class="eh22-recommendation"><div class="eh22-rec-head">🛠 ENGINEERING RECOMMENDATION</div>'
                    f'<div class="eh22-rec-title">{selected_reco}</div>'
                    f'<div class="eh22-rec-note">Use the PLC evidence as a screening input. Confirm process condition, field condition, OEM/design limits and maintenance history before deciding intervention.</div></div>',
                    unsafe_allow_html=True,
                )
            with rec_right:
                st.markdown(
                    '<div class="eh22-panel eh-panel-action"><div class="eh22-panel-head">⚡ NEXT ACTION</div>',
                    unsafe_allow_html=True,
                )
                ac1, ac2 = st.columns(2, gap="small")
                with ac1:
                    if st.button("📈 Engineering Trend", key=f"eh22_trend_{selected_eq}_{selected_tag}", width='stretch'):
                        st.session_state["trend_equipment_from_priority"] = selected_eq
                        st.session_state["trend_tag_from_priority"] = selected_tag
                        st.query_params["opp_nav"] = "↗  Engineering Trend"
                        st.rerun()
                with ac2:
                    if st.button("🎯 Maintenance Priority", key=f"eh22_priority_{selected_eq}", width='stretch'):
                        st.session_state["priority_equipment_from_health"] = selected_eq
                        st.query_params["opp_nav"] = "⚠  Maintenance Priority"
                        st.rerun()
                if st.button("🛠 Action Center", key=f"eh22_action_{selected_eq}_{selected_tag}", width='stretch'):
                    st.query_params["opp_nav"] = "✓  Action Center"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # Compact normal-parameter appendix.
            appendix_title = (
                f"📋 View {visible_normal} verified normal parameter(s)"
                if not quality_gate and not parameter_quality_gate
                else f"📋 View {total_params} parameter(s) — current condition unverified"
            )
            with st.expander(appendix_title, expanded=False):
                appendix_condition = health[health["Condition"] == "Normal"].copy()
                if quality_gate or parameter_quality_gate:
                    appendix_condition["Current Status"] = "UNVERIFIED"
                    appendix_condition["Data Quality"] = appendix_condition["PLC Tag"].map(
                        lambda t: quality_map.get(str(t), {}).get("label", "UNKNOWN")
                    )
                normal_table = appendix_condition[
                    ["PLC Tag", "Parameter", "Unit", "Current", "Baseline Low", "Baseline High", "Direction", "Confidence"]
                    + (["Current Status", "Data Quality"] if quality_gate or parameter_quality_gate else [])
                ].copy()
                for c in ["Current", "Baseline Low", "Baseline High"]:
                    normal_table[c] = normal_table[c].round(3)
                st.dataframe(normal_table, width="stretch", hide_index=True)

            st.markdown(
                '<div class="eh22-disclaimer"><b>Engineering governance:</b> historical screening is a decision-support indicator, not an alarm, trip limit or failure prediction. Validate abnormal signals against OEM/design limits, process condition, field inspection and engineering judgement.</div>',
                unsafe_allow_html=True,
            )

elif page == "Maintenance Priority":
    # -------------------------------------------------------------------------
    # Maintenance Priority — Priority & Risk Matrix
    # Purpose: answer "WHAT SHOULD WE DO FIRST?" rather than repeating the
    # diagnostic detail already available in Equipment Health.
    # -------------------------------------------------------------------------
    st.markdown('<div class="opp-page-title">🎯 Maintenance Priority</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="opp-page-sub">Prioritise equipment for engineering review, inspection and maintenance planning based on historical condition screening.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="opp-note"><b>Decision-support only:</b> P1–P4 are screening priorities derived from historical PLC behaviour. They are not alarm/trip limits, failure predictions or automatic work orders. Equipment criticality is only used when validated.</div>',
        unsafe_allow_html=True,
    )

    if "validated_criticality" not in st.session_state:
        st.session_state["validated_criticality"] = pd.DataFrame()

    with st.expander("⚙️ Criticality data — optional validated master", expanded=False):
        st.caption("Use an approved reliability/engineering criticality assessment. The application will not infer criticality from equipment type.")
        uploaded_crit = st.file_uploader(
            "Upload Equipment Criticality Master (.csv)",
            type=["csv"],
            key="criticality_upload"
        )
        if uploaded_crit is not None:
            try:
                crit = pd.read_csv(uploaded_crit).fillna("")
                if not {"Equipment Code", "Criticality"}.issubset(crit.columns):
                    st.error("Criticality file must contain at least: Equipment Code, Criticality")
                else:
                    crit["Equipment Code"] = crit["Equipment Code"].apply(normalize_equipment_code)
                    allowed = {"CRITICAL", "VERY HIGH", "HIGH", "MEDIUM", "MODERATE", "LOW"}
                    bad = sorted(set(str(x).strip().upper() for x in crit["Criticality"]) - allowed - {""})
                    if bad:
                        st.warning(f"Unrecognized criticality values: {', '.join(bad)}. They remain unvalidated.")
                    st.session_state["validated_criticality"] = crit
                    st.success(f"Validated criticality loaded: {len(crit):,} equipment record(s).")
            except Exception as exc:
                st.error(f"Unable to read criticality file: {exc}")

    criticality_df = st.session_state.get("validated_criticality", pd.DataFrame())
    screening = build_equipment_screening(master, df, criticality_df)

    if screening.empty:
        st.warning("No equipment has sufficient historical numeric data for screening.")
    else:
        # ---- KPI strip: compact and action-oriented -------------------------
        p1n = int((screening["Screening Priority"] == "P1").sum())
        p2n = int((screening["Screening Priority"] == "P2").sum())
        p3n = int((screening["Screening Priority"] == "P3").sum())
        p4n = int((screening["Screening Priority"] == "P4").sum())
        abnormal = int((screening["Condition"] != "HEALTHY").sum())

        st.markdown("### 📌 Priority Snapshot")
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.markdown(f'<div class="priority-kpi priority-p1"><div>🔴 P1 · Immediate Review</div><strong>{p1n:,}</strong><span>highest screening urgency</span></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="priority-kpi priority-p2"><div>🟠 P2 · Plan Inspection</div><strong>{p2n:,}</strong><span>engineering follow-up</span></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="priority-kpi priority-p3"><div>🟡 P3 · Monitor</div><strong>{p3n:,}</strong><span>watch deterioration</span></div>', unsafe_allow_html=True)
        k4.markdown(f'<div class="priority-kpi priority-p4"><div>🟢 P4 · Routine</div><strong>{p4n:,}</strong><span>no abnormal finding</span></div>', unsafe_allow_html=True)
        k5.markdown(f'<div class="priority-kpi priority-focus"><div>🛠️ Requires Attention</div><strong>{abnormal:,}</strong><span>non-healthy equipment</span></div>', unsafe_allow_html=True)

        # ---- Filters ---------------------------------------------------------
        st.markdown("### 🔎 Focus the Worklist")
        f1, f2, f3, f4 = st.columns([1.1, 1, 1, 1.4])
        area_filter = f1.selectbox(
            "Area",
            ["All Areas"] + sorted([str(x) for x in master["Area"].unique() if str(x).strip()]),
            key="priority_area_v2"
        )
        priority_filter = f2.selectbox(
            "Priority",
            ["All", "P1", "P2", "P3", "P4"],
            key="priority_level_v2"
        )
        condition_filter = f3.selectbox(
            "Condition",
            ["All", "CRITICAL", "ATTENTION", "DETERIORATING", "HEALTHY"],
            key="priority_condition_v2"
        )
        sort_filter = f4.selectbox(
            "Sort worklist by",
            ["Priority → Health", "Lowest Health first", "Largest Shift first"],
            key="priority_sort_v2"
        )

        view = screening.copy()
        if area_filter != "All Areas":
            area_eq = set(master.loc[master["Area"] == area_filter, "Equipment Code"].astype(str))
            view = view[view["Equipment Code"].isin(area_eq)]
        if priority_filter != "All":
            view = view[view["Screening Priority"] == priority_filter]
        if condition_filter != "All":
            view = view[view["Condition"] == condition_filter]

        order = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}
        view["_order"] = view["Screening Priority"].map(order).fillna(9)
        if sort_filter == "Lowest Health first":
            view = view.sort_values(["Health", "_order"], ascending=[True, True])
        elif sort_filter == "Largest Shift first":
            view = view.sort_values(["Top Shift %", "_order"], ascending=[False, True])
        else:
            view = view.sort_values(["_order", "Health", "Top Shift %"], ascending=[True, True, False])
        view = view.drop(columns="_order")

        # ---- Priority matrix -------------------------------------------------
        st.markdown("### 🧭 Priority Matrix")
        st.caption("A visual work-prioritisation view. Higher urgency is driven by screening condition; validated criticality is displayed separately and never guessed by the system.")

        matrix = pd.DataFrame({
            "Priority": ["P1", "P2", "P3", "P4"],
            "Meaning": ["Immediate Review", "Plan Inspection", "Monitor", "Routine"],
            "Equipment": [p1n, p2n, p3n, p4n],
        })
        mc = st.columns(4)
        for i, row in matrix.iterrows():
            p = row["Priority"]
            cls = {"P1":"priority-p1","P2":"priority-p2","P3":"priority-p3","P4":"priority-p4"}[p]
            icon = {"P1":"🔴","P2":"🟠","P3":"🟡","P4":"🟢"}[p]
            mc[i].markdown(
                f'<div class="priority-matrix-card {cls}"><div class="matrix-icon">{icon}</div><div class="matrix-code">{p}</div><div class="matrix-title">{row["Meaning"]}</div><div class="matrix-count">{int(row["Equipment"]):,}</div><div class="matrix-label">equipment</div></div>',
                unsafe_allow_html=True,
            )

        # ---- Worklist --------------------------------------------------------
        st.markdown("### 🧰 Maintenance Worklist")
        st.caption(f"Showing {len(view):,} equipment item(s). Select an equipment below to open its engineering decision card.")
        if view.empty:
            st.info("No equipment matches the current filters.")
        else:
            display_cols = [
                "Equipment Code", "Equipment", "Health", "Condition",
                "Screening Priority", "Risk", "Criticality", "Parameters",
                "Deteriorating", "Attention", "Critical", "Top Parameter",
                "Top Finding", "Top Trend", "Top Shift %"
            ]
            display = view[[c for c in display_cols if c in view.columns]].copy()
            display.insert(0, "", range(1, len(display) + 1))
            st.dataframe(display, width='stretch', hide_index=True, height=420)

            # Streamlit dataframes are intentionally kept read-only here for
            # reliability across Streamlit versions. The explicit selector
            # below provides deterministic interaction and avoids fragile
            # dataframe-selection APIs.
            codes = view["Equipment Code"].astype(str).tolist()
            labels = {}
            for _, rr in view.iterrows():
                name = str(rr.get("Equipment", "") or "").strip()
                labels[str(rr["Equipment Code"])] = f"{rr['Equipment Code']}  ·  {name if name else 'Equipment description not yet mapped'}"
            selected = st.selectbox(
                "👆 Select equipment for engineering review",
                codes,
                format_func=lambda x: labels.get(x, x),
                key="priority_equipment_v2"
            )
            r = view[view["Equipment Code"] == selected].iloc[0]

            # ---- Selected equipment decision card ---------------------------
            st.markdown("### 🧩 Selected Equipment")
            st.markdown(
                f'<div class="selected-equipment-head"><div><span class="selected-code">{r["Equipment Code"]}</span><span class="selected-name">{r["Equipment"] if str(r["Equipment"]).strip() else "Equipment description not yet mapped"}</span></div><div class="selected-priority">{r["Screening Priority"]}</div></div>',
                unsafe_allow_html=True,
            )

            a, b, c, d, e = st.columns(5)
            a.metric("Health Score", f"{r['Health']}/100")
            b.metric("Condition", str(r["Condition"]))
            c.metric("Priority", str(r["Screening Priority"]))
            d.metric("Criticality", str(r["Criticality"]))
            e.metric("Risk", str(r["Risk"]))

            finding = f"{r['Top Tag']} — {r['Top Parameter']} → {r['Top Finding']} | Trend {r['Top Trend']} ({r['Top Shift %']:+.1f}%)."
            if r["Screening Priority"] == "P1":
                st.error(f"🔴 **Immediate engineering review:** {finding}")
            elif r["Screening Priority"] == "P2":
                st.warning(f"🟠 **Plan engineering inspection:** {finding}")
            elif r["Screening Priority"] == "P3":
                st.info(f"🟡 **Monitor deterioration:** {finding}")
            else:
                st.success("🟢 **Routine:** no abnormal parameter currently identified by the historical screening engine.")

            left, right = st.columns([1.1, 1])
            with left:
                st.markdown("#### 🔧 Recommended Maintenance Decision")
                st.markdown(f'<div class="decision-card"><b>{r["Maintenance Decision"]}</b><br><span>Suggested check: {r["Top Action"]}</span></div>', unsafe_allow_html=True)
            with right:
                st.markdown("#### 📊 Engineering Evidence")
                st.markdown(
                    f'<div class="evidence-card"><b>{r["Top Parameter"]}</b><br>Trend: <b>{r["Top Trend"]}</b> · Shift: <b>{r["Top Shift %"]:+.1f}%</b><br>Parameters: <b>{int(r["Parameters"])}</b> · Abnormal: <b>{int(r["Deteriorating"] + r["Attention"] + r["Critical"])}</b></div>',
                    unsafe_allow_html=True,
                )

            b1, b2, b3 = st.columns(3)
            if b1.button("📈 Open Problem Trend", key=f"priority_open_trend_v2_{selected}", width='stretch'):
                st.session_state["trend_equipment_from_priority"] = selected
                st.session_state["trend_tag_from_priority"] = r["Top Tag"]
                st.success(f"Trend prepared for {r['Top Tag']}. Open **Engineering Trend** from Navigation.")
            if b2.button("🛠️ Send to Action Center", key=f"priority_open_action_v2_{selected}", width='stretch'):
                fdf = build_action_findings(master[master["Equipment Code"] == selected], df, criticality_df)
                if not fdf.empty:
                    st.session_state["action_selected_finding"] = str(fdf.iloc[0]["Finding ID"])
                    st.success("Finding prepared for the Engineering Action Center. Open it from Navigation.")
                else:
                    st.info("No abnormal finding is currently available for this equipment.")
            if b3.button("🔍 Open Equipment Health", key=f"priority_open_health_v2_{selected}", width='stretch'):
                st.session_state["health_selected_eq"] = selected
                st.success(f"Equipment Health prepared for {selected}. Open **Equipment Health** from Navigation.")

        # ---- Criticality master tools ---------------------------------------
        with st.expander("📋 Equipment Criticality Master", expanded=False):
            st.write("Download this template, complete it from the approved engineering/reliability assessment, then upload the validated CSV above.")
            template = criticality_template(master)
            st.download_button(
                "⬇️ Download Criticality Master Template",
                template.to_csv(index=False).encode("utf-8"),
                "equipment_criticality_master_template.csv",
                "text/csv",
                key="criticality_template_download_v2"
            )

        st.caption(
            "Method: historical P05–P95 behaviour + recent-vs-prior shift + sustained outside-baseline fraction + mapping confidence + validated equipment criticality when supplied. Screening is an engineering decision-support indicator, not an alarm/trip or failure prediction."
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
            st.dataframe(q[["Equipment Code","Equipment","PLC Tag","Parameter","Condition","Priority","Status","PIC","Target Date","Shift %"]],width='stretch',hide_index=True,height=360)
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
            d1.download_button("Download Engineering Action Log (.csv)",export_df.to_csv(index=False).encode("utf-8"),"OPP_engineering_action_log.csv","text/csv",width='stretch')
            uploaded_actions=d2.file_uploader("Restore Action Log (.csv)",type=["csv"],key="action_restore")
            if uploaded_actions is not None:
                restored=pd.read_csv(uploaded_actions).fillna("")
                if "Finding ID" not in restored.columns: st.error("Action Log must contain the Finding ID column.")
                else:
                    for _,rr in restored.iterrows(): store[str(rr["Finding ID"])]=rr.to_dict()
                    st.session_state["engineering_actions"]=store; st.success(f"Restored {len(restored):,} engineering action record(s).")

elif page == "Tag Master":
    st.markdown('<div class="opp-page-title">⌑ Tag Master</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="opp-page-sub">Satu tempat untuk mengendalikan identitas PLC tag, memvalidasi Instrument Master, dan menemukan gap identifikasi. Instrument Master menjadi referensi identitas; PLC Historian tetap menjadi sumber nilai.</div>',
        unsafe_allow_html=True,
    )

    tab_review, tab_plc, tab_instrument, tab_gap = st.tabs(["MAPPING REVIEW", "PEMETAAN PLC TAG", "INSTRUMENT MASTER", "GAP IDENTIFIKASI"])

    with tab_review:
        st.markdown("#### Engineering Mapping Review")
        st.caption("Engineer mengonfirmasi identitas PLC tag terhadap equipment, parameter, dan unit. Raw PLC Historian tidak diubah; hasil konfirmasi disimpan sebagai Engineering Mapping Master.")

        mapping_store = _mapping_store_init(engineering_mapping)
        identification_report = build_tag_identification_report(df, instrument_master)
        queue = build_mapping_review_queue(master, identification_report, mapping_store, instrument_master)
        mapping_df = engineering_mapping_dataframe(mapping_store)

        exact_all = int((identification_report["Identification Status"] == "EXACT MATCH").sum()) if not identification_report.empty else 0
        possible_all = int((identification_report["Identification Status"] == "POSSIBLE MATCH").sum()) if not identification_report.empty else 0
        review_all = int((identification_report["Identification Status"] == "REVIEW REQUIRED").sum()) if not identification_report.empty else 0
        notfound_all = int((identification_report["Identification Status"] == "NOT FOUND").sum()) if not identification_report.empty else 0
        confirmed_n = int(mapping_df["Mapping Status"].isin(["CONFIRMED", "VERIFIED"]).sum()) if not mapping_df.empty else 0
        candidate_n = int(queue["Mapping Candidate Code"].astype(str).str.strip().ne("").sum()) if not queue.empty and "Mapping Candidate Code" in queue.columns else 0
        pending_n = len(queue)
        manual_n = possible_all + review_all + notfound_all - exact_all*0

        m1,m2,m3,m4,m5,m6 = st.columns(6, gap="small")
        m1.metric("PLC TAGS", f"{len(identification_report):,}")
        m2.metric("AUTO IDENTIFIED", f"{exact_all:,}")
        m3.metric("POSSIBLE", f"{possible_all:,}")
        m4.metric("REVIEW", f"{review_all:,}")
        m5.metric("NOT FOUND", f"{notfound_all:,}")
        m6.metric("ENGINEER CONFIRMED", f"{confirmed_n:,}")

        if pending_n:
            st.info(f"{pending_n:,} tag masuk review manual. {candidate_n:,} sudah memiliki kandidat equipment dari Tag Master / Equipment Pattern; sisanya perlu identifikasi lebih lanjut.")
        else:
            st.success("Tidak ada PLC tag yang tersisa di Engineering Mapping Review.")

        if not queue.empty:
            qc1,qc2,qc3 = st.columns([1.5, 1, 1])
            status_filter = qc1.selectbox("Review Queue", ["ALL PENDING", "REVIEW REQUIRED", "POSSIBLE MATCH", "NOT FOUND", "EXACT MATCH"], key="tm_review_status")
            search_review = qc2.text_input("Cari PLC Tag", key="tm_review_search")
            show_skipped = qc3.checkbox("Tampilkan SKIPPED", value=False, key="tm_show_skipped")

            qview = queue.copy()
            if status_filter != "ALL PENDING":
                qview = qview[qview["Identification Status"] == status_filter]
            if search_review:
                qview = qview[qview["PLC Tag"].str.contains(search_review, case=False, na=False, regex=False)]

            skipped = mapping_df[mapping_df["Mapping Status"] == "SKIPPED"] if not mapping_df.empty else pd.DataFrame()
            if show_skipped and not skipped.empty:
                st.markdown("##### Previously Skipped")
                st.dataframe(skipped[[c for c in ["PLC Tag","Equipment Code","Equipment","Parameter","Unit","Identification Status","Verified By","Verified Date"] if c in skipped.columns]], width="stretch", height=180, hide_index=True)

            if not qview.empty:
                tags = qview["PLC Tag"].tolist()
                selected_tag = st.selectbox("Pilih PLC Tag untuk direview", tags, key="tm_review_tag")
                item = qview[qview["PLC Tag"] == selected_tag].iloc[0]

                candidate_tag = str(item.get("Candidate Tag", "")).strip()
                im_candidate = instrument_master[instrument_master["Tag No"].astype(str).map(_tm_norm_tag) == _tm_norm_tag(candidate_tag)].copy() if candidate_tag and not instrument_master.empty else pd.DataFrame()
                imr = im_candidate.iloc[0] if not im_candidate.empty else pd.Series(dtype=object)

                st.markdown('<div class="opp-note"><b>SYSTEM RECOMMENDATION</b><br>' +
                            f'PLC Tag: <b>{selected_tag}</b> &nbsp; | &nbsp; Identification: <b>{item["Identification Status"]}</b> &nbsp; | &nbsp; Score: <b>{float(item["Score"]):.3f}</b><br>' +
                            f'Candidate Instrument: <b>{candidate_tag or "Tidak ada"}</b><br>' +
                            f'Evidence: {item["Reason"] or "Belum ada evidence yang cukup."}</div>', unsafe_allow_html=True)

                mapping_candidate_code = str(item.get("Mapping Candidate Code", "") or "").strip()
                mapping_candidate_name = str(item.get("Mapping Candidate Equipment", "") or "").strip()
                mapping_candidate_source = str(item.get("Mapping Candidate Source", "") or "").strip()
                mapping_candidate_evidence = str(item.get("Mapping Candidate Evidence", "") or "").strip()
                if mapping_candidate_code:
                    st.markdown(
                        f'<div class="opp-note"><b>ENGINEERING EQUIPMENT CANDIDATE</b><br>'
                        f'<b>{mapping_candidate_code}</b>' + (f' — {mapping_candidate_name}' if mapping_candidate_name else '') +
                        f'<br>Source: <b>{mapping_candidate_source}</b> · Evidence: {mapping_candidate_evidence}</div>',
                        unsafe_allow_html=True)

                if not imr.empty:
                    ec1,ec2,ec3,ec4 = st.columns(4, gap="small")
                    ec1.metric("Equipment Candidate", str(imr.get("Derived Equipment Code", "") or "—"))
                    ec2.metric("Parameter", str(imr.get("Suggested Parameter", "") or "—"))
                    ec3.metric("Unit", str(imr.get("Unit", "") or "—"))
                    ec4.metric("Instrument", str(imr.get("Instrument Type", "") or "—"))
                    with st.expander("Lihat evidence Instrument Master", expanded=False):
                        st.dataframe(im_candidate[[c for c in ["Tag No","Service","Area","Derived Equipment Code","Instrument Type","IO Type","Suggested Parameter","Unit","P&ID"] if c in im_candidate.columns]], width="stretch", hide_index=True)

                eq_ref = master[["Equipment Code","Equipment","Area"]].copy() if not master.empty else pd.DataFrame(columns=["Equipment Code","Equipment","Area"])
                eq_ref = eq_ref[eq_ref["Equipment Code"].astype(str).str.strip().ne("")].drop_duplicates("Equipment Code")
                eq_options = ["KEEP / USE CURRENT"] + [_mapping_candidate_label(r["Equipment Code"], r["Equipment"]) for _,r in eq_ref.sort_values("Equipment Code").iterrows()] + ["NEW / NOT IN EQUIPMENT MASTER"]

                def_eq = (str(imr.get("Derived Equipment Code", "") or "").strip() if not imr.empty else "") or str(item.get("Mapping Candidate Code", "") or item.get("Current Equipment Code", "") or "").strip()
                def_label = next((x for x in eq_options if x.startswith(def_eq + " — ")), "KEEP / USE CURRENT") if def_eq else "KEEP / USE CURRENT"
                default_eq_index = eq_options.index(def_label) if def_label in eq_options else 0

                parameter_vocab = sorted(set([str(x).strip() for x in master["Suggested Parameter"].tolist() if str(x).strip()] + ([str(imr.get("Suggested Parameter", "")).strip()] if not imr.empty else [])))
                unit_vocab = sorted(set([str(x).strip() for x in master["Suggested Unit"].tolist() if str(x).strip()] + ([str(imr.get("Unit", "")).strip()] if not imr.empty else [])))
                current_saved = mapping_store.get(selected_tag, {})

                with st.form("engineering_mapping_review_form"):
                    f1,f2 = st.columns([1.25, 1], gap="medium")
                    eq_choice = f1.selectbox("Equipment", eq_options, index=default_eq_index, key="tm_map_eq")
                    parameter_default = str(current_saved.get("Parameter", "") or (imr.get("Suggested Parameter", "") if not imr.empty else "") or item.get("Current Parameter", ""))
                    p_options = ["— SELECT PARAMETER —"] + [x for x in parameter_vocab if x != parameter_default]
                    if parameter_default: p_options.insert(1, parameter_default)
                    parameter_choice = f2.selectbox("Parameter", p_options, index=1 if parameter_default else 0, key="tm_map_param")
                    f3,f4 = st.columns([1.25, 1], gap="medium")
                    unit_default = str(current_saved.get("Unit", "") or (imr.get("Unit", "") if not imr.empty else "") or item.get("Current Unit", ""))
                    unit_choice = f3.selectbox("Unit", ["— SELECT / VERIFY UNIT —"] + [x for x in unit_vocab if x != unit_default], index=1 if unit_default else 0, key="tm_map_unit")
                    area_default = str(current_saved.get("Area", "") or (imr.get("Area", "") if not imr.empty else "") or item.get("Current Equipment Code", ""))
                    area_options = sorted(set([str(x).strip() for x in master["Area"].tolist() if str(x).strip()] + ([str(imr.get("Area", "")).strip()] if not imr.empty else [])))
                    area_choice = f4.selectbox("Area", ["— AUTO / VERIFY —"] + area_options, index=(area_options.index(area_default)+1 if area_default in area_options else 0), key="tm_map_area")

                    new_code = ""
                    new_name = ""
                    if eq_choice == "NEW / NOT IN EQUIPMENT MASTER":
                        n1,n2 = st.columns(2)
                        new_code = n1.text_input("New Equipment Code", value=str(current_saved.get("Equipment Code", "") or def_eq), key="tm_new_eq_code")
                        new_name = n2.text_input("Equipment Name", value=str(current_saved.get("Equipment", "") or (imr.get("Service", "") if not imr.empty else "")), key="tm_new_eq_name")

                    verifier = st.text_input("Engineer / Verifier", value=str(current_saved.get("Verified By", "")), key="tm_map_verifier", placeholder="Nama engineer")
                    evidence = st.text_area("Engineering Evidence / Reason", value=str(current_saved.get("Evidence", "") or item.get("Reason", "")), key="tm_map_evidence", height=80)
                    b1,b2,b3 = st.columns(3)
                    confirm = b1.form_submit_button("✓ CONFIRM MAPPING", type="primary", width="stretch")
                    change = b2.form_submit_button("✎ SAVE AS REVIEW", width="stretch")
                    skip = b3.form_submit_button("→ SKIP", width="stretch")

                action = "CONFIRMED" if confirm else ("REVIEW REQUIRED" if change else ("SKIPPED" if skip else ""))
                if action:
                    eq_code, eq_name = _mapping_parse_candidate(eq_choice)
                    if eq_choice == "KEEP / USE CURRENT":
                        eq_code = str(item.get("Current Equipment Code", "")).strip() or def_eq
                        eq_name = str(item.get("Current Equipment", "")).strip()
                    elif eq_choice == "NEW / NOT IN EQUIPMENT MASTER":
                        eq_code, eq_name = new_code.strip(), new_name.strip()
                    if eq_choice != "NEW / NOT IN EQUIPMENT MASTER" and eq_name == "" and eq_code:
                        hit = eq_ref[eq_ref["Equipment Code"].astype(str) == eq_code]
                        if not hit.empty: eq_name = str(hit.iloc[0]["Equipment"] or "")
                    if action == "CONFIRMED" and not verifier.strip():
                        st.error("Isi Engineer / Verifier sebelum CONFIRM MAPPING.")
                    elif action == "CONFIRMED" and (not eq_code or parameter_choice.startswith("—") or unit_choice.startswith("—")):
                        st.error("Equipment, Parameter, dan Unit harus terisi sebelum mapping dikonfirmasi.")
                    else:
                        area_final = area_choice if not area_choice.startswith("—") else (str(imr.get("Area", "") or "").strip() if not imr.empty else "")
                        mapping_store[selected_tag] = {
                            "PLC Tag": selected_tag, "Equipment Code": eq_code, "Equipment": eq_name, "Area": area_final,
                            "Parameter": "" if parameter_choice.startswith("—") else parameter_choice,
                            "Unit": "" if unit_choice.startswith("—") else unit_choice,
                            "Mapping Status": action, "Identification Status": str(item.get("Identification Status", "")),
                            "Confidence": str(item.get("Score", "")), "Evidence": evidence.strip(),
                            "Verified By": verifier.strip(), "Verified Date": pd.Timestamp.now(tz=EH_SITE_TZ).strftime("%Y-%m-%d %H:%M %Z"),
                            "Source": "Engineer Mapping Review"
                        }
                        st.session_state["engineering_mapping_master"] = mapping_store
                        st.success(f"{selected_tag}: {action}.")
                        st.rerun()

            else:
                st.info("Tidak ada item untuk filter review ini.")

        st.markdown("#### Engineering Mapping Master")
        if mapping_df.empty:
            st.caption("Belum ada mapping yang disimpan oleh engineer.")
        else:
            st.dataframe(mapping_df, width="stretch", height=320, hide_index=True)

        ex1,ex2 = st.columns(2, gap="medium")
        export_bytes = mapping_df.to_csv(index=False).encode("utf-8-sig") if not mapping_df.empty else pd.DataFrame(columns=ENGINEERING_MAPPING_COLUMNS).to_csv(index=False).encode("utf-8-sig")
        ex1.download_button("Download Engineering Mapping Master (.csv)", export_bytes, "engineering_mapping_master.csv", "text/csv", key="tm_download_mapping_master", width="stretch")
        ex2.download_button("Download Pending Review Queue (.csv)", queue.to_csv(index=False).encode("utf-8-sig") if not queue.empty else b"", "engineering_mapping_review_queue.csv", "text/csv", key="tm_download_mapping_queue", width="stretch")
        st.caption("Deployment note: untuk persistensi lintas redeploy di Streamlit Community Cloud, file hasil export `engineering_mapping_master.csv` dapat ditempatkan kembali ke folder `config/` repository. Raw PLC data dan file historis tidak disentuh oleh workflow ini.")

    with tab_plc:
        st.markdown("#### PLC Tag Mapping")
        st.caption("Identification Engine melakukan exact match terlebih dahulu. Candidate fuzzy hanya ditampilkan sebagai POSSIBLE MATCH / REVIEW REQUIRED dan tidak otomatis dianggap sebagai mapping final.")
        c1,c2,c3,c4 = st.columns([1.45, .8, .9, 1.0], gap="small")
        q = c1.text_input("Cari tag / service / equipment / parameter", key="tm_search")
        area_options = ["All"] + sorted([str(x) for x in master["Area"].unique() if str(x).strip()], key=str)
        area = c2.selectbox("Area", area_options, key="tm_area")
        conf = c3.selectbox("Confidence", ["All", "High", "Medium", "Low"], key="tm_conf")
        match_filter = c4.selectbox(
            "Status Identifikasi",
            ["All", "EXACT MATCH", "POSSIBLE MATCH", "REVIEW REQUIRED", "NOT FOUND"],
            key="tm_match_v36",
        )

        view = master.copy()
        if q:
            mask = view.astype(str).apply(lambda ss: ss.str.contains(q, case=False, na=False, regex=False)).any(axis=1)
            view = view[mask]
        if area != "All":
            view = view[view["Area"].astype(str) == area]
        if conf != "All":
            view = view[view["Confidence"].astype(str) == conf]
        if match_filter != "All":
            view = view[view["Instrument Master Match"].astype(str) == match_filter]

        display_cols = [
            "Area","Equipment Code","Equipment","PLC Tag","Suggested Parameter","Suggested Unit",
            "Instrument Master Match","Identification Candidate","Identification Score","Identification Reason",
            "Instrument Service","Instrument Type Master","Instrument IO Type","Instrument Unit Master",
            "Metadata Validation","Metadata Validation Detail","Confidence"
        ]
        display_cols = [c for c in display_cols if c in view.columns]
        st.dataframe(view[display_cols], width="stretch", height=600, hide_index=True)
        st.download_button(
            "Download PLC Tag Mapping CSV",
            master.to_csv(index=False).encode("utf-8-sig"),
            "OPP_PLC_Tag_Mapping_Intelligent.csv",
            "text/csv",
            key="tm_download_plc_v36",
        )
        st.info("Catatan: POSSIBLE MATCH adalah candidate untuk review engineer. REVIEW REQUIRED berarti sistem menemukan indikasi yang belum cukup unik/aman untuk dipilih otomatis. NOT FOUND berarti belum ada candidate yang cukup kuat.")

    with tab_instrument:
        st.markdown("#### Instrument Master")
        if instrument_master.empty:
            st.warning("Instrument Master belum tersedia. Tambahkan `config/instrument_master.csv` ke repository.")
        else:
            im_view = instrument_master.copy()
            c1,c2,c3 = st.columns(3)
            search_im = c1.text_input("Cari Tag / Service / Type", key="im_search")
            category_values = sorted([str(x) for x in im_view["Engineering Category"].unique() if str(x).strip()], key=str)
            category_im = c2.selectbox("Engineering Category", ["All"] + category_values, key="im_category")
            area_values = sorted([str(x) for x in im_view["Area"].unique() if str(x).strip()], key=str)
            area_im = c3.selectbox("Area", ["All"] + area_values, key="im_area")
            if search_im:
                mask = im_view.astype(str).apply(lambda ss: ss.str.contains(search_im, case=False, na=False, regex=False)).any(axis=1)
                im_view = im_view[mask]
            if category_im != "All":
                im_view = im_view[im_view["Engineering Category"].astype(str) == category_im]
            if area_im != "All":
                im_view = im_view[im_view["Area"].astype(str) == area_im]
            display_cols = [
                "Tag No","Service","Area","Derived Equipment Code","Instrument Type","IO Type",
                "Suggested Parameter","Unit","Engineering Category","P&ID","Manufacturer","Model No",
                "Range","Calibration Range","Remarks"
            ]
            display_cols = [c for c in display_cols if c in im_view.columns]
            st.dataframe(im_view[display_cols], width="stretch", height=600, hide_index=True)
            st.download_button(
                "Download Instrument Master CSV",
                instrument_master.to_csv(index=False).encode("utf-8-sig"),
                "OPP_Instrument_Master.csv",
                "text/csv",
                key="tm_download_instrument_v36",
            )

    with tab_gap:
        st.markdown("#### Identification Gap")
        gap = instrument_master_gap_report(df, instrument_master)
        report = gap.get("identification", pd.DataFrame())
        total_im = len(gap["instrument_tags"])
        total_plc = len(gap["plc_tags"])
        exact_n = int((report["Identification Status"] == "EXACT MATCH").sum()) if not report.empty else 0
        possible_n = int((report["Identification Status"] == "POSSIBLE MATCH").sum()) if not report.empty else 0
        review_n = int((report["Identification Status"] == "REVIEW REQUIRED").sum()) if not report.empty else 0
        not_found_n = int((report["Identification Status"] == "NOT FOUND").sum()) if not report.empty else 0

        g1,g2,g3,g4,g5 = st.columns(5, gap="small")
        g1.metric("PLC Tags", f"{total_plc:,}")
        g2.metric("Exact Match", f"{exact_n:,}")
        g3.metric("Possible Match", f"{possible_n:,}")
        g4.metric("Review Required", f"{review_n:,}")
        g5.metric("Not Found", f"{not_found_n:,}")

        coverage = (exact_n / total_plc * 100) if total_plc else 0
        st.progress(min(1.0, coverage / 100), text=f"Exact identification coverage terhadap PLC Historian: {coverage:.1f}%")

        st.markdown("##### Prioritas Review")
        review_view = report[report["Identification Status"].isin(["POSSIBLE MATCH","REVIEW REQUIRED","NOT FOUND"])].copy() if not report.empty else pd.DataFrame()
        if not review_view.empty:
            status_order = {"REVIEW REQUIRED":1,"POSSIBLE MATCH":2,"NOT FOUND":3}
            review_view["_order"] = review_view["Identification Status"].map(status_order).fillna(9)
            review_view = review_view.sort_values(["_order","Score"], ascending=[True,False]).drop(columns="_order")
            st.dataframe(review_view, width="stretch", height=360, hide_index=True)
        else:
            st.success("Semua PLC tag memiliki exact identification yang aman terhadap Instrument Master.")

        left,right = st.columns(2, gap="medium")
        with left:
            st.markdown("##### PLC Tag yang belum memiliki exact match")
            if not review_view.empty:
                st.dataframe(review_view[["PLC Tag","Identification Status","Candidate Tag","Score","Reason"]], width="stretch", height=300, hide_index=True)
            else:
                st.success("Tidak ada PLC tag yang perlu direview.")
        with right:
            st.markdown("##### Instrument belum muncul di PLC Historian")
            if gap["instrument_only"]:
                rows = instrument_master[instrument_master["Normalized Tag"].isin(gap["instrument_only"])][
                    ["Tag No","Service","Area","Instrument Type","IO Type","Engineering Category"]
                ].copy()
                st.dataframe(rows, width="stretch", height=300, hide_index=True)
            else:
                st.success("Semua Instrument Master tag sudah ditemukan di PLC Historian.")

        if not gap["duplicate_tags"].empty:
            with st.expander("⚠️ Duplicate Tag No di Instrument Master", expanded=False):
                st.dataframe(gap["duplicate_tags"].drop(columns=["_Normalized"], errors="ignore"), width="stretch", hide_index=True)

        st.markdown("##### Validasi Metadata Engineering")
        metadata_view = master[[
            "PLC Tag","Instrument Master Match","Suggested Parameter","Suggested Unit",
            "Instrument Master Parameter","Instrument Unit Master","Metadata Validation","Metadata Validation Detail"
        ]].copy() if not master.empty else pd.DataFrame()
        metadata_review = metadata_view[metadata_view["Metadata Validation"].isin(["REVIEW REQUIRED","INCOMPLETE"])].copy() if not metadata_view.empty else pd.DataFrame()
        if metadata_review.empty:
            st.success("Tidak ada konflik metadata parameter/unit/type/IO yang terdeteksi pada mapping yang tersedia.")
        else:
            st.dataframe(metadata_review, width="stretch", height=300, hide_index=True)


elif page == "Engineering Trend":
    st.subheader("Engineering Trend — Equipment View")
    st.caption("Select an equipment code to display all mapped PLC parameters together. Equipment identity is canonicalized so code variants are grouped under one physical equipment.")
    area_options = ["All"] + sorted([x for x in master["Area"].unique() if str(x).strip()])
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
                    st.dataframe(pd.DataFrame(summary), width='stretch', height=300)
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
    st.markdown('<div class="opp-page-title">⇧ Daily PLC Data Import</div>', unsafe_allow_html=True)
    st.markdown('<div class="opp-page-sub">Upload daily PLC Excel exports one file at a time. Each file is validated and committed directly to the historical database before the next file is selected.</div>', unsafe_allow_html=True)
    st.markdown('<div class="opp-note"><b>Robust import workflow:</b> Select ONE Excel file → Validate → Append to database → Select the next file. This avoids loading many large Excel workbooks into browser/server memory at the same time.</div>', unsafe_allow_html=True)

    import gc

    # IMPORTANT:
    # Streamlit's multi-file uploader keeps the selected UploadedFile objects in memory.
    # With large PLC exports, selecting 18 files can therefore exhaust Community Cloud
    # memory before our Python code even gets a chance to process them sequentially.
    # This page deliberately uses a SINGLE-file uploader. Each file is processed and
    # committed to SQLite, then the uploader is reset for the next file.
    uploaded = st.file_uploader(
        "Select one daily PLC export (.xlsx)",
        type=["xlsx"],
        accept_multiple_files=False,
        key="daily_plc_import_v14",
        help="For a large historical batch, import the files one-by-one. Each successful file is written to SQLite before you select the next file."
    )

    if uploaded is not None:
        file_name = Path(uploaded.name).name
        file_size_mb = (int(getattr(uploaded, "size", 0) or 0) / (1024 * 1024))
        st.info(f"📄 **{file_name}**  •  {file_size_mb:.1f} MB  •  only this workbook will be processed in memory.")

        c1, c2 = st.columns([1, 1], gap="small")
        validate_one = c1.button("🔎 Validate File", type="secondary", width='stretch', key="validate_one_v14")
        import_one = c2.button("✅ Import This File", type="primary", width='stretch', key="import_one_v14")

        if validate_one or import_one:
            import tempfile, os
            tmp_path = None
            try:
                # Copy the uploaded workbook to disk first, then release the Streamlit
                # buffer as soon as possible. Only one workbook is ever materialized.
                tmp_dir = ROOT / "data" / "import_staging"
                tmp_dir.mkdir(parents=True, exist_ok=True)
                suffix = Path(file_name).suffix.lower() or ".xlsx"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=tmp_dir) as tf:
                    tf.write(uploaded.getbuffer())
                    tmp_path = Path(tf.name)

                progress = st.progress(0, text="Reading Excel workbook…")
                incoming = pd.read_excel(tmp_path, engine="openpyxl")
                progress.progress(0.45, text="Validating ArchiveTime…")

                result = {
                    "File": file_name,
                    "Status": "Ready",
                    "Rows": int(len(incoming)),
                    "New": 0,
                    "Existing": 0,
                    "Invalid": 0,
                    "Duplicate in file": 0,
                    "First Timestamp": pd.NaT,
                    "Last Timestamp": pd.NaT,
                }

                if incoming.empty:
                    result["Status"] = "Empty file"
                elif "ArchiveTime" not in incoming.columns:
                    result["Status"] = "Missing ArchiveTime"
                    result["Invalid"] = int(len(incoming))
                else:
                    incoming["ArchiveTime"] = pd.to_datetime(incoming["ArchiveTime"], errors="coerce")
                    result["Invalid"] = int(incoming["ArchiveTime"].isna().sum())
                    valid = incoming.dropna(subset=["ArchiveTime"]).copy()
                    result["First Timestamp"] = valid["ArchiveTime"].min() if not valid.empty else pd.NaT
                    result["Last Timestamp"] = valid["ArchiveTime"].max() if not valid.empty else pd.NaT
                    before = len(valid)
                    valid = valid.drop_duplicates("ArchiveTime", keep="last")
                    result["Duplicate in file"] = int(before - len(valid))

                    # Query the DB directly instead of loading the complete history DataFrame.
                    _init_history_db()
                    conn = _db_connect()
                    try:
                        existing = {
                            row[0] for row in conn.execute(
                                "SELECT archive_time FROM plc_history"
                            ).fetchall()
                        }
                    finally:
                        conn.close()

                    valid_keys = valid["ArchiveTime"].map(lambda x: pd.Timestamp(x).isoformat())
                    new_mask = ~valid_keys.isin(existing)
                    result["New"] = int(new_mask.sum())
                    result["Existing"] = int((~new_mask).sum())

                    if result["New"] == 0 and result["Existing"] > 0:
                        result["Status"] = "Already in history"
                    elif result["New"] == 0:
                        result["Status"] = "No valid rows"

                    if import_one and result["New"] > 0:
                        progress.progress(0.70, text="Writing new rows to SQLite…")
                        new_rows = valid.loc[new_mask].copy()
                        written, _ = persist_daily_import(new_rows, file_name)
                        progress.progress(1.0, text="Import complete")

                        load_history.clear()
                        recent_import_log.clear()
                        st.session_state["import_last_result_v14"] = {
                            **result,
                            "Imported": int(written),
                        }
                        st.success(f"✅ **{written:,} new rows** imported from **{file_name}**.")
                        st.caption("The historical database has been updated. Dashboard, Equipment Health and Engineering Trend will use the refreshed history on the next rerun.")

                        del new_rows
                    elif import_one and result["New"] == 0:
                        progress.progress(1.0, text="Nothing new to import")
                        st.warning(f"No new timestamps were imported from **{file_name}**. The valid records are already in history.")
                    else:
                        progress.progress(1.0, text="Validation complete")

                # Show one-file validation result without retaining the workbook.
                result_view = pd.DataFrame([result])
                for c in ["First Timestamp", "Last Timestamp"]:
                    result_view[c] = pd.to_datetime(result_view[c], errors="coerce").dt.strftime("%d %b %Y %H:%M").fillna("—")
                st.markdown("#### File Validation Result")
                st.dataframe(result_view, width='stretch', hide_index=True)

                if validate_one and not import_one:
                    if result.get("New", 0) > 0:
                        st.success(f"Ready to import: **{result['New']:,} new timestamp row(s)**.")
                    else:
                        st.info("This file contains no new timestamp records for the current database.")

                # Small preview only; the full workbook is not retained.
                if tmp_path and tmp_path.exists():
                    try:
                        preview = pd.read_excel(tmp_path, engine="openpyxl", nrows=10)
                        with st.expander("Preview first 10 rows", expanded=False):
                            st.dataframe(preview, width='stretch', hide_index=True)
                        del preview
                    except Exception:
                        pass

                del incoming
                gc.collect()

            except Exception as exc:
                st.error(f"❌ Could not process **{file_name}**: {type(exc).__name__}: {exc}")
            finally:
                if tmp_path is not None:
                    try:
                        tmp_path.unlink(missing_ok=True)
                    except Exception:
                        pass
                gc.collect()

    st.markdown("#### Batch Import Guidance")
    g1, g2, g3 = st.columns(3, gap="small")
    g1.markdown('<div class="dashboard-panel"><b>1. Select one file</b><br><span style="color:#667085;font-size:.75rem">Choose the next daily PLC Excel export.</span></div>', unsafe_allow_html=True)
    g2.markdown('<div class="dashboard-panel"><b>2. Validate / Import</b><br><span style="color:#667085;font-size:.75rem">The workbook is processed and released from memory.</span></div>', unsafe_allow_html=True)
    g3.markdown('<div class="dashboard-panel"><b>3. Repeat</b><br><span style="color:#667085;font-size:.75rem">Continue with the next day until the historical batch is complete.</span></div>', unsafe_allow_html=True)

    st.markdown("#### Historical Database Status")
    try:
        db_rows, db_first, db_last, import_count = history_database_stats()
        h1, h2, h3, h4 = st.columns(4, gap="small")
        h1.metric("Historical Rows", f"{db_rows:,}")
        h2.metric("First Timestamp", pd.to_datetime(db_first).strftime("%d %b %Y %H:%M") if db_first else "—")
        h3.metric("Latest Timestamp", pd.to_datetime(db_last).strftime("%d %b %Y %H:%M") if db_last else "—")
        h4.metric("Import Batches", f"{import_count:,}")
        st.caption("SQLite is the single historical source consumed by Dashboard, Equipment Health and Engineering Trend. Re-uploading the same Excel file is safe: existing timestamps are not duplicated.")
        log_df = recent_import_log(8)
        if not log_df.empty:
            with st.expander("🧾 Recent import history", expanded=False):
                st.dataframe(log_df, width='stretch', hide_index=True)
        with st.expander("🗄️ Database details", expanded=False):
            st.code(str(DB_PATH), language="text")
            st.caption("Unique ArchiveTime key • transactional import • import log • compressed row payloads")
    except Exception as exc:
        st.error(f"Unable to read historical database status: {exc}")
