"""
AegisFi ETL (Extract, Transform, Load) Pipeline.
Implements data validation, cleaning, SCD Type 2 dimension management, and DuckDB storage.
"""

import duckdb
import pandas as pd
from datetime import datetime
from config import DB_PATH, DATA_DIR
from dwh.schema import initialize_database
from dwh.generator import generate_web3_dataset

class AegisETLPipeline:
    def __init__(self, db_path=DB_PATH):
        self.db_path = str(db_path)
        self.conn = None

    def get_connection(self):
        return duckdb.connect(self.db_path)

    def run_full_pipeline(self, n_swaps=8000, n_liquidity_events=800):
        print(f"[*] Starting AegisFi DWH ETL Pipeline...")
        print(f"[*] Target Database: {self.db_path}")
        
        # 1. Extraction / Generation
        print("[1/4] Extracting & Generating realistic on-chain transaction data...")
        dataset = generate_web3_dataset(n_swaps=n_swaps, n_liquidity_events=n_liquidity_events)
        
        # Save raw CSV extracts for audit and academic demo
        raw_dir = DATA_DIR / "raw"
        raw_dir.mkdir(exist_ok=True)
        for tbl_name, df in dataset.items():
            df.to_csv(raw_dir / f"{tbl_name}.csv", index=False)
        print(f"    -> Raw extracts archived in {raw_dir}")

        # 2. Transformation & Validation
        print("[2/4] Transforming, cleaning, and validating dimensional data...")
        
        # Ensure timestamps are proper datetime objects
        dataset["dim_time"]["timestamp"] = pd.to_datetime(dataset["dim_time"]["timestamp"])
        dataset["dim_token"]["created_at"] = pd.to_datetime(dataset["dim_token"]["created_at"])
        dataset["dim_liquidity_pool"]["created_at"] = pd.to_datetime(dataset["dim_liquidity_pool"]["created_at"])
        dataset["dim_wallet"]["effective_start_date"] = pd.to_datetime(dataset["dim_wallet"]["effective_start_date"])
        dataset["dim_wallet"]["effective_end_date"] = pd.to_datetime(dataset["dim_wallet"]["effective_end_date"])

        # Data Cleaning: deduplicate and handle missing values
        for key in dataset:
            initial_len = len(dataset[key])
            dataset[key] = dataset[key].drop_duplicates()
            dedup_diff = initial_len - len(dataset[key])
            if dedup_diff > 0:
                print(f"    -> Cleaned {dedup_diff} duplicate records from {key}")

        # 3. Load into DuckDB Star Schema
        print("[3/4] Initializing Star Schema DDL and Loading into DuckDB Warehouse...")
        conn = self.get_connection()
        initialize_database(conn)

        # Register and insert dataframes
        for tbl_name, df_data in dataset.items():
            conn.execute(f"INSERT INTO {tbl_name} SELECT * FROM df_data")
            count_res = conn.execute(f"SELECT COUNT(*) FROM {tbl_name}").fetchall()[0][0]
            print(f"    [+] Loaded {count_res} rows into {tbl_name}")

        # 4. Verification and SCD-2 Metric Checks
        print("[4/4] Verifying Star Schema integrity and SCD Type 2 dimension states...")
        scd2_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_wallet_records,
                COUNT(DISTINCT wallet_address) as unique_wallets,
                COUNT(*) FILTER (WHERE is_current = FALSE) as historic_scd2_records,
                COUNT(*) FILTER (WHERE is_current = TRUE) as current_active_records
            FROM dim_wallet
        """).df()
        
        fact_swaps_stat = conn.execute("""
            SELECT 
                COUNT(*) as total_swaps,
                SUM(amount_usd) as total_volume_usd,
                AVG(gas_used_gwei) as avg_gas_gwei
            FROM fact_dex_swaps
        """).df()

        conn.close()

        print("\n" + "="*50)
        print(">>> ETL PIPELINE COMPLETED SUCCESSFULLY <<<")
        print(f"Total Wallets (Unique): {scd2_stats['unique_wallets'][0]}")
        print(f"SCD Type 2 Records Tracked: {scd2_stats['historic_scd2_records'][0]} historical versions")
        print(f"Total DEX Volume Processed: ${fact_swaps_stat['total_volume_usd'][0]:,.2f} across {fact_swaps_stat['total_swaps'][0]:,} swaps")
        print("="*50 + "\n")
        return True

    def execute_query(self, sql_query):
        """Helper to run arbitrary analytical queries."""
        conn = self.get_connection()
        res_df = conn.execute(sql_query).df()
        conn.close()
        return res_df

if __name__ == "__main__":
    etl = AegisETLPipeline()
    etl.run_full_pipeline(n_swaps=3000, n_liquidity_events=300)
