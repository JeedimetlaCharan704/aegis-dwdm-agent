"""
AegisFi Wallet Behavioral Clustering Engine (DWDM Data Mining).
Implements K-Means Clustering & DBSCAN to discover wallet archetypes:
1. Smart Money (High win rate, moderate-high volume, early accumulation)
2. Whales (Extremely large single orders, high market impact)
3. Arbitrage / MEV Bots (High frequency, micro slippage, gas sensitive)
4. Retail (Low volume, random frequency)
"""

import duckdb
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from config import DB_PATH, KMEANS_WALLET_CLUSTERS

class WalletBehaviorClusterer:
    def __init__(self, db_path=DB_PATH, n_clusters=KMEANS_WALLET_CLUSTERS):
        self.db_path = str(db_path)
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        self.dbscan = DBSCAN(eps=1.2, min_samples=3)
        self.feature_columns = [
            "log_total_volume",
            "swap_count",
            "avg_trade_usd",
            "avg_price_impact",
            "win_rate_pct",
            "reputation_score"
        ]
        self.cluster_names = {}
        self.silhouette_avg = 0.0

    def _extract_wallet_features(self):
        conn = duckdb.connect(self.db_path)
        sql = """
            SELECT 
                w.wallet_sk,
                w.wallet_address,
                w.behavior_tag AS ground_truth_tag,
                w.reputation_score,
                w.win_rate_pct,
                COUNT(s.swap_id) AS swap_count,
                COALESCE(SUM(s.amount_usd), 0.0) AS total_volume_usd,
                COALESCE(AVG(s.amount_usd), 0.0) AS avg_trade_usd,
                COALESCE(AVG(s.price_impact_pct), 0.0) AS avg_price_impact,
                COALESCE(AVG(s.gas_used_gwei), 30.0) AS avg_gas_gwei
            FROM dim_wallet w
            LEFT JOIN fact_dex_swaps s ON w.wallet_sk = s.wallet_sk
            WHERE w.is_current = TRUE
            GROUP BY w.wallet_sk, w.wallet_address, w.behavior_tag, w.reputation_score, w.win_rate_pct;
        """
        df = conn.execute(sql).df()
        conn.close()

        # Feature Engineering: log transform for skewed volume
        df["log_total_volume"] = np.log1p(df["total_volume_usd"])
        return df

    def fit_and_cluster(self):
        """
        Fits K-Means and DBSCAN on engineered wallet features.
        Returns clustered DataFrame and model evaluation metrics.
        """
        df = self._extract_wallet_features()
        if len(df) < self.n_clusters:
            return df, {}

        X = df[self.feature_columns].values
        X_scaled = self.scaler.fit_transform(X)

        # 1. K-Means
        kmeans_labels = self.kmeans.fit_predict(X_scaled)
        df["kmeans_cluster"] = kmeans_labels

        # Calculate Silhouette Score (DWDM Viva metric)
        if len(set(kmeans_labels)) > 1:
            self.silhouette_avg = round(float(silhouette_score(X_scaled, kmeans_labels)), 4)
        else:
            self.silhouette_avg = 0.0

        # 2. DBSCAN (Outlier / Sybil Detection)
        dbscan_labels = self.dbscan.fit_predict(X_scaled)
        df["dbscan_cluster"] = dbscan_labels
        df["is_density_outlier"] = dbscan_labels == -1

        # 3. Label Clusters based on Centroids
        self._interpret_clusters(df)
        df["predicted_archetype"] = df["kmeans_cluster"].map(self.cluster_names)

        metrics = {
            "n_clusters": self.n_clusters,
            "inertia": round(float(self.kmeans.inertia_), 2),
            "silhouette_score": self.silhouette_avg,
            "density_outliers_count": int(df["is_density_outlier"].sum()),
            "cluster_mapping": self.cluster_names
        }

        return df, metrics

    def _interpret_clusters(self, df):
        """Maps numeric cluster IDs to human/business archetypes using centroid means."""
        cluster_summary = df.groupby("kmeans_cluster")[
            ["total_volume_usd", "avg_trade_usd", "win_rate_pct", "swap_count"]
        ].mean()

        for cid, row in cluster_summary.iterrows():
            if row["avg_trade_usd"] > 40000:
                self.cluster_names[cid] = "Whale / High Net-Worth"
            elif row["win_rate_pct"] > 70 and row["total_volume_usd"] > 100000:
                self.cluster_names[cid] = "Smart Money / Alpha Trader"
            elif row["swap_count"] > 15:
                self.cluster_names[cid] = "Arbitrage / Active Algorithmic"
            else:
                self.cluster_names[cid] = "Retail / Casual Trader"

    def get_smart_money_wallets(self):
        """Returns the top Smart Money wallets for the Alpha Scout Agent."""
        df, _ = self.fit_and_cluster()
        smart_df = df[df["predicted_archetype"].str.contains("Smart Money", na=False)]
        return smart_df.sort_values(by="win_rate_pct", ascending=False)

if __name__ == "__main__":
    clusterer = WalletBehaviorClusterer()
    clustered_df, metrics = clusterer.fit_and_cluster()
    print("Clustering Metrics:", metrics)
    print("\nCluster Distribution:")
    print(clustered_df["predicted_archetype"].value_counts())
