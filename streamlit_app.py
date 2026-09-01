import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import re

st.set_page_config(page_title="OPP Engineering Monitoring", page_icon="⚙️", layout="wide")
ROOT = Path(__file__).resolve().parent

# --- Professional UI theme ---
st.markdown("""<style>
.main .block-container{padding-top:1.15rem;padding-bottom:3rem;max-width:1500px}
[data-testid="stSidebar"]{background:#f4f7fb;border-right:1px solid #dfe5ee}
[data-testid="stSidebar"] .stRadio>label{font-size:.82rem!important;font-weight:800!important;color:#344054!important}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"]{gap:.18rem}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label{padding:.58rem .65rem!important;border-radius:.55rem;font-size:.92rem!important}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover{background:#e8f1ff}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked){background:#dcecff;color:#1256ad!important;font-weight:700!important}
.opp-brand{padding:.35rem .35rem 1.1rem;border-bottom:1px solid #dfe5ee;margin-bottom:1rem}.opp-brand-title{font-size:1.35rem;font-weight:800;color:#182230}.opp-brand-sub{color:#667085;font-size:.76rem;margin-top:.2rem}
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

</style>""",unsafe_allow_html=True)

DB_PATH = ROOT / "data" / "plc_history.sqlite"
DB_SCHEMA_VERSION = 1


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

        # One-time migration of existing v9 *.csv.gz history into SQLite.
        existing_count = conn.execute("SELECT COUNT(*) FROM plc_history").fetchone()[0]
        legacy_files = sorted((ROOT / "data").glob("*.csv.gz"))
        migrated = conn.execute("SELECT value FROM app_meta WHERE key='legacy_csv_migrated'").fetchone()
        if existing_count == 0 and legacy_files and not migrated:
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
                        raw = json.dumps(row.to_dict(), default=str, allow_nan=False).encode("utf-8")
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
            raw = json.dumps(row.to_dict(), default=str, allow_nan=False).encode("utf-8")
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

def _navigate_dashboard(nav_label, value=None):
    """Set navigation/filter state before the next Streamlit rerun."""
    st.session_state["main_navigation"] = nav_label
    if nav_label == "⚠  Maintenance Priority" and value:
        st.session_state["priority_condition_v2"] = value
    elif nav_label == "〽  Equipment Health" and value:
        st.session_state["health_area"] = value

st.sidebar.markdown("""<div class="opp-brand"><div class="opp-brand-title">⚙️ OPP</div><div class="opp-brand-sub">Engineering Monitoring</div></div>""",unsafe_allow_html=True)
nav_options={"⌂  Dashboard":"Dashboard","〽  Equipment Health":"Equipment Health","⚠  Maintenance Priority":"Maintenance Priority","✓  Action Center":"Action Center","⌑  Tag Master":"Tag Master","↗  Engineering Trend":"Engineering Trend","⇧  Data Import":"Data Import"}
selected_nav=st.sidebar.radio("NAVIGATION",list(nav_options.keys()),key="main_navigation")
page=nav_options[selected_nav]
st.sidebar.markdown("---")
st.sidebar.caption("Decision Support • OPP Engineering")

st.markdown('<div class="opp-page-title">OPP Engineering Monitoring</div>',unsafe_allow_html=True)
st.markdown('<div class="opp-page-sub">Engineering decision support for process monitoring, equipment health, abnormality screening and maintenance follow-up.</div>',unsafe_allow_html=True)

high = int((master["Confidence"] == "High").sum())
medium = int((master["Confidence"] == "Medium").sum())
low = int((master["Confidence"] == "Low").sum())

if page == "Dashboard":
    # Executive dashboard: visual overview only. Detailed screening lives in
    # Equipment Health / Maintenance Priority / Action Center.
    st.markdown('<div class="opp-page-sub dashboard-intro">Plant condition overview and engineering decision support — identify the signal, then drill down only when needed.</div>', unsafe_allow_html=True)

    screening = build_equipment_screening(master, df)
    findings = build_action_findings(master, df)
    if not findings.empty:
        store = ensure_action_store(findings)
        action_df = actions_dataframe(store)
        open_count = int((action_df["Status"] != "CLOSED").sum()) if not action_df.empty else 0
    else:
        open_count = 0

    if screening.empty:
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

        last_data = ""
        try:
            last_data = pd.to_datetime(df["ArchiveTime"], errors="coerce").max().strftime("%d %b %Y")
        except Exception:
            pass

        # ==============================================================
        # 1. Executive KPI strip — one clean visual row.
        # ==============================================================
        k1, k2, k3, k4, k5 = st.columns(5, gap="small")
        kpis = [
            (k1, "kpi-blue", "🩺 Screened Equipment", total_eq, "equipment covered by screening"),
            (k2, "kpi-cyan", "✓ Healthy Equipment", healthy, f"{healthy/max(total_eq,1)*100:.1f}% of screened"),
            (k3, "kpi-orange", "⚠ Requires Attention", nonhealthy, f"{nonhealthy/max(total_eq,1)*100:.1f}% outside healthy"),
            (k4, "kpi-red", "🔴 P1 Immediate Review", p1n, "highest screening urgency"),
            (k5, "kpi-purple", "🛠 Open Findings", open_count, "engineering follow-up open"),
        ]
        for col, cls, title, value, small in kpis:
            col.markdown(
                f'<div class="opp-card dashboard-kpi {cls}">'
                f'<div class="opp-card-title">{title}</div>'
                f'<div class="opp-card-value">{value:,}</div>'
                f'<div class="opp-card-small">{small}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="dashboard-grid-gap"></div>', unsafe_allow_html=True)

        # ==============================================================
        # 2. Plant Condition + Action Center
        #    Real bordered containers keep both panels aligned.
        # ==============================================================
        left, right = st.columns([1.6, 1], gap="small")

        with left:
            with st.container(border=True, key="dash_plant_condition"):
                st.markdown('<div class="dashboard-panel-header">🩺 Plant Condition</div>', unsafe_allow_html=True)
                st.markdown('<div class="dashboard-panel-body">', unsafe_allow_html=True)
                st.markdown('<div class="dashboard-panel-sub">Historical screening distribution — click a condition to open the worklist.</div>', unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4, gap="small")
                cards = [
                    (c1, "HEALTHY", healthy, "condition-healthy", "Routine condition", None),
                    (c2, "DETERIORATING", deteriorating, "condition-deteriorating", "Showing deterioration", "DETERIORATING"),
                    (c3, "ATTENTION", attention, "condition-attention", "Engineering review", "ATTENTION"),
                    (c4, "CRITICAL", critical, "condition-critical", "Highest concern", "CRITICAL"),
                ]
                for col, label, n, cls, desc, filter_value in cards:
                    status_cls = {
                        "HEALTHY":"status-healthy",
                        "DETERIORATING":"status-deteriorating",
                        "ATTENTION":"status-attention",
                        "CRITICAL":"status-critical"
                    }.get(label, "")
                    col.markdown(
                        f'<div class="condition-card {cls}">'
                        f'<div class="label {status_cls}">{label}</div>'
                        f'<div class="count">{n:,}</div>'
                        f'<div class="pct">{n/max(total_eq,1)*100:.1f}% · {desc}</div></div>',
                        unsafe_allow_html=True,
                    )
                    if filter_value:
                        col.button(
                            f"🔎 View {label.title()}",
                            key=f"dash_condition_{filter_value.lower()}",
                            use_container_width=True,
                            on_click=_navigate_dashboard,
                            args=("⚠  Maintenance Priority", filter_value),
                        )
                st.markdown('</div>', unsafe_allow_html=True)

        with right:
            with st.container(border=True, key="dash_action_center"):
                st.markdown('<div class="dashboard-panel-header">🛠 Action Center</div>', unsafe_allow_html=True)
                st.markdown('<div class="dashboard-panel-body">', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="opp-card dashboard-kpi kpi-purple dashboard-action-kpi">'
                    f'<div class="opp-card-title">🛠 OPEN ENGINEERING FINDINGS</div>'
                    f'<div class="opp-card-value">{open_count:,}</div>'
                    f'<div class="opp-card-small">findings awaiting engineering follow-up</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown('<div style="height:.55rem"></div>', unsafe_allow_html=True)
                st.button("🛠 Open Action Center", key="dash_open_action", use_container_width=True,
                          on_click=_navigate_dashboard, args=("✓  Action Center", None))
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="dashboard-grid-gap"></div>', unsafe_allow_html=True)

        # ==============================================================
        # 3. Engineering Focus + Data Quality
        # ==============================================================
        left, right = st.columns([1.6, 1], gap="small")

        with left:
            with st.container(border=True, key="dash_engineering_focus"):
                st.markdown('<div class="dashboard-panel-header">🎯 Engineering Focus</div>', unsafe_allow_html=True)
                st.markdown('<div class="dashboard-panel-body">', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="focus-box"><b>{nonhealthy:,} equipment</b> are outside the healthy screening state. '
                    f'Priority screening identifies <b>{p1n} P1</b> immediate-review, <b>{p2n} P2</b> planned-inspection, '
                    f'<b>{p3n} P3</b> monitoring and <b>{p4n} P4</b> routine items.</div>',
                    unsafe_allow_html=True,
                )
                q1,q2,q3,q4=st.columns(4, gap="small")
                priority_cards = [
                    (q1,"P1",p1n,"Immediate Review","p1"),
                    (q2,"P2",p2n,"Planned Inspection","p2"),
                    (q3,"P3",p3n,"Monitoring","p3"),
                    (q4,"P4",p4n,"Routine","p4"),
                ]
                for col,label,n,desc,cls in priority_cards:
                    col.markdown(
                        f'<div class="priority-summary-card {cls}">'
                        f'<div class="psc-top"><span class="psc-dot"></span>{label}</div>'
                        f'<div class="psc-count">{n:,}</div>'
                        f'<div class="psc-desc">{desc}</div></div>',
                        unsafe_allow_html=True,
                    )
                st.button("🎯 Open Maintenance Priority", key="dash_open_priority", use_container_width=True,
                          on_click=_navigate_dashboard, args=("⚠  Maintenance Priority", None))
                st.markdown('</div>', unsafe_allow_html=True)

        with right:
            with st.container(border=True, key="dash_data_quality"):
                st.markdown('<div class="dashboard-panel-header">📊 Data Quality & Coverage</div>', unsafe_allow_html=True)
                st.markdown('<div class="dashboard-panel-body">', unsafe_allow_html=True)
                dq1,dq2,dq3,dq4=st.columns(4, gap="small")
                dq1.markdown(f'<div class="dq-card"><div class="dq-label">PLC Tags</div><div class="dq-value">{len(master):,}</div></div>', unsafe_allow_html=True)
                dq2.markdown(f'<div class="dq-card dq-high-bg"><div class="dq-label">High</div><div class="dq-value dq-high">{high:,}</div></div>', unsafe_allow_html=True)
                dq3.markdown(f'<div class="dq-card dq-medium-bg"><div class="dq-label">Medium</div><div class="dq-value dq-medium">{medium:,}</div></div>', unsafe_allow_html=True)
                dq4.markdown(f'<div class="dq-card dq-low-bg"><div class="dq-label">Low</div><div class="dq-value dq-low">{low:,}</div></div>', unsafe_allow_html=True)
                st.caption("Confidence describes mapping evidence, not equipment condition.")
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="dashboard-grid-gap"></div>', unsafe_allow_html=True)

        # ==============================================================
        # 4. Area Signal + Priority Mix
        # ==============================================================
        left, right = st.columns([1.6, 1], gap="small")

        with left:
            with st.container(border=True, key="dash_area_signal"):
                st.markdown('<div class="dashboard-panel-header">📍 Area Signal</div>', unsafe_allow_html=True)
                st.markdown('<div class="dashboard-panel-body">', unsafe_allow_html=True)
                st.markdown('<div class="dashboard-panel-sub">Areas with the highest concentration of non-healthy equipment.</div>', unsafe_allow_html=True)

                area_df = screening.copy()
                area_map = master[["Equipment Code", "Area"]].drop_duplicates("Equipment Code")
                area_df = area_df.merge(area_map, on="Equipment Code", how="left")
                area_df["Area"] = area_df["Area"].fillna("").astype(str).str.strip()
                area_df = area_df[area_df["Area"] != ""]
                if not area_df.empty:
                    area_summary = (
                        area_df.assign(Abnormal=area_df["Condition"]!="HEALTHY")
                        .groupby("Area",as_index=False)
                        .agg(Equipment=("Equipment Code","count"),Abnormal=("Abnormal","sum"))
                    )
                    area_summary["Abnormal %"] = area_summary["Abnormal"]/area_summary["Equipment"].clip(lower=1)*100
                    area_summary = area_summary.sort_values(["Abnormal","Abnormal %"],ascending=[False,False]).head(6).reset_index(drop=True)
                    cols=st.columns(3, gap="small")
                    for i,rr in area_summary.iterrows():
                        col=cols[i%3]
                        area=rr["Area"]; abnormal_n=int(rr["Abnormal"]); equip_n=int(rr["Equipment"]); pct=float(rr["Abnormal %"])
                        safe_key=re.sub(r"[^A-Za-z0-9]+","_",str(area))
                        # Severity colour is based on concentration.
                        bar_color = "#f04438" if pct >= 50 else "#f79009" if pct >= 25 else "#12b76a"
                        col.markdown(
                            f'<div class="area-card">'
                            f'<div class="area-title">📍 {area}</div>'
                            f'<div class="area-number">{abnormal_n} <span style="font-size:.72rem;font-weight:600">of {equip_n} abnormal</span></div>'
                            f'<div class="area-pct">{pct:.1f}% of equipment</div>'
                            f'<div class="signal-bar"><div class="signal-fill" style="width:{min(100,pct):.0f}%;background:{bar_color}"></div></div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                        col.button(
                            f"🔎 View {area}", key=f"dash_area_{safe_key}",
                            use_container_width=True, on_click=_navigate_dashboard,
                            args=("〽  Equipment Health",area)
                        )
                st.markdown('<div style="height:.2rem"></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with right:
            with st.container(border=True, key="dash_priority_mix"):
                st.markdown('<div class="dashboard-panel-header">🚦 Priority Mix</div>', unsafe_allow_html=True)
                st.markdown('<div class="dashboard-panel-body">', unsafe_allow_html=True)
                st.markdown('<div class="dashboard-panel-sub">Current screening distribution by maintenance priority.</div>', unsafe_allow_html=True)
                priority_total=max(p1n+p2n+p3n+p4n,1)
                for label,n,icon,cls in [
                    ("P1 Immediate",p1n,"🔴","p1"),
                    ("P2 Inspection",p2n,"🟠","p2"),
                    ("P3 Monitor",p3n,"🟡","p3"),
                    ("P4 Routine",p4n,"🟢","p4")
                ]:
                    pct=n/priority_total*100
                    st.markdown(
                        f'<div class="priority-line {cls}">'
                        f'<div class="priority-line-top"><span>{icon} {label}</span><b>{n:,} <span style="font-weight:500;color:#667085">({pct:.1f}%)</span></b></div>'
                        f'<div class="signal-bar"><div class="signal-fill" style="width:{pct:.0f}%"></div></div></div>',
                        unsafe_allow_html=True
                    )
                st.markdown('<div style="height:.55rem"></div>', unsafe_allow_html=True)
                st.markdown(
                    '<div class="focus-box" style="font-size:.72rem">'
                    '<b>🔴 P1</b> immediate review &nbsp;•&nbsp; '
                    '<b>🟠 P2</b> planned inspection &nbsp;•&nbsp; '
                    '<b>🟡 P3</b> monitor &nbsp;•&nbsp; '
                    '<b>🟢 P4</b> routine</div>',
                    unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

        st.caption("Historical screening is decision support only — not an alarm/trip limit or failure prediction. Validate abnormal signals against OEM limits, process condition, field inspection and engineering judgement.")

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
    st.markdown('<div class="opp-page-sub">Upload a daily PLC Excel export, validate it, then append only new timestamps to the historical data used by Dashboard, Equipment Health and Engineering Trend.</div>', unsafe_allow_html=True)
    st.markdown('<div class="opp-note"><b>Import workflow:</b> Upload → Validate → Append New Rows → Refresh history.</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload daily PLC export (.xlsx)", type=["xlsx"], key="daily_plc_import_v9")
    if uploaded:
        try:
            incoming = pd.read_excel(uploaded)
        except Exception as exc:
            st.error(f"Unable to read Excel file: {exc}")
            incoming = pd.DataFrame()

        if not incoming.empty:
            if "ArchiveTime" not in incoming.columns:
                st.error("ArchiveTime not found. The Excel export must contain an 'ArchiveTime' column.")
            else:
                incoming["ArchiveTime"] = pd.to_datetime(incoming["ArchiveTime"], errors="coerce")
                invalid_count = int(incoming["ArchiveTime"].isna().sum())
                valid = incoming.dropna(subset=["ArchiveTime"]).copy()
                before_dedup = len(valid)
                valid = valid.drop_duplicates(subset=["ArchiveTime"], keep="last")
                duplicate_count = before_dedup - len(valid)

                known = set(df["ArchiveTime"].dropna()) if not df.empty else set()
                new_mask = ~valid["ArchiveTime"].isin(known)
                new_count = int(new_mask.sum())

                q1, q2, q3, q4 = st.columns(4, gap="small")
                q1.metric("Rows", f"{len(incoming):,}")
                q2.metric("New timestamps", f"{new_count:,}")
                q3.metric("Already in history", f"{len(valid) - new_count:,}")
                q4.metric("Invalid timestamps", f"{invalid_count:,}")

                if duplicate_count:
                    st.caption(f"{duplicate_count:,} duplicate timestamp row(s) inside the uploaded file were collapsed before import.")

                st.markdown("#### Import Preview")
                st.dataframe(valid.head(20), use_container_width=True, height=360)

                if new_count > 0:
                    st.warning(f"{new_count:,} new timestamp row(s) are ready to be appended to the PLC history.")
                    if st.button("✅ Append New Data to History", type="primary", use_container_width=True, key="append_daily_plc_v9"):
                        written, output = persist_daily_import(valid, uploaded.name)
                        if written:
                            # load_history() is cached, so clear it before rerun.
                            load_history.clear()
                            st.success(f"Successfully appended {written:,} new rows from {uploaded.name}.")
                            st.caption(f"Archive created: {output.name}")
                            st.rerun()
                        else:
                            st.info("No new timestamps were appended; the uploaded data is already in history.")
                else:
                    st.success("No new timestamps to append. The uploaded file is already represented in the current history.")

    st.markdown("#### Historical Database Status")
    try:
        db_rows, db_first, db_last, import_count = history_database_stats()
        h1, h2, h3, h4 = st.columns(4, gap="small")
        h1.metric("Historical Rows", f"{db_rows:,}")
        h2.metric("First Timestamp", pd.to_datetime(db_first).strftime("%d %b %Y %H:%M") if db_first else "—")
        h3.metric("Latest Timestamp", pd.to_datetime(db_last).strftime("%d %b %Y %H:%M") if db_last else "—")
        h4.metric("Import Batches", f"{import_count:,}")
        st.caption("SQLite is the single historical source consumed by Dashboard, Equipment Health and Engineering Trend. Re-uploading the same Excel file is safe: existing timestamps are not duplicated.")
        with st.expander("🗄️ Database details", expanded=False):
            st.code(str(DB_PATH), language="text")
            st.caption("Unique ArchiveTime key • transactional import • import log • compressed row payloads")
    except Exception as exc:
        st.error(f"Unable to read historical database status: {exc}")
