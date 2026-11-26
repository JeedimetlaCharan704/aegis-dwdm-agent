"""
Aegis Analytics: Enterprise On-Chain Data Warehouse & Security Dashboard.
Human-designed FinTech aesthetic (Inter typography, clean slate theme, enterprise navigation).
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import duckdb

from config import DB_PATH, DEVELOPER_WALLET_ADDRESS, IS_LLM_CONFIGURED, GROK_MODEL, LLM_PROVIDER_NAME
from dwh.etl_pipeline import AegisETLPipeline
from dwh.olap_engine import AegisOLAPEngine
from data_mining.anomaly_detector import RugPullAnomalyDetector
from data_mining.wallet_clusterer import WalletBehaviorClusterer
from data_mining.association_miner import TokenAssociationMiner
from agents.swarm_coordinator import AegisSwarmCoordinator
from web3_execution.executor import AegisWeb3Executor

# ==============================================================================
# ENTERPRISE HUMAN-DESIGNED FINTECH STYLING (INTER FONT, CLEAN SLATE)
# ==============================================================================
st.set_page_config(
    page_title="Aegis Analytics | On-Chain Data Warehouse",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Typography & Palette (High-Tech Minimal Theme) */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        color: #f8fafc;
    }
    code, pre, .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Top App Header */
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 18px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 22px;
    }
    .brand-mark {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(99, 102, 241, 0.25));
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 800;
        color: #38bdf8;
        margin-right: 12px;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.25);
    }
    .brand-name {
        font-size: 18px;
        font-weight: 700;
        letter-spacing: -0.015em;
        color: #ffffff;
    }
    .brand-sub {
        font-size: 12px;
        color: #64748b;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.03em;
        margin-top: 2px;
    }
    .meta-badge {
        font-size: 11px;
        font-weight: 500;
        font-family: 'JetBrains Mono', monospace;
        padding: 5px 12px;
        border-radius: 6px;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #94a3b8;
        display: inline-flex;
        align-items: center;
        gap: 7px;
        backdrop-filter: blur(10px);
    }
    .status-dot {
        width: 6.5px;
        height: 6.5px;
        border-radius: 50%;
        background: #10b981;
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.8);
    }

    /* High-Tech Metric Cards */
    .kpi-container {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(14px);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .kpi-container:hover {
        border-color: rgba(56, 189, 248, 0.35);
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -8px rgba(0, 0, 0, 0.6), 0 0 16px rgba(56, 189, 248, 0.15);
    }
    .kpi-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #64748b;
        margin-bottom: 5px;
    }
    .kpi-num {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.02em;
        font-family: 'JetBrains Mono', monospace;
    }
    .kpi-desc {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 4px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* High-Tech Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.02em;
        color: #94a3b8;
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 6px;
        transition: all 0.18s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff;
        background: rgba(255, 255, 255, 0.04);
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        background: rgba(56, 189, 248, 0.12) !important;
        border-color: rgba(56, 189, 248, 0.3) !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.18) !important;
    }

    .clean-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 18px 20px;
        margin-bottom: 14px;
        backdrop-filter: blur(14px);
    }
    .clean-card-title {
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #cbd5e1;
        margin-bottom: 4px;
    }
    .clean-card-caption {
        font-size: 11px;
        color: #64748b;
        margin-bottom: 12px;
        font-family: 'JetBrains Mono', monospace;
    }
</style>
""", unsafe_allow_html=True)

# Minimalist Corporate Plotly Chart Styling
def format_enterprise_chart(fig, title="", height=270):
    fig.update_layout(
        title={
            "text": title,
            "font": {"family": "Inter, sans-serif", "size": 13, "color": "#f9fafb", "weight": 600},
            "x": 0.01,
            "y": 0.96
        },
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=32, b=10),
        font=dict(family="Inter, sans-serif", color="#9ca3af", size=11),
        xaxis=dict(
            gridcolor="#1f2937",
            showline=False,
            zeroline=False,
            tickfont=dict(family="Inter", size=10, color="#6b7280")
        ),
        yaxis=dict(
            gridcolor="#1f2937",
            showline=False,
            zeroline=False,
            tickfont=dict(family="Inter", size=10, color="#6b7280")
        ),
        legend=dict(
            font=dict(family="Inter", size=10, color="#9ca3af"),
            bgcolor="rgba(0,0,0,0)"
        ),
        hoverlabel=dict(
            bgcolor="#111827",
            bordercolor="#374151",
            font_size=11,
            font_family="Inter"
        )
    )
    return fig

# Engine Singletons
@st.cache_resource
def get_engines():
    if not DB_PATH.exists():
        etl = AegisETLPipeline()
        etl.run_full_pipeline(n_swaps=4000, n_liquidity_events=400)
    return {
        "olap": AegisOLAPEngine(),
        "anomaly": RugPullAnomalyDetector(),
        "cluster": WalletBehaviorClusterer(),
        "assoc": TokenAssociationMiner(),
        "coordinator": AegisSwarmCoordinator(),
        "executor": AegisWeb3Executor()
    }

engines = get_engines()
olap = engines["olap"]
anomaly_engine = engines["anomaly"]
cluster_engine = engines["cluster"]
assoc_engine = engines["assoc"]
coordinator = engines["coordinator"]
executor = engines["executor"]

@st.cache_data(ttl=600)
def fetch_dwh_kpis():
    conn = duckdb.connect(str(DB_PATH))
    swaps = conn.execute("SELECT COUNT(*) FROM fact_dex_swaps").fetchone()[0]
    volume = conn.execute("SELECT SUM(amount_usd) FROM fact_dex_swaps").fetchone()[0] or 0.0
    wallets = conn.execute("SELECT COUNT(DISTINCT wallet_address) FROM dim_wallet").fetchone()[0]
    scd = conn.execute("SELECT COUNT(*) FROM dim_wallet WHERE is_current = FALSE").fetchone()[0]
    conn.close()
    return swaps, volume, wallets, scd

@st.cache_data(ttl=600)
def cached_anomalies():
    return anomaly_engine.fit_and_detect(), anomaly_engine.get_active_threats(0.70)

@st.cache_data(ttl=600)
def cached_clusters():
    return cluster_engine.fit_and_cluster()

@st.cache_data(ttl=600)
def cached_association_rules():
    return assoc_engine.mine_rules()

@st.cache_data(ttl=600)
def cached_rollup(grain):
    return olap.roll_up_volume(grain)

@st.cache_data(ttl=600)
def cached_whale_slice(min_usd):
    return olap.slice_whale_activity(min_usd)

@st.cache_data(ttl=600)
def cached_subcube(token, tag):
    return olap.dice_subcube(token_symbol=token, min_amount=1000.0, behavior_tag=tag)

@st.cache_data(ttl=600)
def cached_pivot():
    return olap.pivot_volume_by_day_and_token()

@st.cache_data(ttl=600)
def cached_drilldown(pool):
    return olap.drill_down_pool_activity(pool, limit=30)

@st.cache_data(ttl=600)
def cached_scd_audit():
    conn = duckdb.connect(str(DB_PATH))
    df = conn.execute("""
        SELECT 
            wallet_address,
            wallet_sk,
            reputation_score,
            behavior_tag,
            effective_start_date,
            effective_end_date,
            is_current
        FROM dim_wallet
        WHERE wallet_address IN (
            SELECT wallet_address FROM dim_wallet GROUP BY wallet_address HAVING COUNT(*) > 1
        )
        ORDER BY wallet_address, effective_start_date ASC;
    """).df()
    conn.close()
    return df

total_swaps, total_volume, total_wallets, scd2_hist = fetch_dwh_kpis()

# Application Header
st.markdown(f"""
<div class="app-header">
    <div>
        <div style="display: flex; align-items: center;">
            <span class="brand-mark">A</span>
            <div>
                <span class="brand-name">Aegis Analytics</span>
                <span style="font-size: 11px; background: #161f33; border: 1px solid #1f2937; padding: 2px 7px; border-radius: 4px; color: #9ca3af; margin-left: 6px;">Enterprise v2.4</span>
            </div>
        </div>
        <div class="brand-sub">On-Chain Data Warehouse & Quantitative Risk Management</div>
    </div>
    <div style="display: flex; gap: 8px;">
        <span class="meta-badge"><span class="status-dot"></span> Base Sepolia (84532)</span>
        <span class="meta-badge">DuckDB OLAP</span>
        <span class="meta-badge">Groq Intelligence</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Clean KPI Row
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">Total Processed Volume</div>
        <div class="kpi-num mono">${total_volume:,.2f}</div>
        <div class="kpi-desc">Indexed across 8 monitored pools</div>
    </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">Verified Transactions</div>
        <div class="kpi-num mono">{total_swaps:,}</div>
        <div class="kpi-desc">Fact-table grain swap records</div>
    </div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">Classified Wallets</div>
        <div class="kpi-num mono">{total_wallets}</div>
        <div class="kpi-desc">Clustered dimensional entities</div>
    </div>
    """, unsafe_allow_html=True)
with k4:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">Audit Histories (SCD-2)</div>
        <div class="kpi-num mono">{scd2_hist}</div>
        <div class="kpi-desc">Dimension state changes tracked</div>
    </div>
    """, unsafe_allow_html=True)

# Human Enterprise Navigation Tabs
tab_dwh, tab_mining, tab_agent, tab_settle = st.tabs([
    "Overview & OLAP",
    "Risk & Pattern Discovery",
    "Intelligence & Surveillance",
    "Security Guard & Settlement"
])

# TAB 1: OVERVIEW & OLAP
with tab_dwh:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    c_op_ctrl, c_op_view = st.columns([1, 2.5])

    with c_op_ctrl:
        st.markdown("<div class='clean-card-title'>OLAP Query Selector</div>", unsafe_allow_html=True)
        st.markdown("<div class='clean-card-caption'>Choose a multi-dimensional operation to explore the warehouse.</div>", unsafe_allow_html=True)
        olap_choice = st.radio(
            "Query Type:",
            [
                "Daily Volume Roll-up",
                "Granular Pool Drill-down",
                "Whale Orders (>= $50k)",
                "Asset & Wallet Subcube",
                "Asset x Day Pivot Table",
                "SCD Type 2 Audit Trail"
            ],
            label_visibility="collapsed"
        )

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        if olap_choice == "Daily Volume Roll-up":
            granularity = st.selectbox("Temporal Aggregation:", ["day", "week", "day_of_week", "hour"])
        elif olap_choice == "Whale Orders (>= $50k)":
            min_whale_usd = st.slider("Minimum Trade Size ($ USD):", 10000, 250000, 50000, step=5000)
        elif olap_choice == "Asset & Wallet Subcube":
            dice_token = st.selectbox("Target Asset:", ["WETH", "USDC", "LINK", "UNI", "PEPE-SAFE"])
            dice_tag = st.selectbox("Wallet Class:", ["SMART_MONEY", "WHALE", "ARBITRAGE_BOT", "RETAIL"])
        elif olap_choice == "Granular Pool Drill-down":
            pool_target = st.selectbox("Select Pool to Inspect:", ["pool_weth_usdc", "pool_link_weth", "pool_pepe_weth", "pool_moon_weth"])

    with c_op_view:
        if olap_choice == "Daily Volume Roll-up":
            df_rollup = cached_rollup(granularity)
            fig_roll = px.bar(
                df_rollup,
                x="time_bucket",
                y="total_volume_usd",
                color_discrete_sequence=["#2563eb"],
                labels={"time_bucket": granularity.capitalize(), "total_volume_usd": "Volume ($)"}
            )
            format_enterprise_chart(fig_roll, f"Aggregated Volume Rolled Up by {granularity.capitalize()}", height=260)
            st.plotly_chart(fig_roll, use_container_width=True)
            st.dataframe(df_rollup, use_container_width=True, height=170)

        elif olap_choice == "Granular Pool Drill-down":
            df_drill = cached_drilldown(pool_target)
            st.markdown(f"<div class='clean-card-title'>Atomic Swap Drill-down for {pool_target}</div>", unsafe_allow_html=True)
            st.dataframe(df_drill, use_container_width=True, height=420)

        elif olap_choice == "Whale Orders (>= $50k)":
            df_slice = cached_whale_slice(min_whale_usd)
            fig_whale = px.scatter(
                df_slice,
                x="amount_usd",
                y="price_impact_pct",
                color="behavior_tag",
                color_discrete_sequence=["#3b82f6", "#10b981", "#f59e0b", "#ef4444"],
                hover_data=["wallet_address", "token_in", "token_out"]
            )
            format_enterprise_chart(fig_whale, f"Whale Trades (>= ${min_whale_usd:,}) vs Price Slippage", height=260)
            st.plotly_chart(fig_whale, use_container_width=True)
            st.dataframe(df_slice.head(25), use_container_width=True, height=170)

        elif olap_choice == "Asset & Wallet Subcube":
            df_dice = cached_subcube(dice_token, dice_tag)
            st.markdown(f"<div class='clean-card-title'>Multi-Dimensional Subcube: {dice_token} x {dice_tag}</div>", unsafe_allow_html=True)
            st.dataframe(df_dice, use_container_width=True, height=330)

        elif olap_choice == "Asset x Day Pivot Table":
            df_pivot = cached_pivot()
            st.markdown("<div class='clean-card-title'>Cross-Tabulation Matrix: Asset x Day of Week</div>", unsafe_allow_html=True)
            st.dataframe(df_pivot, use_container_width=True, height=330)

        elif olap_choice == "SCD Type 2 Audit Trail":
            df_scd = cached_scd_audit()
            st.markdown("<div class='clean-card-title'>Slowly Changing Dimension (SCD Type 2) Historical Ledger</div>", unsafe_allow_html=True)
            st.markdown("<div class='clean-card-caption'>Tracks wallet classification upgrades or demotions over time without overwriting history.</div>", unsafe_allow_html=True)
            st.dataframe(df_scd, use_container_width=True, height=420)

# TAB 2: RISK & PATTERNS
with tab_mining:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    m_sub1, m_sub2, m_sub3 = st.tabs([
        "Isolation Forest (Rug-Pull Outliers)",
        "Wallet Clustering (K-Means)",
        "Token Co-Trading Rules (FP-Growth)"
    ])

    with m_sub1:
        df_anomalies, threats = cached_anomalies()
        col_m1, col_m2 = st.columns([2.2, 1])
        with col_m1:
            fig_anomaly = px.scatter(
                df_anomalies,
                x="drain_percentage",
                y="threat_score",
                color="is_anomaly",
                color_discrete_map={True: "#ef4444", False: "#3b82f6"},
                hover_data=["pool_id", "protocol", "behavior_tag"],
                labels={"drain_percentage": "Liquidity Drain %", "threat_score": "Threat Score (0 to 1)"}
            )
            fig_anomaly.add_hline(y=0.75, line_dash="dash", line_color="#ef4444", annotation_text="Threat Threshold (0.75)", annotation_font_size=10)
            format_enterprise_chart(fig_anomaly, "Liquidity Drain Velocity vs Anomaly Threat Score", height=290)
            st.plotly_chart(fig_anomaly, use_container_width=True)

        with col_m2:
            st.markdown("<div class='clean-card-title'>Flagged High-Risk Pools</div>", unsafe_allow_html=True)
            if not threats.empty:
                st.dataframe(threats[["pool_id", "drain_percentage", "threat_score", "behavior_tag"]].head(10), use_container_width=True, height=260)
            else:
                st.info("Zero critical drainage events detected in current window.")

    with m_sub2:
        df_clusters, c_metrics = cached_clusters()
        col_c_metric1, col_c_metric2, col_c_metric3 = st.columns(3)
        with col_c_metric1:
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-label">Clusters Evaluated (K)</div>
                <div class="kpi-num mono">{c_metrics.get('n_clusters', 4)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_c_metric2:
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-label">Silhouette Quality Score</div>
                <div class="kpi-num mono">{c_metrics.get('silhouette_score', 0.0):.4f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_c_metric3:
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-label">Inertia (Within-Cluster Variance)</div>
                <div class="kpi-num mono">{c_metrics.get('inertia', 0.0):,.1f}</div>
            </div>
            """, unsafe_allow_html=True)

        fig_cluster = px.scatter(
            df_clusters,
            x="total_volume_usd",
            y="win_rate_pct",
            color="predicted_archetype",
            size="swap_count",
            color_discrete_sequence=["#10b981", "#3b82f6", "#f59e0b", "#6b7280"],
            hover_data=["wallet_address", "reputation_score"],
            log_x=True,
            labels={"total_volume_usd": "Volume (USD, Log)", "win_rate_pct": "Win Rate (%)"}
        )
        format_enterprise_chart(fig_cluster, "Wallet Behavioral Segments (Volume vs Win Rate)", height=290)
        st.plotly_chart(fig_cluster, use_container_width=True)

    with m_sub3:
        itemsets, rules = cached_association_rules()
        if not rules.empty:
            fig_rules = px.scatter(
                rules.head(25),
                x="support",
                y="confidence",
                size="lift",
                color="lift",
                color_continuous_scale="Blues",
                hover_data=["antecedents_str", "consequents_str"]
            )
            format_enterprise_chart(fig_rules, "Token Co-Trading Rules (Support vs Confidence)", height=280)
            st.plotly_chart(fig_rules, use_container_width=True)
            st.dataframe(rules[["antecedents_str", "consequents_str", "support", "confidence", "lift"]].head(15), use_container_width=True, height=200)

# TAB 3: INTELLIGENCE & SURVEILLANCE
with tab_agent:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    c_surv1, c_surv2 = st.columns([1.1, 1])

    with c_surv1:
        st.markdown("<div class='clean-card-title'>Automated Surveillance Engine</div>", unsafe_allow_html=True)
        st.markdown("<div class='clean-card-caption'>Evaluates active threat indicators across all warehouse pools.</div>", unsafe_allow_html=True)
        if st.button("Run Security Scan", use_container_width=True, type="primary"):
            with st.spinner("Analyzing active pool states and generating threat report..."):
                cycle_res = coordinator.run_surveillance_cycle()
                st.session_state.latest_cycle = cycle_res

        if "latest_cycle" in st.session_state:
            res = st.session_state.latest_cycle
            if res["threat_alert"]:
                st.error("Security Alert: Abnormal liquidity drainage detected exceeding risk threshold.")
            else:
                st.success("Nominal State: Zero pool exploits detected in current surveillance cycle.")

            with st.expander("Threat Assessment Details", expanded=True):
                st.markdown(res["security_report"]["analysis"])

            with st.expander("Smart Money Accumulation Insights", expanded=True):
                st.markdown(res["alpha_report"]["analysis"])

    with c_surv2:
        st.markdown("<div class='clean-card-title'>Natural Language Data Query</div>", unsafe_allow_html=True)
        st.markdown("<div class='clean-card-caption'>Query the on-chain warehouse in plain English.</div>", unsafe_allow_html=True)
        user_prompt = st.text_input("Enter question:", placeholder="e.g., Which tokens are smart money accumulating?", label_visibility="collapsed")
        
        if st.button("Submit Query", use_container_width=True):
            if user_prompt:
                with st.spinner("Processing analytical response..."):
                    reply = coordinator.process_user_query(user_prompt)
                    st.markdown(f"<div class='clean-card'>{reply.get('analysis', '')}</div>", unsafe_allow_html=True)

# TAB 4: SETTLEMENT & GUARD
with tab_settle:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    c_set1, c_set2 = st.columns([1, 1.2])

    with c_set1:
        st.markdown("<div class='clean-card-title'>Smart Account Delegation (ERC-4337)</div>", unsafe_allow_html=True)
        policy = executor.session_keys.get(DEVELOPER_WALLET_ADDRESS.lower(), {})
        
        st.markdown(f"""
        <div class="clean-card">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #9ca3af; font-size: 13px;">Delegated Wallet</span>
                <span class="mono" style="font-size: 13px; color: #f9fafb;">{DEVELOPER_WALLET_ADDRESS[:8]}...{DEVELOPER_WALLET_ADDRESS[-6:]}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #9ca3af; font-size: 13px;">Session Status</span>
                <span style="color: #34d399; font-size: 13px; font-weight: 500;">Active Policy</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #9ca3af; font-size: 13px;">Trigger Threshold</span>
                <span class="mono" style="color: #f9fafb; font-size: 13px;">Threat Score &ge; {policy.get('risk_threshold', 0.80)}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #9ca3af; font-size: 13px;">Permitted Actions</span>
                <span class="mono" style="color: #9ca3af; font-size: 12px;">Rescue Swap, Revoke Approvals</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='clean-card-title'>Active Exploit Target</div>", unsafe_allow_html=True)
        _, threats_found = cached_anomalies()
        
        if not threats_found.empty:
            target_t = threats_found.iloc[0]
            token_symbol = "PEPE-SAFE" if "pepe" in target_t["pool_id"] else "MOON-AI"
            st.warning(f"Target Pool: {target_t['pool_id']} | Drain: {target_t['drain_percentage']}% | Threat Score: {target_t['threat_score']}")

            if st.button(f"Execute Protective Token Swap ({token_symbol} → USDC)", type="primary", use_container_width=True):
                with st.spinner("Submitting signed protective transaction to Base Sepolia..."):
                    rescue_receipt = executor.execute_emergency_rescue(
                        user_wallet=DEVELOPER_WALLET_ADDRESS,
                        pool_id=target_t["pool_id"],
                        token_symbol=token_symbol,
                        amount_tokens=50000.0,
                        threat_score=float(target_t["threat_score"])
                    )
                    st.session_state.latest_rescue = rescue_receipt

    with c_set2:
        st.markdown("<div class='clean-card-title'>Settlement Ledger</div>", unsafe_allow_html=True)
        if "latest_rescue" in st.session_state:
            rcpt = st.session_state.latest_rescue
            if rcpt["status"] == "SUCCESS":
                st.markdown(f"""
                <div class="clean-card" style="border-left: 3px solid #10b981;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span style="color: #34d399; font-weight: 600; font-size: 13px;">Transaction Confirmed</span>
                        <span class="mono" style="font-size: 12px; color: #6b7280;">Block #{rcpt['block_number']}</span>
                    </div>
                    <div style="margin: 10px 0;">
                        <div style="color: #6b7280; font-size: 11px;">Transaction Hash</div>
                        <div class="mono" style="font-size: 12px; color: #60a5fa; word-break: break-all;">{rcpt['tx_hash']}</div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 10px 0;">
                        <div>
                            <div style="color: #6b7280; font-size: 11px;">Assets Evacuated</div>
                            <div class="mono" style="color: #f9fafb; font-size: 13px;">{rcpt['tokens_rescued']:,} {rcpt['compromised_token']}</div>
                        </div>
                        <div>
                            <div style="color: #6b7280; font-size: 11px;">Secured Value</div>
                            <div class="mono" style="color: #34d399; font-size: 13px; font-weight: 600;">${rcpt['received_usdc']:,.2f} USDC</div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 8px; border-top: 1px solid #1f2937;">
                        <span style="font-size: 12px; color: #9ca3af;">Router Approvals Revoked: <b style="color: #34d399;">Yes</b></span>
                        <a href="{rcpt['explorer_url']}" target="_blank" style="color: #60a5fa; font-size: 12px; text-decoration: none;">View on BaseScan &rarr;</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='clean-card' style='color: #6b7280; font-size: 13px;'>Awaiting execution. No protective actions triggered in current session.</div>", unsafe_allow_html=True)
