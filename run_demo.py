"""
AegisFi: Master Execution & Academic / Hackathon Demo Runner.
Executes the end-to-end pipeline:
ETL -> Star Schema -> OLAP -> Data Mining -> Grok Swarm -> Web3 Autonomous Rescue.
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from dwh.etl_pipeline import AegisETLPipeline
from dwh.olap_engine import AegisOLAPEngine
from data_mining.anomaly_detector import RugPullAnomalyDetector
from data_mining.wallet_clusterer import WalletBehaviorClusterer
from data_mining.association_miner import TokenAssociationMiner
from agents.swarm_coordinator import AegisSwarmCoordinator
from web3_execution.executor import AegisWeb3Executor
from config import DEVELOPER_WALLET_ADDRESS, DB_PATH

def run_master_demo():
    print("=" * 70)
    print("🛡️  AEGIS-FI: AUTONOMOUS ON-CHAIN GUARDIAN & ALPHA INTELLIGENCE  🛡️")
    print("   Data Warehousing & Data Mining (DWDM) + Grok Multi-Agent Swarm")
    print("=" * 70)

    # 1. DATA WAREHOUSE ETL & STAR SCHEMA
    print("\n[PHASE 1: DATA WAREHOUSE & STAR SCHEMA INITIALIZATION]")
    etl = AegisETLPipeline()
    etl.run_full_pipeline(n_swaps=4000, n_liquidity_events=400)

    # 2. OLAP MULTI-DIMENSIONAL OPERATIONS
    print("\n[PHASE 2: EXECUTING MULTI-DIMENSIONAL OLAP OPERATIONS]")
    olap = AegisOLAPEngine()
    print("  -> Running OLAP Roll-Up (Time Dimension: Day)...")
    rollup_df = olap.roll_up_volume("day")
    print(f"     Indexed {len(rollup_df)} time buckets. Total volume: ${rollup_df['total_volume_usd'].sum():,.2f}")

    print("  -> Running OLAP Whale Slice (Trades ≥ $50,000)...")
    whale_df = olap.slice_whale_activity(50000.0)
    print(f"     Extracted {len(whale_df)} institutional whale swaps.")

    print("  -> Running OLAP Cross-Tabulation Pivot (Tokens × Days)...")
    pivot_df = olap.pivot_volume_by_day_and_token()
    print(f"     Generated matrix for {len(pivot_df)} tokens.")

    # 3. DATA MINING ALGORITHMS
    print("\n[PHASE 3: TRAINING & EXECUTING DATA MINING MODELS]")
    print("  -> 1. Isolation Forest Rug-Pull Detector...")
    detector = RugPullAnomalyDetector()
    anomalies = detector.fit_and_detect()
    threats = detector.get_active_threats(0.75)
    print(f"     Flagged {len(threats)} critical liquidity-draining exploit events (>0.75 threat score).")

    print("  -> 2. K-Means & DBSCAN Wallet Behavioral Clustering (k=4)...")
    clusterer = WalletBehaviorClusterer()
    clusters_df, c_metrics = clusterer.fit_and_cluster()
    print(f"     Clustering Quality: Silhouette Score = {c_metrics['silhouette_score']} | Inertia = {c_metrics['inertia']}")
    for cid, name in c_metrics["cluster_mapping"].items():
        count = (clusters_df['kmeans_cluster'] == cid).sum()
        print(f"       • Cluster #{cid} ({name}): {count} wallets")

    print("  -> 3. FP-Growth Token Affinity & Association Mining...")
    miner = TokenAssociationMiner()
    itemsets, rules = miner.mine_rules()
    print(f"     Mined {len(itemsets)} frequent itemsets and {len(rules)} high-lift association rules.")
    if not rules.empty:
        top_rule = rules.iloc[0]
        print(f"       • Top Rule: {{{top_rule['antecedents_str']}}} ➔ {{{top_rule['consequents_str']}}} (Lift: {top_rule['lift']}, Conf: {top_rule['confidence']})")

    # 4. GROK MULTI-AGENT SWARM
    print("\n[PHASE 4: GROK AUTONOMOUS MULTI-AGENT SWARM SURVEILLANCE]")
    coordinator = AegisSwarmCoordinator()
    surveillance = coordinator.run_surveillance_cycle()
    print(f"  -> Surveillance Status: {surveillance['cycle_status']}")
    print(f"  -> Critical Exploit Alert: {surveillance['threat_alert']}")
    print("\n  [SENTINEL AGENT REPORT]:")
    print("  " + surveillance['security_report']['analysis'].replace("\n", "\n  "))

    # 5. AUTONOMOUS WEB3 RESCUE
    print("\n[PHASE 5: AUTONOMOUS ON-CHAIN WEB3 EXECUTION (ERC-4337 SESSION KEY)]")
    executor = AegisWeb3Executor()
    if not threats.empty:
        top_threat = threats.iloc[0]
        pool_id = top_threat["pool_id"]
        token = "PEPE-SAFE" if "pepe" in pool_id else "MOON-AI"
        print(f"  -> Triggering Autonomous Emergency Rescue on compromised pool: {pool_id}...")
        receipt = executor.execute_emergency_rescue(
            user_wallet=DEVELOPER_WALLET_ADDRESS,
            pool_id=pool_id,
            token_symbol=token,
            amount_tokens=50000.0,
            threat_score=float(top_threat["threat_score"])
        )
        print("  -> Autonomous Rescue Succeeded!")
        print(f"     Tx Hash: {receipt['tx_hash']}")
        print(f"     Asset Exited: {receipt['tokens_rescued']:,} {receipt['compromised_token']}")
        print(f"     USDC Secured: ${receipt['received_usdc']:,.2f}")
        print(f"     Contract Approvals Revoked: {receipt['approval_revoked']}")
        print(f"     Block Explorer: {receipt['explorer_url']}")
    else:
        print("  -> No pool in critical threat zone; executing Alpha Rebalance...")
        alpha_tx = executor.execute_alpha_rebalance(DEVELOPER_WALLET_ADDRESS, "WETH", "LINK", 1500.0)
        print(f"     Alpha Rebalance Tx: {alpha_tx['tx_hash']}")

    print("\n" + "=" * 70)
    print("✨ ALL 5 PHASES COMPLETED WITH 100% SUCCESS!")
    print("To launch the interactive visual dashboard, run:")
    print("   streamlit run aegis-dwdm-agent/dashboard/app.py")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    run_master_demo()
