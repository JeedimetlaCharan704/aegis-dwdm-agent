"""
AegisFi Alpha Scout Agent (Smart Money & Strategy Scout).
Analyzes K-Means wallet clusters and FP-Growth association rules with Grok
to surface high-conviction on-chain trading alpha.
"""

from agents.grok_client import GrokAgentClient
from agents.tools import tool_get_smart_money_insights, tool_get_token_association_rules

class AlphaScoutAgent:
    def __init__(self):
        self.grok = GrokAgentClient()
        self.role = "Autonomous Web3 Alpha & Strategy Scout"

    def hunt_alpha_opportunities(self):
        """
        1. Calls Data Mining tools for Smart Money clusters and FP-Growth rules.
        2. Reasons over accumulation trends using Grok.
        3. Returns actionable trade insights.
        """
        smart_money = tool_get_smart_money_insights()
        rules = tool_get_token_association_rules()

        system_prompt = (
            "You are Aegis Alpha Scout, an autonomous DeFi quantitative intelligence agent. "
            "You synthesize K-Means wallet clustering results and FP-Growth association rules "
            "to discover high-conviction token accumulation patterns before retail traders."
        )

        user_prompt = f"""
        SMART MONEY CLUSTERING RESULTS (K-Means k=4):
        {smart_money}

        MINED TOKEN ASSOCIATION RULES (FP-Growth):
        {rules}

        Identify the strongest token accumulation play and explain the quantitative evidence.
        """

        reasoning = self.grok.generate_response(system_prompt, user_prompt)

        return {
            "agent": "Alpha Scout",
            "smart_wallets_tracked": len(smart_money.get("smart_money_wallets", [])),
            "association_rules_found": len(rules.get("top_rules", [])),
            "analysis": reasoning,
            "recommended_play": "ACCUMULATE_CO_TRADED_ASSETS"
        }

if __name__ == "__main__":
    alpha = AlphaScoutAgent()
    res = alpha.hunt_alpha_opportunities()
    print("Alpha Scout Analysis:")
    print(res["analysis"])
