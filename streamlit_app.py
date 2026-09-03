import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import re
from urllib.parse import quote

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
    f'<div><span class="coverage-icon-v19">▣</span><b>{_sidebar_min_dt.strftime("%d %b %Y %H:%M") if _sidebar_min_dt is not None else "—"}</b><small>First Data</small></div>'
    f'<div><span class="coverage-icon-v19">▣</span><b>{_sidebar_max_dt.strftime("%d %b %Y %H:%M") if _sidebar_max_dt is not None else "—"}</b><small>Latest Data</small></div>'
    f'</div>'
    f'<div class="coverage-summary-v19">'
    f'<div class="sidebar-ring-v19" style="--pct:{min(100,max(0,_sidebar_cov)):.1f}%"><span>{_sidebar_cov:.1f}%</span></div>'
    f'<div><div class="coverage-label-v19">Data Coverage</div>'
    f'<div class="coverage-value-v19">{_sidebar_unique_days:,} / {_sidebar_data_days:,} Days</div>'
    f'<div class="coverage-note-v19">Historical data available</div></div>'
    f'</div>',
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
            if st.button("↻ Refresh Data", key="dash_refresh_v15", use_container_width=True):
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
                        st.line_chart(chart, height=185, use_container_width=True)
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
    # Equipment Health v8
    # Visual concept: dark equipment header -> KPI strip -> why flagged ->
    # condition / abnormal parameters / engineering finding -> trend -> actions.
    # The screening/baseline engine above is intentionally preserved.
    # -------------------------------------------------------------------------
    st.markdown('<div class="opp-page-title">🩺 Equipment Health</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="opp-page-sub">Identify abnormal equipment and understand which parameter is driving the screening result.</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="opp-note"><b>Historical screening only:</b> this view detects behaviour outside the historical P05–P95 range. Always validate the signal against OEM limits, operating philosophy, field condition and engineering judgement.</div>',
        unsafe_allow_html=True
    )

    area_options = ["All Areas"] + sorted([x for x in master["Area"].unique() if str(x).strip()])
    selected_area = st.selectbox("Area", area_options, key="health_area")
    area_view = master if selected_area == "All Areas" else master[master["Area"] == selected_area]

    eq_codes = sorted([str(x) for x in area_view["Equipment Code"].unique() if str(x)])
    if not eq_codes:
        st.warning("No canonical equipment code is available for this area.")
    else:
        eq_labels = {}
        for code in eq_codes:
            rr = area_view[area_view["Equipment Code"] == code]["Equipment"].replace("", np.nan).dropna()
            eq_labels[code] = f"{code} — {rr.iloc[0] if len(rr) else 'Equipment description not yet mapped'}"

        default_eq = st.session_state.get("health_selected_eq", eq_codes[0])
        if default_eq not in eq_codes:
            default_eq = eq_codes[0]

        selected_eq = st.selectbox(
            "Equipment", eq_codes, index=eq_codes.index(default_eq),
            format_func=lambda x: eq_labels.get(x, x), key="health_selected_eq"
        )

        ev = area_view[area_view["Equipment Code"] == selected_eq].copy()
        names = ev["Equipment"].replace("", np.nan).dropna()
        eq_name = names.iloc[0] if len(names) else "Equipment description not yet mapped"
        eq_area = str(ev["Area"].iloc[0]) if len(ev) and str(ev["Area"].iloc[0]).strip() else selected_area

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
                tag, meta.get("Suggested Parameter", ""),
                meta.get("Suggested Unit", ""), meta.get("Instrument Type", "")
            )
            rows.append({
                "PLC Tag": tag, "Parameter": parameter, "Unit": unit,
                "Parameter Source": source, **stats,
                "Confidence": str(meta.get("Confidence", "") or "Low"),
                "Action": parameter_action(parameter, tag)
            })

        if not rows:
            st.warning("No sufficient historical numeric data is available for this equipment.")
        else:
            health = pd.DataFrame(rows)
            critical = int((health.Condition == "Critical").sum())
            attention = int((health.Condition == "Attention").sum())
            deteriorating = int((health.Condition == "Deteriorating").sum())
            normal = int((health.Condition == "Normal").sum())
            abnormal = critical + attention + deteriorating

            severity = {"Normal": 0, "Deteriorating": 12, "Attention": 25, "Critical": 50}
            conf_weight = {"High": 1.0, "Medium": .85, "Low": .65}
            health["Penalty"] = [
                min(60, (severity.get(r.Condition, 0) + min(r["Outside Fraction"] * 12, 8))
                    * conf_weight.get(r.Confidence, .65))
                for _, r in health.iterrows()
            ]
            raw_score = 100 - float(health["Penalty"].mean())

            if critical:
                overall, risk, priority, icon, cap = "CRITICAL", "HIGH", "P1", "🔴", 69
            elif attention:
                overall, risk, priority, icon, cap = "ATTENTION", "MEDIUM", "P2", "🟠", 89
            elif deteriorating:
                overall, risk, priority, icon, cap = "DETERIORATING", "MEDIUM-LOW", "P3", "🟡", 94
            else:
                overall, risk, priority, icon, cap = "HEALTHY", "LOW", "P4", "🟢", 100

            score = int(round(max(0, min(cap, raw_score))))

            try:
                last_dt = pd.to_datetime(df["ArchiveTime"], errors="coerce").max()
                last_label = last_dt.strftime("%d %b %Y %H:%M") if pd.notna(last_dt) else "—"
            except Exception:
                last_label = "—"

            condition_class = overall.lower()
            priority_class = priority.lower()

            # Equipment identity banner
            st.markdown(
                f'<div class="health-v8-banner">'
                f'<div class="health-v8-banner-left">'
                f'<div class="health-v8-eq-icon">⚙️</div>'
                f'<div><div class="health-v8-code">{selected_eq}</div>'
                f'<div class="health-v8-name">{eq_name}</div>'
                f'<span class="health-v8-area">{eq_area}</span></div></div>'
                f'<div class="health-v8-banner-right">'
                f'<div class="health-v8-badge">{icon} {priority} · {overall}</div>'
                f'<div class="health-v8-last">🗓 Last data: {last_label}</div>'
                f'</div></div>',
                unsafe_allow_html=True
            )

            # KPI strip
            k1, k2, k3, k4, k5 = st.columns(5, gap="small")
            kpi_items = [
                (k1, "Condition", f"{icon} {overall}", f"{abnormal} parameter(s) require attention", f"condition-{condition_class}"),
                (k2, "Screening Score", f"{score} / 100", "Historical screening indicator", ""),
                (k3, "Abnormal Parameters", f"{abnormal} / {len(health)}", f"{abnormal/max(len(health),1)*100:.1f}% of monitored parameters", ""),
                (k4, "Maintenance Priority", priority, f"{risk} engineering review level", f"priority-{priority_class}"),
                (k5, "Risk Level", risk, "Engineering review level", f"priority-{priority_class}" if risk != "LOW" else "condition-healthy"),
            ]
            for col, label, value, small, cls in kpi_items:
                col.markdown(
                    f'<div class="health-v8-kpi {cls}">'
                    f'<div class="label">{label}</div><div class="value">{value}</div>'
                    f'<div class="small">{small}</div></div>',
                    unsafe_allow_html=True
                )

            # Why flagged
            flagged = health[health["Condition"] != "Normal"].copy()
            if not flagged.empty:
                order = {"Critical": 0, "Attention": 1, "Deteriorating": 2, "Normal": 3}
                flagged["_order"] = flagged["Condition"].map(order).fillna(9)
                sort_cols = [c for c in ["_order", "Deviation Sigma"] if c in flagged.columns]
                flagged = flagged.sort_values(sort_cols, ascending=[True, False][:len(sort_cols)])
                primary = flagged.iloc[0]
                st.markdown(
                    f'<div class="health-v8-why">'
                    f'<div class="health-v8-why-title">⚠ WHY IS THIS EQUIPMENT FLAGGED?</div>'
                    f'{abnormal} parameter(s) require attention. The primary signal is '
                    f'<b>{primary["Parameter"]}</b> ({primary["PLC Tag"]}) showing '
                    f'<b>{primary["Direction"].lower()}</b> behaviour with a recent shift of '
                    f'<b>{primary["Shift %"]:+.1f}%</b>. Historical behaviour is assessed against '
                    f'the P05–P95 range; field verification is recommended before maintenance action.'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # Three-panel diagnostic area
            p_left, p_mid, p_right = st.columns([.9, 1.65, 1.0], gap="small")

            with p_left:
                st.markdown(
                    '<div class="health-v8-panel">'
                    '<div class="health-v8-panel-head">📊 CONDITION DISTRIBUTION</div>'
                    '<div class="health-v8-dist-grid">',
                    unsafe_allow_html=True
                )
                total = max(len(health), 1)
                dist_items = [
                    ("normal", "NORMAL", normal),
                    ("deteriorating", "DETERIORATING", deteriorating),
                    ("attention", "ATTENTION", attention),
                    ("critical", "CRITICAL", critical),
                ]
                for cls, label, n in dist_items:
                    st.markdown(
                        f'<div class="health-v8-dist {cls}"><div class="dlabel">{label}</div>'
                        f'<div class="dvalue">{n:,}</div><div class="dpct">{n/total*100:.0f}% of parameters</div></div>',
                        unsafe_allow_html=True
                    )
                st.markdown('</div></div>', unsafe_allow_html=True)

            with p_mid:
                st.markdown(
                    '<div class="health-v8-panel">'
                    '<div class="health-v8-panel-head">📈 PARAMETER CONDITION <span style="font-weight:600;color:#98a2b3">(Top Abnormal Parameters)</span></div>',
                    unsafe_allow_html=True
                )
                if flagged.empty:
                    st.success("No parameter currently shows a significant historical-behaviour deviation.")
                else:
                    table_rows = []
                    for _, rr in flagged.head(6).iterrows():
                        scls = str(rr["Condition"]).lower()
                        table_rows.append(
                            f'<tr><td><span class="health-v8-status {scls}">{rr["Condition"]}</span></td>'
                            f'<td>{rr["PLC Tag"]}</td><td>{rr["Parameter"]}</td>'
                            f'<td>{rr["Current"]:.3f} {rr["Unit"]}</td>'
                            f'<td>{rr["Baseline Low"]:.3f} – {rr["Baseline High"]:.3f}</td>'
                            f'<td>{rr["Shift %"]:+.1f}%</td><td>{rr["Confidence"]}</td></tr>'
                        )
                    table_html = (
                        '<div class="health-v8-table-wrap"><table class="health-v8-table">'
                        '<thead><tr><th>Status</th><th>PLC Tag</th><th>Parameter</th><th>Current</th>'
                        '<th>Baseline (P05–P95)</th><th>Trend Shift</th><th>Confidence</th></tr></thead>'
                        '<tbody>' + ''.join(table_rows) + '</tbody></table></div>'
                    )
                    st.markdown(table_html, unsafe_allow_html=True)
                    if normal:
                        st.markdown(
                            f'<div style="text-align:center;font-size:.62rem;color:#175cd3;font-weight:750;margin-top:.45rem">'
                            f'⌄ {normal} normal parameter(s) are available in the detailed table below.</div>',
                            unsafe_allow_html=True
                        )
                st.markdown('</div>', unsafe_allow_html=True)

            with p_right:
                st.markdown(
                    '<div class="health-v8-panel">'
                    '<div class="health-v8-panel-head">🔎 ENGINEERING FINDING <span style="font-weight:600;color:#98a2b3">(Primary Signal)</span></div>',
                    unsafe_allow_html=True
                )
                if flagged.empty:
                    st.success("No abnormal finding.")
                    selected_tag = None
                else:
                    options = flagged["PLC Tag"].tolist()
                    selected_tag = st.selectbox(
                        "Problem parameter", options,
                        format_func=lambda x: f"{x} — {flagged.loc[flagged['PLC Tag']==x,'Parameter'].iloc[0]}",
                        key=f"problem_tag_{selected_eq}"
                    )
                    r = flagged[flagged["PLC Tag"] == selected_tag].iloc[0]
                    cond = str(r["Condition"])
                    status_icon = "🔴" if cond == "Critical" else "🟠" if cond == "Attention" else "🟡"
                    st.markdown(
                        f'<div class="health-v8-finding">'
                        f'<div class="health-v8-finding-title">{status_icon} {selected_tag} — {r["Parameter"]}</div>'
                        f'<div class="health-v8-pills">'
                        f'<span class="health-v8-pill">Condition: {cond}</span>'
                        f'<span class="health-v8-pill">Trend: {r["Direction"]} ({r["Shift %"]:+.1f}%)</span>'
                        f'<span class="health-v8-pill">Confidence: {r["Confidence"]}</span>'
                        f'</div>'
                        f'<div class="health-v8-reco"><b>🛠 ENGINEERING RECOMMENDATION</b><br>{r["Action"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                st.markdown('</div>', unsafe_allow_html=True)

            # Detailed normal parameters, kept collapsible so the abnormal signal remains primary.
            if not flagged.empty and normal:
                with st.expander(f"📋 Show {normal} normal parameter(s)", expanded=False):
                    normal_table = health[health["Condition"] == "Normal"][
                        ["PLC Tag", "Parameter", "Unit", "Current", "Baseline Low", "Baseline High", "Direction", "Confidence"]
                    ].copy()
                    for c in ["Current", "Baseline Low", "Baseline High"]:
                        normal_table[c] = normal_table[c].round(3)
                    st.dataframe(normal_table, use_container_width=True, hide_index=True)

            # Problem trend
            if selected_tag is not None:
                r = flagged[flagged["PLC Tag"] == selected_tag].iloc[0]
                trend = df[["ArchiveTime", selected_tag]].copy() if selected_tag in df.columns else pd.DataFrame()
                if not trend.empty:
                    trend[selected_tag] = pd.to_numeric(trend[selected_tag], errors="coerce")
                    trend = trend.dropna().sort_values("ArchiveTime").set_index("ArchiveTime")
                    if len(trend):
                        plot_df = pd.DataFrame({
                            "Current Value": trend[selected_tag],
                            "Historical P05": float(r["Baseline Low"]),
                            "Historical P95": float(r["Baseline High"]),
                        }, index=trend.index)

                        st.markdown(
                            '<div class="health-v8-trend-panel">'
                            f'<div class="health-v8-trend-head">📈 PROBLEM TREND <span style="font-weight:600;color:#98a2b3">({r["Parameter"]})</span></div>'
                            '<div class="health-v8-trend-sub">Current signal versus historical P05–P95 screening range.</div>',
                            unsafe_allow_html=True
                        )
                        st.line_chart(plot_df, height=245, use_container_width=True)

                        t1, t2, t3 = st.columns(3, gap="small")
                        t1.markdown(
                            f'<div class="health-v8-trend-metric"><div class="tm-label">CURRENT</div>'
                            f'<div class="tm-value">{r["Current"]:.3f} {r["Unit"]}</div><div class="tm-note">Latest value</div></div>',
                            unsafe_allow_html=True
                        )
                        t2.markdown(
                            f'<div class="health-v8-trend-metric"><div class="tm-label">HISTORICAL P05–P95</div>'
                            f'<div class="tm-value">{r["Baseline Low"]:.3f} – {r["Baseline High"]:.3f}</div>'
                            f'<div class="tm-note">Typical historical range</div></div>',
                            unsafe_allow_html=True
                        )
                        shift_color = "#d92d20" if abs(float(r["Shift %"])) >= 10 else "#344054"
                        t3.markdown(
                            f'<div class="health-v8-trend-metric"><div class="tm-label">RECENT SHIFT</div>'
                            f'<div class="tm-value" style="color:{shift_color}">{r["Shift %"]:+.1f}%</div>'
                            f'<div class="tm-note">vs previous shift window</div></div>',
                            unsafe_allow_html=True
                        )
                        st.markdown('</div>', unsafe_allow_html=True)

                        b1, b2, b3 = st.columns(3, gap="small")
                        if b1.button("📈 Open Engineering Trend", key=f"health_trend_{selected_eq}_{selected_tag}", use_container_width=True):
                            st.session_state["trend_equipment_from_priority"] = selected_eq
                            st.session_state["trend_tag_from_priority"] = selected_tag
                            st.info("Equipment and PLC tag are prepared for Engineering Trend. Use the navigation panel to open the trend view.")
                        if b2.button("🎯 Open Maintenance Priority", key=f"health_priority_{selected_eq}", use_container_width=True):
                            st.session_state["priority_equipment_from_health"] = selected_eq
                            st.info("Equipment is prepared for Maintenance Priority. Use the navigation panel to review its screening priority.")
                        if b3.button("🔄 Recheck Parameter", key=f"health_recheck_{selected_eq}_{selected_tag}", use_container_width=True):
                            st.rerun()

            st.markdown(
                '<div class="health-v8-note"><b>Note:</b> Screening is not a failure prediction. '
                'Always confirm with field inspection, OEM/design limits, process condition and engineering judgement before maintenance action.</div>',
                unsafe_allow_html=True
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
            st.dataframe(display, use_container_width=True, hide_index=True, height=420)

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
            if b1.button("📈 Open Problem Trend", key=f"priority_open_trend_v2_{selected}", use_container_width=True):
                st.session_state["trend_equipment_from_priority"] = selected
                st.session_state["trend_tag_from_priority"] = r["Top Tag"]
                st.success(f"Trend prepared for {r['Top Tag']}. Open **Engineering Trend** from Navigation.")
            if b2.button("🛠️ Send to Action Center", key=f"priority_open_action_v2_{selected}", use_container_width=True):
                fdf = build_action_findings(master[master["Equipment Code"] == selected], df, criticality_df)
                if not fdf.empty:
                    st.session_state["action_selected_finding"] = str(fdf.iloc[0]["Finding ID"])
                    st.success("Finding prepared for the Engineering Action Center. Open it from Navigation.")
                else:
                    st.info("No abnormal finding is currently available for this equipment.")
            if b3.button("🔍 Open Equipment Health", key=f"priority_open_health_v2_{selected}", use_container_width=True):
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
    area = st.selectbox("Area", ["All"] + sorted([x for x in master["Area"].unique() if str(x).strip()]))
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
        validate_one = c1.button("🔎 Validate File", type="secondary", use_container_width=True, key="validate_one_v14")
        import_one = c2.button("✅ Import This File", type="primary", use_container_width=True, key="import_one_v14")

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
                st.dataframe(result_view, use_container_width=True, hide_index=True)

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
                            st.dataframe(preview, use_container_width=True, hide_index=True)
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
                st.dataframe(log_df, use_container_width=True, hide_index=True)
        with st.expander("🗄️ Database details", expanded=False):
            st.code(str(DB_PATH), language="text")
            st.caption("Unique ArchiveTime key • transactional import • import log • compressed row payloads")
    except Exception as exc:
        st.error(f"Unable to read historical database status: {exc}")
