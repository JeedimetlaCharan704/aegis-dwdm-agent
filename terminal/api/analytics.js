export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');

  const data = {
    kpis: {
      total_swaps: 4000,
      total_volume_usd: 117897228.29,
      total_wallets: 188,
      scd2_hist_count: 10,
      network: "Base Sepolia (84532)",
      engine: "DuckDB Columnar OLAP"
    },
    olap_rollup: [
      { day: "Day 1", volume: 3840210.50, swaps: 124, avg_impact: 0.42 },
      { day: "Day 2", volume: 4192000.10, swaps: 138, avg_impact: 0.38 },
      { day: "Day 3", volume: 3950110.80, swaps: 130, avg_impact: 0.45 },
      { day: "Day 4", volume: 5120300.00, swaps: 165, avg_impact: 0.51 },
      { day: "Day 5", volume: 4890000.20, swaps: 152, avg_impact: 0.48 },
      { day: "Day 6", volume: 3200100.00, swaps: 98, avg_impact: 0.35 },
      { day: "Day 7", volume: 3450000.00, swaps: 105, avg_impact: 0.36 }
    ],
    whale_slice: [
      { tx_hash: "0x8f2a...39b1", wallet: "0x742d...f44e", tag: "WHALE", pair: "WETH/USDC", amount_usd: 245000.00, impact: 2.85 },
      { tx_hash: "0x12c4...aa09", wallet: "0x19a0...33c1", tag: "WHALE", pair: "WBTC/WETH", amount_usd: 198000.00, impact: 1.94 },
      { tx_hash: "0x98bb...120f", wallet: "0x4421...98bb", tag: "SMART_MONEY", pair: "WETH/LINK", amount_usd: 142000.00, impact: 1.25 },
      { tx_hash: "0xaa31...4401", wallet: "0x8901...44ff", tag: "WHALE", pair: "WETH/USDT", amount_usd: 115000.00, impact: 1.10 },
      { tx_hash: "0x66ff...e210", wallet: "0x2211...55da", tag: "SMART_MONEY", pair: "WETH/UNI", amount_usd: 95000.00, impact: 0.95 }
    ],
    anomalies: [
      { pool: "pool_pepe_weth", protocol: "BaseSwap", drain_pct: 98.50, threat_score: 1.00, tag: "SUSPECTED_RUGGER", status: "CRITICAL" },
      { pool: "pool_moon_weth", protocol: "BaseSwap", drain_pct: 94.63, threat_score: 0.77, tag: "SUSPECTED_RUGGER", status: "HIGH" },
      { pool: "pool_rug_weth", protocol: "BaseSwap", drain_pct: 88.21, threat_score: 0.82, tag: "SUSPECTED_RUGGER", status: "CRITICAL" },
      { pool: "pool_link_weth", protocol: "UniswapV3", drain_pct: 12.40, threat_score: 0.12, tag: "SMART_MONEY", status: "SAFE" },
      { pool: "pool_weth_usdc", protocol: "UniswapV3", drain_pct: 4.50, threat_score: 0.05, tag: "RETAIL", status: "SAFE" }
    ],
    clustering: {
      n_clusters: 4,
      silhouette_score: 0.6512,
      wcss_inertia: 100.3,
      clusters: [
        { name: "Smart Money / Alpha", size: 20, avg_win_rate: 84.2, avg_volume: "$480K" },
        { name: "Whales / High Net-Worth", size: 48, avg_win_rate: 68.5, avg_volume: "$1.45M" },
        { name: "Arbitrage / Algorithmic", size: 25, avg_win_rate: 72.0, avg_volume: "$210K" },
        { name: "Retail / Casual Trader", size: 120, avg_win_rate: 46.8, avg_volume: "$14K" }
      ]
    },
    association_rules: [
      { antecedent: "WETH, UNI", consequent: "LINK", support: 0.085, confidence: 0.754, lift: 2.68 },
      { antecedent: "USDC, PEPE-SAFE", consequent: "MOON-AI", support: 0.042, confidence: 0.880, lift: 3.45 },
      { antecedent: "WBTC", consequent: "WETH", support: 0.185, confidence: 0.820, lift: 1.95 }
    ],
    scd_ledger: [
      { wallet: "0x3b89...11c4", version: "v1", tag: "RETAIL", rep: 54.0, period: "2026-10-01 to 2026-10-15", is_current: false },
      { wallet: "0x3b89...11c4", version: "v2", tag: "SMART_MONEY", rep: 92.5, period: "2026-10-15 to Present", is_current: true },
      { wallet: "0x99a1...ff32", version: "v1", tag: "RETAIL", rep: 48.0, period: "2026-10-01 to 2026-10-20", is_current: false },
      { wallet: "0x99a1...ff32", version: "v2", tag: "SUSPECTED_RUGGER", rep: 12.0, period: "2026-10-20 to Present", is_current: true }
    ]
  };

  return res.status(200).json(data);
}
