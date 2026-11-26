"""
AegisFi Agent Tools.
Exposes Data Warehouse OLAP queries and Data Mining models as callable tools for Autonomous Agents.
"""

from dwh.olap_engine import AegisOLAPEngine
from data_mining.anomaly_detector import RugPullAnomalyDetector
from data_mining.wallet_clusterer import WalletBehaviorClusterer
from data_mining.association_miner import TokenAssociationMiner

# Singletons for performance
_olap = AegisOLAPEngine()
_anomaly = RugPullAnomalyDetector()
_clusterer = WalletBehaviorClusterer()
_miner = TokenAssociationMiner()

def tool_get_active_threats(threshold=0.75):
    """
    Scans the Data Warehouse using the Isolation Forest model to detect high-risk rug-pull pools.
    """
    threats_df = _anomaly.get_active_threats(threshold=threshold)
    if threats_df.empty:
        return {"status": "SAFE", "active_threats": []}

    records = threats_df[[
        "pool_id", "protocol", "drain_percentage", "threat_score", "behavior_tag", "tx_hash"
    ]].head(5).to_dict(orient="records")
    return {"status": "THREAT_DETECTED", "count": len(records), "active_threats": records}

def tool_get_smart_money_insights():
    """
    Queries K-Means wallet clustering to find the highest-performing Smart Money wallets.
    """
    smart_df = _clusterer.get_smart_money_wallets()
    if smart_df.empty:
        return {"status": "NO_DATA", "wallets": []}

    records = smart_df[[
        "wallet_address", "win_rate_pct", "total_volume_usd", "swap_count", "reputation_score"
    ]].head(5).to_dict(orient="records")
    return {"status": "SUCCESS", "smart_money_wallets": records}

def tool_get_token_association_rules():
    """
    Runs FP-Growth association rule mining to discover token co-trading affinity.
    """
    _, rules_df = _miner.mine_rules()
    if rules_df.empty:
        return {"status": "NO_RULES", "rules": []}

    top_rules = rules_df[[
        "antecedents_str", "consequents_str", "support", "confidence", "lift"
    ]].head(5).to_dict(orient="records")
    return {"status": "SUCCESS", "top_rules": top_rules}

def tool_query_olap_rollup(hierarchy="day"):
    """
    Performs OLAP roll-up across time dimension (day, week, month).
    """
    df = _olap.roll_up_volume(hierarchy)
    return {"status": "SUCCESS", "records": df.head(10).to_dict(orient="records")}

def tool_query_pool_drain_stats():
    """
    Retrieves OLAP liquidity drain analytics across all pools.
    """
    df = _olap.get_liquidity_drain_profile()
    return {"status": "SUCCESS", "pools": df.to_dict(orient="records")}
