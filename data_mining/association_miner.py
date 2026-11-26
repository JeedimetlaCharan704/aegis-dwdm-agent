"""
AegisFi Token Affinity & Association Rule Miner (DWDM Data Mining).
Implements FP-Growth (Frequent Pattern Growth) & Apriori to extract:
- Token Co-holding and Co-trading Association Rules
- Market Basket Analysis for Web3 Portfolios
- Cross-Asset accumulation patterns (e.g., {WETH} -> {LINK})
"""

import duckdb
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
from config import DB_PATH, FP_GROWTH_MIN_SUPPORT, FP_GROWTH_MIN_CONFIDENCE

class TokenAssociationMiner:
    def __init__(self, db_path=DB_PATH, min_support=FP_GROWTH_MIN_SUPPORT, min_confidence=FP_GROWTH_MIN_CONFIDENCE):
        self.db_path = str(db_path)
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.te = TransactionEncoder()

    def _extract_wallet_baskets(self):
        """
        Creates 'market baskets' of tokens traded by each wallet.
        """
        conn = duckdb.connect(self.db_path)
        sql = """
            SELECT 
                w.wallet_sk,
                tin.symbol AS token_symbol
            FROM fact_dex_swaps s
            JOIN dim_wallet w ON s.wallet_sk = w.wallet_sk
            JOIN dim_token tin ON s.token_in_id = tin.token_id
            UNION
            SELECT 
                w.wallet_sk,
                tout.symbol AS token_symbol
            FROM fact_dex_swaps s
            JOIN dim_wallet w ON s.wallet_sk = w.wallet_sk
            JOIN dim_token tout ON s.token_out_id = tout.token_id;
        """
        df = conn.execute(sql).df()
        conn.close()

        # Group into list of tokens per wallet
        baskets = df.groupby("wallet_sk")["token_symbol"].apply(list).tolist()
        return baskets

    def mine_rules(self):
        """
        Runs FP-Growth and extracts association rules sorted by Lift.
        """
        baskets = self._extract_wallet_baskets()
        if not baskets:
            return pd.DataFrame(), pd.DataFrame()

        # One-hot encode transactions
        te_ary = self.te.fit(baskets).transform(baskets)
        df_encoded = pd.DataFrame(te_ary, columns=self.te.columns_)

        # Mine Frequent Itemsets via FP-Growth
        frequent_itemsets = fpgrowth(df_encoded, min_support=self.min_support, use_colnames=True)
        if frequent_itemsets.empty:
            return pd.DataFrame(), pd.DataFrame()

        # Generate Association Rules
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=self.min_confidence)
        if rules.empty:
            return frequent_itemsets, pd.DataFrame()

        # Format items to clean strings
        rules["antecedents_str"] = rules["antecedents"].apply(lambda x: ", ".join(list(x)))
        rules["consequents_str"] = rules["consequents"].apply(lambda x: ", ".join(list(x)))
        
        # Round metrics for readability
        for col in ["support", "confidence", "lift", "leverage", "conviction"]:
            if col in rules.columns:
                rules[col] = rules[col].round(4)

        rules = rules.sort_values(by="lift", ascending=False)
        return frequent_itemsets, rules

    def get_token_recommendations(self, held_tokens):
        """
        Given a user's currently held tokens, returns mined association recommendations.
        """
        _, rules = self.mine_rules()
        if rules.empty:
            return []

        recommendations = []
        for _, row in rules.iterrows():
            antecedents = set(row["antecedents"])
            consequents = set(row["consequents"])
            if antecedents.issubset(set(held_tokens)) and not consequents.issubset(set(held_tokens)):
                recommendations.append({
                    "recommended_token": list(consequents)[0],
                    "based_on": list(antecedents),
                    "confidence": row["confidence"],
                    "lift": row["lift"]
                })
        return recommendations

if __name__ == "__main__":
    miner = TokenAssociationMiner()
    itemsets, rules = miner.mine_rules()
    print(f"Frequent Itemsets Found: {len(itemsets)}")
    print(f"Association Rules Mined: {len(rules)}")
    if not rules.empty:
        print(rules[["antecedents_str", "consequents_str", "support", "confidence", "lift"]].head(10))
