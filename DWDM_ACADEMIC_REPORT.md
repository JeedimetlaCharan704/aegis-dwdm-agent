# 🎓 DWDM Academic Project Report & Viva Examination Guide
## Project: AegisFi — On-Chain Data Warehouse & Pattern Mining System

---

## 1. Project Overview & Architecture
* **Subject:** Data Warehousing and Data Mining (DWDM)
* **Application Domain:** Decentralized Finance (DeFi) & On-Chain Risk Management
* **Core Philosophy:** Transforming unorganized, high-velocity blockchain transactional event streams into a structured Dimensional Star Schema to enable sub-second OLAP analysis, advanced anomaly detection, and autonomous decision-making.

---

## 2. Data Warehousing (DWH) Concepts Implemented

### 2.1 Dimensional Modeling: Star Schema
Unlike normalized 3NF schemas optimized for OLTP (On-Line Transaction Processing), our warehouse uses a **Star Schema** optimized for OLAP analytical queries.

* **Fact Tables (Contain numerical measures and metrics):**
  1. `fact_dex_swaps`: Atomic grain representing every individual token swap. Contains measures: `amount_usd`, `amount_in_tokens`, `amount_out_tokens`, `price_impact_pct`, `gas_used_gwei`.
  2. `fact_liquidity_events`: Records pool liquidity modifications (Mints, Burns, and Drains). Measures: `liquidity_usd_delta`, `remaining_pool_tvl_usd`, `drain_percentage`.
* **Dimension Tables (Provide contextual filtering and aggregation):**
  1. `dim_wallet`: Contains wallet profile, reputation score, and behavior attributes.
  2. `dim_token`: Contains token contract metadata, symbol, decimals, and verified status.
  3. `dim_liquidity_pool`: Contains pool addresses, protocol (e.g., UniswapV3, BaseSwap), and fee tiers.
  4. `dim_time`: Hierarchical temporal dimension (`timestamp`, `hour`, `day`, `day_of_week`, `week`, `month`, `year`).

### 2.2 Slowly Changing Dimensions (SCD Type 2)
* **What is SCD Type 2?** A technique to preserve historical data changes in dimension tables rather than overwriting existing records (Type 1).
* **Implementation in `dim_wallet`:**
  * When a wallet's reputation score drops or its behavior tag changes from `RETAIL` to `SMART_MONEY` or `SUSPECTED_RUGGER`, the previous row is closed by setting `is_current = FALSE` and `effective_end_date = NOW()`.
  * A new surrogate key (`wallet_sk = w_10_v2`) is inserted with `is_current = TRUE` and `effective_start_date = NOW()`.
  * **Viva Significance:** Allows analytical queries to accurately evaluate historical states as they existed at the time of past transactions.

### 2.3 Multi-Dimensional OLAP Operations

| OLAP Operation | Mathematical / SQL Definition | AegisFi Implementation |
| :--- | :--- | :--- |
| **Roll-Up** | Aggregates data by climbing up a dimension hierarchy (e.g., hour $\rightarrow$ day $\rightarrow$ month). | `olap.roll_up_volume("day")` aggregates swaps into daily volume and average price impact. |
| **Drill-Down** | Reverses roll-up; moves from aggregated high-level summaries down to detailed atomic data. | `olap.drill_down_pool_activity(pool_id)` steps from pool level down to individual block transaction hashes. |
| **Slice** | Filters the data cube along a single dimension. | `olap.slice_whale_activity(min_usd=50000)` extracts the subset where trade size $\ge \$50,000$. |
| **Dice** | Extracts a sub-cube by filtering across two or more dimensions simultaneously. | `olap.dice_subcube(token="WETH", behavior="SMART_MONEY")` slices across Token, Wallet, and Volume dimensions. |
| **Pivot** | Rotates the dimensional coordinate axes to provide a cross-tabulation view. | `olap.pivot_volume_by_day_and_token()` produces a matrix of Tokens vs Day-of-Week. |

---

## 3. Data Mining (DM) Concepts & Algorithms

### 3.1 Unsupervised Anomaly Detection: Isolation Forest
* **Objective:** Detect rug-pulls and liquidity-draining exploits before the pool hits zero.
* **Algorithm Mechanism:**
  * Construct an ensemble of Isolation Trees (iTrees).
  * Outliers have distinct values and are isolated near the root of the tree, resulting in a **short path length $h(x)$**.
  * The anomaly score $s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$, where $c(n)$ is the average path length of an unsuccessful search in a Binary Search Tree.
  * Score $\to 1$: Critical exploit (sudden $>85\%$ liquidity drain in 1 block).

### 3.2 Clustering: K-Means & DBSCAN
* **Objective:** Profile on-chain wallet behaviors into actionable archetypes.
* **K-Means Formulation:**
  * Minimizes Within-Cluster Sum of Squares (WCSS / Inertia):
    $$\text{Inertia} = \sum_{i=1}^{k} \sum_{x \in S_i} ||x - \mu_i||^2$$
  * We set $k=4$, discovering: *Smart Money*, *Whales*, *Arbitrage/MEV Bots*, and *Retail*.
* **Evaluation Metric (Silhouette Score):**
  $$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$
  * $a(i)$: Mean intra-cluster distance.
  * $b(i)$: Mean nearest-cluster distance.
  * Our model achieves **$s \approx 0.65$**, demonstrating dense, well-separated clusters.
* **DBSCAN:** Identifies density outliers ($min\_samples=3, \epsilon=1.2$) to flag anomalous burner/exploiter addresses.

### 3.3 Association Rule Mining: FP-Growth
* **Objective:** Market Basket Analysis of token co-trading portfolios.
* **Why FP-Growth over Apriori?** FP-Growth uses a compact Frequent Pattern Tree (FP-Tree) structure and eliminates the need for expensive repeated candidate generation passes over the database.
* **Key Metrics:**
  * **Support:** $P(A \cap B)$ — Proportion of wallets holding both tokens.
  * **Confidence:** $P(B | A) = \frac{P(A \cap B)}{P(A)}$ — Probability of buying Token B given Token A is held.
  * **Lift:** $\frac{P(A \cap B)}{P(A) \cdot P(B)}$ — Lift $> 1$ indicates strong positive affinity (not random chance).

---

## 4. Top 10 Viva Examination Questions & Answers

1. **Q: What is the difference between Star Schema and Snowflake Schema?**
   * *Answer:* A Star Schema has completely denormalized dimension tables connected directly to the central fact table in a single join, maximizing analytical query performance. A Snowflake Schema normalizes dimension tables into sub-dimensions (e.g., splitting `dim_token` into `dim_category`), reducing redundancy at the cost of requiring more complex multi-table joins.
2. **Q: Why did you implement SCD Type 2 instead of Type 1 or Type 3?**
   * *Answer:* Type 1 overwrites old values (destroying history), and Type 3 only stores the previous value in a single column. Type 2 preserves the complete audit history by inserting a new version record with effective date ranges, which is essential for forensic blockchain analysis.
3. **Q: What is the significance of the Silhouette Score in your K-Means clustering?**
   * *Answer:* The Silhouette Score ranges from -1 to +1. A score of 0.65 proves that wallets within the same archetype (e.g. Smart Money) are tightly clustered together while remaining distinctly separated from Retail or MEV bots.
4. **Q: How does Isolation Forest differ from standard classification like Random Forest?**
   * *Answer:* Random Forest is supervised and requires labeled data. Isolation Forest is unsupervised and isolates anomalies based purely on the principle that rare points require fewer random partitions to be isolated.
5. **Q: Why choose DuckDB for the Data Warehouse layer?**
   * *Answer:* DuckDB is a columnar, in-process analytical engine with vectorized query execution, providing sub-second OLAP query performance without requiring complex external server infrastructure.
6. **Q: Explain the role of Lift in Association Rule Mining.**
   * *Answer:* If Lift = 1, events A and B are independent. A Lift of 2.68 means that a wallet holding Token A is 2.68 times more likely to purchase Token B than a random wallet in the dataset.
7. **Q: What are the Fact tables in your schema and what are their measures?**
   * *Answer:* `fact_dex_swaps` (measures: `amount_usd`, `price_impact_pct`, `gas_used_gwei`) and `fact_liquidity_events` (measures: `liquidity_usd_delta`, `drain_percentage`).
8. **Q: How does the OLAP Pivot operation work in your dashboard?**
   * *Answer:* It transposes the time dimension (`day_of_week`) across columns and tokens across rows, aggregating the sum of `amount_usd` as cell values.
9. **Q: How does your agent use the Data Warehouse?**
   * *Answer:* Through tool-calling interfaces where the agent formulates SQL/OLAP parameters, retrieves aggregated analytical views, and passes them to Grok for synthesis.
10. **Q: What is the real-world utility of this system?**
    * *Answer:* It acts as an autonomous guardian that bridges on-chain data warehousing with real-time exploit prevention via ERC-4337 smart accounts.
