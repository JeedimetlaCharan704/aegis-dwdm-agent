"""
AegisFi Data Warehouse - Star Schema DDL
Implements:
1. Fact Tables: fact_dex_swaps, fact_liquidity_events
2. Dimension Tables: dim_wallet (with SCD Type 2), dim_token, dim_liquidity_pool, dim_time
"""

STAR_SCHEMA_DDL = """
-- Drop tables if re-initializing
DROP TABLE IF EXISTS fact_dex_swaps;
DROP TABLE IF EXISTS fact_liquidity_events;
DROP TABLE IF EXISTS dim_wallet;
DROP TABLE IF EXISTS dim_token;
DROP TABLE IF EXISTS dim_liquidity_pool;
DROP TABLE IF EXISTS dim_time;

-- 1. Dimension: Time (Hierarchical Date/Time Dimension)
CREATE TABLE dim_time (
    time_id VARCHAR PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    hour INTEGER NOT NULL,
    day INTEGER NOT NULL,
    day_of_week VARCHAR NOT NULL,
    week INTEGER NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL
);

-- 2. Dimension: Token
CREATE TABLE dim_token (
    token_id VARCHAR PRIMARY KEY,
    token_address VARCHAR NOT NULL,
    symbol VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    decimals INTEGER DEFAULT 18,
    is_verified BOOLEAN DEFAULT TRUE,
    risk_score DOUBLE DEFAULT 0.0,
    created_at TIMESTAMP
);

-- 3. Dimension: Liquidity Pool
CREATE TABLE dim_liquidity_pool (
    pool_id VARCHAR PRIMARY KEY,
    pool_address VARCHAR NOT NULL,
    protocol VARCHAR NOT NULL,
    token0_id VARCHAR NOT NULL,
    token1_id VARCHAR NOT NULL,
    fee_tier_bps INTEGER NOT NULL,
    initial_tvl_usd DOUBLE NOT NULL,
    created_at TIMESTAMP
);

-- 4. Dimension: Wallet (Implements Slowly Changing Dimension - SCD Type 2)
CREATE TABLE dim_wallet (
    wallet_sk VARCHAR PRIMARY KEY,        -- Surrogate Key (e.g., 0x123_v1)
    wallet_address VARCHAR NOT NULL,      -- Natural Business Key
    reputation_score DOUBLE NOT NULL,     -- 0 to 100
    behavior_tag VARCHAR NOT NULL,        -- 'SMART_MONEY', 'WHALE', 'ARBITRAGE_BOT', 'RETAIL', 'SUSPECTED_RUGGER'
    total_tx_count INTEGER DEFAULT 0,
    win_rate_pct DOUBLE DEFAULT 50.0,
    is_contract BOOLEAN DEFAULT FALSE,
    -- SCD Type 2 Tracking Columns
    effective_start_date TIMESTAMP NOT NULL,
    effective_end_date TIMESTAMP,
    is_current BOOLEAN NOT NULL DEFAULT TRUE
);

-- 5. Fact Table: DEX Swaps
CREATE TABLE fact_dex_swaps (
    swap_id VARCHAR PRIMARY KEY,
    tx_hash VARCHAR NOT NULL,
    block_number BIGINT NOT NULL,
    time_id VARCHAR NOT NULL REFERENCES dim_time(time_id),
    wallet_sk VARCHAR NOT NULL REFERENCES dim_wallet(wallet_sk),
    pool_id VARCHAR NOT NULL REFERENCES dim_liquidity_pool(pool_id),
    token_in_id VARCHAR NOT NULL REFERENCES dim_token(token_id),
    token_out_id VARCHAR NOT NULL REFERENCES dim_token(token_id),
    amount_in_tokens DOUBLE NOT NULL,
    amount_out_tokens DOUBLE NOT NULL,
    amount_usd DOUBLE NOT NULL,
    price_impact_pct DOUBLE NOT NULL,
    gas_used_gwei DOUBLE NOT NULL,
    is_sandwich_victim BOOLEAN DEFAULT FALSE
);

-- 6. Fact Table: Liquidity Events (Mints, Burns, Rug-Pull Drains)
CREATE TABLE fact_liquidity_events (
    event_id VARCHAR PRIMARY KEY,
    tx_hash VARCHAR NOT NULL,
    block_number BIGINT NOT NULL,
    time_id VARCHAR NOT NULL REFERENCES dim_time(time_id),
    wallet_sk VARCHAR NOT NULL REFERENCES dim_wallet(wallet_sk),
    pool_id VARCHAR NOT NULL REFERENCES dim_liquidity_pool(pool_id),
    event_type VARCHAR NOT NULL,          -- 'ADD_LIQUIDITY', 'REMOVE_LIQUIDITY', 'DRAIN_LIQUIDITY'
    amount_token0 DOUBLE NOT NULL,
    amount_token1 DOUBLE NOT NULL,
    liquidity_usd_delta DOUBLE NOT NULL,  -- Positive for Add, Negative for Remove
    remaining_pool_tvl_usd DOUBLE NOT NULL,
    drain_percentage DOUBLE DEFAULT 0.0   -- For rug-pull anomaly detection
);

-- Indexes for OLAP query performance
CREATE INDEX IF NOT EXISTS idx_swaps_time ON fact_dex_swaps(time_id);
CREATE INDEX IF NOT EXISTS idx_swaps_pool ON fact_dex_swaps(pool_id);
CREATE INDEX IF NOT EXISTS idx_swaps_wallet ON fact_dex_swaps(wallet_sk);
CREATE INDEX IF NOT EXISTS idx_liq_pool ON fact_liquidity_events(pool_id);
"""

def initialize_database(conn):
    """Executes the Star Schema DDL on a DuckDB connection."""
    conn.execute(STAR_SCHEMA_DDL)
    print("Star Schema initialized successfully in DuckDB.")
