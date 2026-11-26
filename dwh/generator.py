"""
Realistic On-Chain Blockchain Data Generator for AegisFi Data Warehouse.
Generates authentic DEX trading, liquidity events, wallet histories, and rug-pull scenarios.
"""

import random
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def generate_address(prefix="0x"):
    random_bytes = random.randbytes(20)
    return prefix + random_bytes.hex()

def generate_tx_hash():
    return "0x" + hashlib.sha256(str(random.random()).encode()).hexdigest()

def generate_web3_dataset(n_swaps=5000, n_liquidity_events=500, start_date=datetime(2026, 10, 1)):
    random.seed(42)
    np.random.seed(42)

    # 1. Generate Tokens
    tokens_meta = [
        {"symbol": "WETH", "name": "Wrapped Ether", "decimals": 18, "is_verified": True, "risk_score": 0.05},
        {"symbol": "USDC", "name": "USD Coin", "decimals": 6, "is_verified": True, "risk_score": 0.01},
        {"symbol": "USDT", "name": "Tether USD", "decimals": 6, "is_verified": True, "risk_score": 0.02},
        {"symbol": "WBTC", "name": "Wrapped Bitcoin", "decimals": 8, "is_verified": True, "risk_score": 0.04},
        {"symbol": "LINK", "name": "Chainlink Token", "decimals": 18, "is_verified": True, "risk_score": 0.08},
        {"symbol": "UNI", "name": "Uniswap", "decimals": 18, "is_verified": True, "risk_score": 0.10},
        {"symbol": "PEPE-SAFE", "name": "Pepe Safe Meme", "decimals": 18, "is_verified": False, "risk_score": 0.88},
        {"symbol": "MOON-AI", "name": "Moon AI Yield", "decimals": 18, "is_verified": False, "risk_score": 0.94},
        {"symbol": "RUG-INU", "name": "Rug Pull Inu", "decimals": 18, "is_verified": False, "risk_score": 0.99},
        {"symbol": "ALPHA-BOT", "name": "Alpha Autonomous", "decimals": 18, "is_verified": True, "risk_score": 0.25},
    ]

    tokens = []
    for i, meta in enumerate(tokens_meta):
        token_id = f"tok_{i+1}"
        tokens.append({
            "token_id": token_id,
            "token_address": generate_address(),
            "symbol": meta["symbol"],
            "name": meta["name"],
            "decimals": meta["decimals"],
            "is_verified": meta["is_verified"],
            "risk_score": meta["risk_score"],
            "created_at": start_date - timedelta(days=random.randint(10, 100))
        })
    df_tokens = pd.DataFrame(tokens)

    # 2. Generate Liquidity Pools
    pools_data = [
        {"pool_id": "pool_weth_usdc", "protocol": "UniswapV3", "token0": "tok_1", "token1": "tok_2", "fee": 500, "tvl": 5000000.0},
        {"pool_id": "pool_weth_usdt", "protocol": "UniswapV3", "token0": "tok_1", "token1": "tok_3", "fee": 500, "tvl": 3200000.0},
        {"pool_id": "pool_wbtc_weth", "protocol": "UniswapV3", "token0": "tok_4", "token1": "tok_1", "fee": 3000, "tvl": 4500000.0},
        {"pool_id": "pool_link_weth", "protocol": "UniswapV3", "token0": "tok_5", "token1": "tok_1", "fee": 3000, "tvl": 850000.0},
        {"pool_id": "pool_uni_weth", "protocol": "UniswapV3", "token0": "tok_6", "token1": "tok_1", "fee": 3000, "tvl": 620000.0},
        {"pool_id": "pool_pepe_weth", "protocol": "BaseSwap", "token0": "tok_7", "token1": "tok_1", "fee": 10000, "tvl": 120000.0},
        {"pool_id": "pool_moon_weth", "protocol": "BaseSwap", "token0": "tok_8", "token1": "tok_1", "fee": 10000, "tvl": 80000.0},
        {"pool_id": "pool_rug_weth", "protocol": "BaseSwap", "token0": "tok_9", "token1": "tok_1", "fee": 10000, "tvl": 95000.0},
    ]

    pools = []
    for p in pools_data:
        pools.append({
            "pool_id": p["pool_id"],
            "pool_address": generate_address(),
            "protocol": p["protocol"],
            "token0_id": p["token0"],
            "token1_id": p["token1"],
            "fee_tier_bps": p["fee"],
            "initial_tvl_usd": p["tvl"],
            "created_at": start_date - timedelta(days=random.randint(5, 50))
        })
    df_pools = pd.DataFrame(pools)

    # 3. Generate Wallets (with SCD Type 2 history)
    # We create normal wallets and a subset that undergo state changes
    wallet_profiles = [
        {"type": "SMART_MONEY", "count": 25, "rep": (85, 99), "win_rate": (70, 92)},
        {"type": "WHALE", "count": 15, "rep": (75, 95), "win_rate": (55, 75)},
        {"type": "ARBITRAGE_BOT", "count": 20, "rep": (60, 80), "win_rate": (60, 85)},
        {"type": "RETAIL", "count": 120, "rep": (40, 65), "win_rate": (40, 55)},
        {"type": "SUSPECTED_RUGGER", "count": 8, "rep": (10, 30), "win_rate": (20, 40)},
    ]

    wallets = []
    wallet_lookup = []
    w_idx = 1
    for prof in wallet_profiles:
        for _ in range(prof["count"]):
            addr = generate_address()
            rep = round(random.uniform(*prof["rep"]), 2)
            win_r = round(random.uniform(*prof["win_rate"]), 2)
            tx_c = random.randint(5, 500)
            
            # Version 1 of wallet
            v1_start = start_date - timedelta(days=random.randint(30, 90))
            wallets.append({
                "wallet_sk": f"w_{w_idx}_v1",
                "wallet_address": addr,
                "reputation_score": rep,
                "behavior_tag": prof["type"],
                "total_tx_count": tx_c,
                "win_rate_pct": win_r,
                "is_contract": prof["type"] == "ARBITRAGE_BOT" and random.random() < 0.5,
                "effective_start_date": v1_start,
                "effective_end_date": None,
                "is_current": True
            })
            wallet_lookup.append({"wallet_sk": f"w_{w_idx}_v1", "address": addr, "tag": prof["type"]})
            w_idx += 1

    # Demonstrate SCD Type 2: 10 wallets changed behavior midway (e.g. Retail upgraded to Smart Money or flagged as Rugger)
    scd_evolutions = random.sample(range(len(wallets)), 10)
    for idx in scd_evolutions:
        old_w = wallets[idx]
        change_time = start_date + timedelta(days=15)
        # Update old version
        old_w["effective_end_date"] = change_time
        old_w["is_current"] = False
        
        # New tag
        new_tag = "SMART_MONEY" if old_w["behavior_tag"] == "RETAIL" else "SUSPECTED_RUGGER"
        new_rep = 92.0 if new_tag == "SMART_MONEY" else 15.0
        new_sk = old_w["wallet_sk"].replace("_v1", "_v2")
        
        wallets.append({
            "wallet_sk": new_sk,
            "wallet_address": old_w["wallet_address"],
            "reputation_score": new_rep,
            "behavior_tag": new_tag,
            "total_tx_count": old_w["total_tx_count"] + 45,
            "win_rate_pct": 82.5 if new_tag == "SMART_MONEY" else 25.0,
            "is_contract": old_w["is_contract"],
            "effective_start_date": change_time,
            "effective_end_date": None,
            "is_current": True
        })
        # Update lookup to latest
        for item in wallet_lookup:
            if item["address"] == old_w["wallet_address"]:
                item["wallet_sk"] = new_sk
                item["tag"] = new_tag

    df_wallets = pd.DataFrame(wallets)

    # 4. Generate Time Dimension
    time_records = []
    current_time = start_date
    for i in range(24 * 45): # 45 days hourly
        t_id = current_time.strftime("%Y%m%d%H")
        time_records.append({
            "time_id": t_id,
            "timestamp": current_time,
            "hour": current_time.hour,
            "day": current_time.day,
            "day_of_week": current_time.strftime("%A"),
            "week": current_time.isocalendar()[1],
            "month": current_time.month,
            "year": current_time.year
        })
        current_time += timedelta(hours=1)
    df_time = pd.DataFrame(time_records)
    time_ids = df_time["time_id"].tolist()

    # 5. Generate Fact DEX Swaps
    swaps = []
    block_start = 18_500_000
    pool_ids = [p["pool_id"] for p in pools_data]

    # Pre-select smart money wallets for co-trading association pattern mining
    smart_wallets = [w for w in wallet_lookup if w["tag"] == "SMART_MONEY"]

    for i in range(n_swaps):
        # Pick wallet
        if random.random() < 0.35 and smart_wallets:
            w_choice = random.choice(smart_wallets)
        else:
            w_choice = random.choice(wallet_lookup)

        # Token pair
        pool_choice = random.choice(pools_data)
        token_in = pool_choice["token0"]
        token_out = pool_choice["token1"]
        if random.random() < 0.5:
            token_in, token_out = token_out, token_in

        # Co-trading pattern: Smart money frequently trades LINK (tok_5) and UNI (tok_6) after WETH
        if w_choice["tag"] == "SMART_MONEY" and random.random() < 0.6:
            token_in = "tok_1"  # WETH
            token_out = random.choice(["tok_5", "tok_6"])  # LINK or UNI

        # Amount sizing by wallet tag
        if w_choice["tag"] == "WHALE":
            amt_usd = random.uniform(50000, 250000)
            impact = random.uniform(0.8, 3.5)
        elif w_choice["tag"] == "ARBITRAGE_BOT":
            amt_usd = random.uniform(5000, 25000)
            impact = random.uniform(0.05, 0.3)
        elif w_choice["tag"] == "SMART_MONEY":
            amt_usd = random.uniform(10000, 75000)
            impact = random.uniform(0.2, 1.2)
        else: # Retail
            amt_usd = random.uniform(100, 4500)
            impact = random.uniform(0.01, 0.5)

        t_id = random.choice(time_ids)
        block = block_start + i * 2 + random.randint(0, 5)

        swaps.append({
            "swap_id": f"swap_{i+1}",
            "tx_hash": generate_tx_hash(),
            "block_number": block,
            "time_id": t_id,
            "wallet_sk": w_choice["wallet_sk"],
            "pool_id": pool_choice["pool_id"],
            "token_in_id": token_in,
            "token_out_id": token_out,
            "amount_in_tokens": round(amt_usd / 2500.0, 4),
            "amount_out_tokens": round(amt_usd / 1.0, 4) if token_out in ["tok_2", "tok_3"] else round(amt_usd / 2500.0, 4),
            "amount_usd": round(amt_usd, 2),
            "price_impact_pct": round(impact, 4),
            "gas_used_gwei": round(random.uniform(15.0, 45.0), 2),
            "is_sandwich_victim": impact > 2.0 and random.random() < 0.3
        })
    df_swaps = pd.DataFrame(swaps)

    # 6. Generate Fact Liquidity Events (Mints, Burns & Anomaly Rug-Pulls)
    liq_events = []
    pool_tvl_tracker = {p["pool_id"]: p["tvl"] for p in pools_data}
    
    # Identify rugger wallets
    rugger_wallets = [w for w in wallet_lookup if "RUG" in w["tag"] or "SUSPECTED" in w["tag"]]
    rug_pools = ["pool_pepe_weth", "pool_moon_weth", "pool_rug_weth"]

    for j in range(n_liquidity_events):
        p_id = random.choice(pool_ids)
        current_tvl = pool_tvl_tracker[p_id]
        
        # Check if rug-pull event occurs in suspicious pools
        is_rug_pull = (p_id in rug_pools) and (j > n_liquidity_events * 0.7) and random.random() < 0.25
        
        if is_rug_pull:
            w_choice = random.choice(rugger_wallets) if rugger_wallets else random.choice(wallet_lookup)
            drain_pct = random.uniform(88.0, 99.5)
            drain_usd = current_tvl * (drain_pct / 100.0)
            remaining_tvl = max(100.0, current_tvl - drain_usd)
            pool_tvl_tracker[p_id] = remaining_tvl
            
            liq_events.append({
                "event_id": f"liq_{j+1}",
                "tx_hash": generate_tx_hash(),
                "block_number": block_start + j * 10,
                "time_id": random.choice(time_ids[-100:]),
                "wallet_sk": w_choice["wallet_sk"],
                "pool_id": p_id,
                "event_type": "DRAIN_LIQUIDITY",
                "amount_token0": round(drain_usd / 2500.0, 4),
                "amount_token1": round(drain_usd / 2.0, 4),
                "liquidity_usd_delta": -round(drain_usd, 2),
                "remaining_pool_tvl_usd": round(remaining_tvl, 2),
                "drain_percentage": round(drain_pct, 2)
            })
        else:
            w_choice = random.choice(wallet_lookup)
            is_add = random.random() < 0.65
            ev_type = "ADD_LIQUIDITY" if is_add else "REMOVE_LIQUIDITY"
            delta_pct = random.uniform(1.0, 15.0)
            delta_usd = current_tvl * (delta_pct / 100.0) * (1 if is_add else -1)
            remaining_tvl = max(10000.0, current_tvl + delta_usd)
            pool_tvl_tracker[p_id] = remaining_tvl
            
            liq_events.append({
                "event_id": f"liq_{j+1}",
                "tx_hash": generate_tx_hash(),
                "block_number": block_start + j * 10,
                "time_id": random.choice(time_ids),
                "wallet_sk": w_choice["wallet_sk"],
                "pool_id": p_id,
                "event_type": ev_type,
                "amount_token0": round(abs(delta_usd) / 2500.0, 4),
                "amount_token1": round(abs(delta_usd) / 2.0, 4),
                "liquidity_usd_delta": round(delta_usd, 2),
                "remaining_pool_tvl_usd": round(remaining_tvl, 2),
                "drain_percentage": round(delta_pct, 2) if not is_add else 0.0
            })
    df_liq = pd.DataFrame(liq_events)

    return {
        "dim_token": df_tokens,
        "dim_liquidity_pool": df_pools,
        "dim_wallet": df_wallets,
        "dim_time": df_time,
        "fact_dex_swaps": df_swaps,
        "fact_liquidity_events": df_liq
    }

if __name__ == "__main__":
    print("Testing data generation...")
    dataset = generate_web3_dataset(n_swaps=500, n_liquidity_events=50)
    for table_name, df in dataset.items():
        print(f"Table {table_name}: {len(df)} rows, columns: {list(df.columns)}")
