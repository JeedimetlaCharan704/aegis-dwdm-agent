import unittest
import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

import duckdb
from config import DB_PATH
from dwh.etl_pipeline import AegisETLPipeline
from dwh.olap_engine import AegisOLAPEngine

class TestDataWarehouse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.etl = AegisETLPipeline()
        cls.etl.run_full_pipeline(n_swaps=1000, n_liquidity_events=100)
        cls.olap = AegisOLAPEngine()

    def test_tables_exist(self):
        conn = duckdb.connect(str(DB_PATH))
        tables = conn.execute("SHOW TABLES").df()["name"].tolist()
        conn.close()
        expected = [
            "dim_time", "dim_token", "dim_liquidity_pool", 
            "dim_wallet", "fact_dex_swaps", "fact_liquidity_events"
        ]
        for tbl in expected:
            self.assertIn(tbl, tables, f"Missing table: {tbl}")

    def test_scd_type_2_integrity(self):
        conn = duckdb.connect(str(DB_PATH))
        scd_count = conn.execute("SELECT COUNT(*) FROM dim_wallet WHERE is_current = FALSE").fetchone()[0]
        conn.close()
        self.assertGreater(scd_count, 0, "SCD Type 2 must track historized records.")

    def test_olap_rollup(self):
        df_rollup = self.olap.roll_up_volume("day")
        self.assertFalse(df_rollup.empty)
        self.assertIn("total_volume_usd", df_rollup.columns)

    def test_olap_whale_slice(self):
        df_slice = self.olap.slice_whale_activity(50000.0)
        self.assertFalse(df_slice.empty)
        self.assertTrue((df_slice["amount_usd"] >= 50000.0).all())

    def test_olap_pivot(self):
        df_pivot = self.olap.pivot_volume_by_day_and_token()
        self.assertFalse(df_pivot.empty)
        self.assertIn("token", df_pivot.columns)

if __name__ == "__main__":
    unittest.main()
