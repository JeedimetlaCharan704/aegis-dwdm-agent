"""
AegisFi OLAP Engine.
Implements standard Data Warehousing Multi-Dimensional operations:
- Roll-up
- Drill-down
- Slice
- Dice
- Pivot / Cross-Tabulation
"""

import duckdb
import pandas as pd
from config import DB_PATH

class AegisOLAPEngine:
    def __init__(self, db_path=DB_PATH):
        self.db_path = str(db_path)

    def _query(self, sql):
        conn = duckdb.connect(self.db_path)
        try:
            return conn.execute(sql).df()
        finally:
            conn.close()

    # 1. ROLL-UP: Move from detailed level to aggregated hierarchy
    def roll_up_volume(self, hierarchy_level="day"):
        """
        Roll-up DEX volume across time dimension hierarchy: hour -> day -> week -> month.
        """
        valid_levels = ["hour", "day", "week", "month", "year", "day_of_week"]
        if hierarchy_level not in valid_levels:
            hierarchy_level = "day"

        sql = f"""
            SELECT 
                t.{hierarchy_level} AS time_bucket,
                COUNT(s.swap_id) AS total_swaps,
                ROUND(SUM(s.amount_usd), 2) AS total_volume_usd,
                ROUND(AVG(s.amount_usd), 2) AS avg_trade_usd,
                ROUND(AVG(s.price_impact_pct), 4) AS avg_price_impact,
                ROUND(AVG(s.gas_used_gwei), 2) AS avg_gas_gwei
            FROM fact_dex_swaps s
            JOIN dim_time t ON s.time_id = t.time_id
            GROUP BY t.{hierarchy_level}
            ORDER BY t.{hierarchy_level} ASC;
        """
        return self._query(sql)

    # 2. DRILL-DOWN: Move from aggregated level down to granular details
    def drill_down_pool_activity(self, pool_id=None, limit=50):
        """
        Drill down from high-level pool summaries to individual atomic swap transactions.
        """
        where_clause = f"WHERE s.pool_id = '{pool_id}'" if pool_id else ""
        sql = f"""
            SELECT 
                s.swap_id,
                s.tx_hash,
                s.block_number,
                t.timestamp,
                p.protocol,
                w.wallet_address,
                w.behavior_tag,
                tin.symbol AS token_in,
                tout.symbol AS token_out,
                s.amount_usd,
                s.price_impact_pct,
                s.gas_used_gwei
            FROM fact_dex_swaps s
            JOIN dim_time t ON s.time_id = t.time_id
            JOIN dim_liquidity_pool p ON s.pool_id = p.pool_id
            JOIN dim_wallet w ON s.wallet_sk = w.wallet_sk
            JOIN dim_token tin ON s.token_in_id = tin.token_id
            JOIN dim_token tout ON s.token_out_id = tout.token_id
            {where_clause}
            ORDER BY t.timestamp DESC
            LIMIT {limit};
        """
        return self._query(sql)

    # 3. SLICE: Filter data along one single dimension
    def slice_whale_activity(self, min_amount_usd=50000.0):
        """
        Slice operation: Select swaps where trade size >= threshold (Whale slice).
        """
        sql = f"""
            SELECT 
                s.swap_id,
                w.wallet_address,
                w.behavior_tag,
                tin.symbol AS token_in,
                tout.symbol AS token_out,
                s.amount_usd,
                s.price_impact_pct,
                t.timestamp
            FROM fact_dex_swaps s
            JOIN dim_wallet w ON s.wallet_sk = w.wallet_sk
            JOIN dim_token tin ON s.token_in_id = tin.token_id
            JOIN dim_token tout ON s.token_out_id = tout.token_id
            JOIN dim_time t ON s.time_id = t.time_id
            WHERE s.amount_usd >= {min_amount_usd}
            ORDER BY s.amount_usd DESC;
        """
        return self._query(sql)

    # 4. DICE: Multi-dimensional sub-cube extraction
    def dice_subcube(self, token_symbol="WETH", min_amount=1000.0, behavior_tag="SMART_MONEY"):
        """
        Dice operation: Filter across multiple dimensions simultaneously (Token x Volume x Wallet Type).
        """
        sql = f"""
            SELECT 
                p.protocol,
                tin.symbol AS token_in,
                tout.symbol AS token_out,
                w.behavior_tag,
                COUNT(s.swap_id) AS swap_count,
                ROUND(SUM(s.amount_usd), 2) AS subcube_volume_usd,
                ROUND(AVG(s.price_impact_pct), 3) AS avg_impact
            FROM fact_dex_swaps s
            JOIN dim_wallet w ON s.wallet_sk = w.wallet_sk
            JOIN dim_liquidity_pool p ON s.pool_id = p.pool_id
            JOIN dim_token tin ON s.token_in_id = tin.token_id
            JOIN dim_token tout ON s.token_out_id = tout.token_id
            WHERE (tin.symbol = '{token_symbol}' OR tout.symbol = '{token_symbol}')
              AND s.amount_usd >= {min_amount}
              AND w.behavior_tag = '{behavior_tag}'
            GROUP BY p.protocol, tin.symbol, tout.symbol, w.behavior_tag
            ORDER BY subcube_volume_usd DESC;
        """
        return self._query(sql)

    # 5. PIVOT: Rotate dimensions to create cross-tabulation matrix
    def pivot_volume_by_day_and_token(self):
        """
        Pivot operation: Token symbols on rows, Day of Week on columns, Total Volume as values.
        """
        sql = """
            PIVOT (
                SELECT 
                    tin.symbol AS token,
                    t.day_of_week,
                    s.amount_usd
                FROM fact_dex_swaps s
                JOIN dim_token tin ON s.token_in_id = tin.token_id
                JOIN dim_time t ON s.time_id = t.time_id
            )
            ON day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
            USING ROUND(SUM(amount_usd), 2)
            ORDER BY token ASC;
        """
        return self._query(sql)

    # 6. LIQUIDITY DRAIN OLAP ANALYSIS (Security & Anomaly View)
    def get_liquidity_drain_profile(self):
        """
        Aggregates pool liquidity events to show net flow, maximum single drain, and current TVL.
        """
        sql = """
            SELECT 
                p.pool_id,
                p.protocol,
                p.initial_tvl_usd,
                COUNT(l.event_id) AS total_events,
                COUNT(CASE WHEN l.event_type = 'DRAIN_LIQUIDITY' THEN 1 END) AS drain_events,
                ROUND(MAX(l.drain_percentage), 2) AS max_drain_pct,
                ROUND(MIN(l.remaining_pool_tvl_usd), 2) AS lowest_tvl_observed,
                ROUND(SUM(l.liquidity_usd_delta), 2) AS net_liquidity_flow_usd
            FROM dim_liquidity_pool p
            LEFT JOIN fact_liquidity_events l ON p.pool_id = l.pool_id
            GROUP BY p.pool_id, p.protocol, p.initial_tvl_usd
            ORDER BY max_drain_pct DESC;
        """
        return self._query(sql)

if __name__ == "__main__":
    olap = AegisOLAPEngine()
    print("Testing OLAP roll-up by day:")
    print(olap.roll_up_volume("day").head())
