"""
AegisFi Anomaly Detection Engine (DWDM Data Mining).
Uses Isolation Forest & Z-Score Analysis on Liquidity Flows to detect:
- Rug-Pulls (sudden massive liquidity removals)
- Flash Loan Drain Anomalies
- High Slippage Sandwich Attacks
"""

import duckdb
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from config import DB_PATH, ISOLATION_FOREST_CONTAMINATION

class RugPullAnomalyDetector:
    def __init__(self, db_path=DB_PATH, contamination=ISOLATION_FOREST_CONTAMINATION):
        self.db_path = str(db_path)
        self.contamination = contamination
        self.model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            "drain_percentage", 
            "abs_liquidity_delta", 
            "drain_to_remaining_ratio"
        ]

    def _load_liquidity_data(self):
        conn = duckdb.connect(self.db_path)
        sql = """
            SELECT 
                l.event_id,
                l.tx_hash,
                l.block_number,
                l.pool_id,
                p.protocol,
                p.initial_tvl_usd,
                l.event_type,
                l.drain_percentage,
                ABS(l.liquidity_usd_delta) AS abs_liquidity_delta,
                l.remaining_pool_tvl_usd,
                (ABS(l.liquidity_usd_delta) / NULLIF(l.remaining_pool_tvl_usd, 0)) AS drain_to_remaining_ratio,
                w.wallet_address,
                w.behavior_tag
            FROM fact_liquidity_events l
            JOIN dim_liquidity_pool p ON l.pool_id = p.pool_id
            JOIN dim_wallet w ON l.wallet_sk = w.wallet_sk;
        """
        df = conn.execute(sql).df()
        conn.close()
        
        # Replace inf and fill na
        df["drain_to_remaining_ratio"] = df["drain_to_remaining_ratio"].replace([np.inf, -np.inf], 999.0).fillna(0.0)
        return df

    def fit_and_detect(self):
        """
        Trains Isolation Forest and predicts anomaly scores across all liquidity events.
        Returns annotated DataFrame with anomaly flags and risk scores (0 to 1).
        """
        df = self._load_liquidity_data()
        if len(df) == 0:
            return df

        X = df[self.feature_columns].values
        X_scaled = self.scaler.fit_transform(X)

        # Fit Isolation Forest
        self.model.fit(X_scaled)
        self.is_trained = True

        # raw_scores: negative means anomaly
        raw_scores = self.model.decision_function(X_scaled)
        preds = self.model.predict(X_scaled)  # -1 = anomaly, 1 = normal

        df["is_anomaly"] = preds == -1
        # Convert decision function to risk score between 0.0 (safe) and 1.0 (extreme threat)
        # Isolation forest decision function is typically in range [-0.5, 0.5]
        min_s, max_s = raw_scores.min(), raw_scores.max()
        if max_s > min_s:
            df["threat_score"] = np.round(1.0 - ((raw_scores - min_s) / (max_s - min_s)), 4)
        else:
            df["threat_score"] = 0.0

        return df

    def get_active_threats(self, threshold=0.75):
        """
        Returns list of pools currently flagged with threat score >= threshold.
        Used by the Sentinel Agent to trigger emergency rescues.
        """
        df = self.fit_and_detect()
        threats = df[df["threat_score"] >= threshold].sort_values(by="threat_score", ascending=False)
        return threats

if __name__ == "__main__":
    detector = RugPullAnomalyDetector()
    results = detector.fit_and_detect()
    threats = detector.get_active_threats(0.75)
    print(f"Total Events: {len(results)}, Flagged Anomalies: {results['is_anomaly'].sum()}")
    print(f"High Threat Exploits (>0.75): {len(threats)}")
    if len(threats) > 0:
        print(threats[["event_id", "pool_id", "drain_percentage", "threat_score", "behavior_tag"]].head())
