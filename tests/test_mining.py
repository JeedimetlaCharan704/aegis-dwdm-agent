import unittest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from data_mining.anomaly_detector import RugPullAnomalyDetector
from data_mining.wallet_clusterer import WalletBehaviorClusterer
from data_mining.association_miner import TokenAssociationMiner

class TestDataMiningEngine(unittest.TestCase):
    def test_isolation_forest_anomaly(self):
        detector = RugPullAnomalyDetector()
        df = detector.fit_and_detect()
        self.assertFalse(df.empty)
        self.assertIn("threat_score", df.columns)
        self.assertIn("is_anomaly", df.columns)
        self.assertTrue((df["threat_score"] >= 0.0).all() and (df["threat_score"] <= 1.0).all())

    def test_kmeans_and_dbscan_clustering(self):
        clusterer = WalletBehaviorClusterer()
        df, metrics = clusterer.fit_and_cluster()
        self.assertFalse(df.empty)
        self.assertIn("kmeans_cluster", df.columns)
        self.assertIn("predicted_archetype", df.columns)
        self.assertIn("silhouette_score", metrics)
        self.assertGreater(metrics["silhouette_score"], 0.20, "Silhouette score should indicate reasonable cluster cohesion.")

    def test_fp_growth_association_mining(self):
        miner = TokenAssociationMiner()
        itemsets, rules = miner.mine_rules()
        self.assertFalse(itemsets.empty, "Frequent itemsets must be found.")
        self.assertIn("support", itemsets.columns)

if __name__ == "__main__":
    unittest.main()
