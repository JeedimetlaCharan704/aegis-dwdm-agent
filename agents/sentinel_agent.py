"""
AegisFi Sentinel Agent (Security & Exploit Guardian).
Autonomously detects rug-pulls and liquidity drains, reasons over threat vectors with Grok,
and triggers emergency fund rescue transactions.
"""

from agents.grok_client import GrokAgentClient
from agents.tools import tool_get_active_threats, tool_query_pool_drain_stats

class SentinelAgent:
    def __init__(self):
        self.grok = GrokAgentClient()
        self.role = "Autonomous Web3 Security Sentinel"

    def analyze_security_threats(self, threshold=0.75):
        """
        1. Calls Data Mining tool to detect active anomalies.
        2. Reasons over threat vectors using Grok.
        3. Returns structured security assessment and recommended action.
        """
        threat_data = tool_get_active_threats(threshold=threshold)
        drain_stats = tool_query_pool_drain_stats()

        system_prompt = (
            "You are Aegis Sentinel, an elite on-chain security agent for Web3. "
            "You monitor a real-time Data Warehouse and Isolation Forest anomaly detector. "
            "When given pool threat metrics, provide a precise, high-urgency security brief "
            "including Threat Level, Vulnerability Type, Mathematical Anomaly Details, and Rescue Recommendation."
        )

        user_prompt = f"""
        LIVE THREAT DATA FROM ISOLATION FOREST ENGINE:
        {threat_data}

        OLAP LIQUIDITY DRAIN PROFILE:
        {drain_stats['pools'][:3]}

        Assess whether an immediate on-chain rescue transaction must be initiated.
        """

        reasoning = self.grok.generate_response(system_prompt, user_prompt)
        
        has_critical_threat = threat_data["status"] == "THREAT_DETECTED" and len(threat_data["active_threats"]) > 0
        top_threat = threat_data["active_threats"][0] if has_critical_threat else None

        return {
            "agent": "Sentinel Guardian",
            "threat_detected": has_critical_threat,
            "top_threat": top_threat,
            "raw_threats": threat_data["active_threats"],
            "analysis": reasoning,
            "recommended_action": "AUTONOMOUS_RESCUE_REQUIRED" if has_critical_threat else "MAINTAIN_VIGILANCE"
        }

if __name__ == "__main__":
    sentinel = SentinelAgent()
    assessment = sentinel.analyze_security_threats(0.70)
    print("Sentinel Assessment:")
    print(assessment["analysis"])
