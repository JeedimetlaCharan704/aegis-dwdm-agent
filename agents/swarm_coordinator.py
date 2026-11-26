"""
AegisFi Swarm Coordinator.
Orchestrates the multi-agent swarm (Sentinel, Alpha Scout, Executor) and handles user inquiries.
"""

from agents.grok_client import GrokAgentClient
from agents.sentinel_agent import SentinelAgent
from agents.alpha_agent import AlphaScoutAgent
from agents.tools import tool_query_olap_rollup

class AegisSwarmCoordinator:
    def __init__(self):
        self.grok = GrokAgentClient()
        self.sentinel = SentinelAgent()
        self.alpha = AlphaScoutAgent()

    def run_surveillance_cycle(self, threat_threshold=0.75):
        """
        Executes a complete autonomous surveillance cycle:
        1. Sentinel scans for exploits and rug-pulls.
        2. Alpha Scout scans for smart-money accumulation.
        3. Coordinator aggregates findings into an executive briefing.
        """
        print("[*] Coordinator: Launching autonomous multi-agent surveillance cycle...")
        security_report = self.sentinel.analyze_security_threats(threshold=threat_threshold)
        alpha_report = self.alpha.hunt_alpha_opportunities()

        briefing = {
            "cycle_status": "COMPLETED",
            "threat_alert": security_report["threat_detected"],
            "security_report": security_report,
            "alpha_report": alpha_report
        }
        return briefing

    def process_user_query(self, query):
        """
        Processes free-form natural language queries from the user.
        Routes to the appropriate specialist agent or DWH tool.
        """
        q_lower = query.lower()
        if any(w in q_lower for w in ["threat", "rug", "exploit", "safety", "danger", "security"]):
            return self.sentinel.analyze_security_threats()
        elif any(w in q_lower for w in ["alpha", "smart money", "whale", "buy", "accumulat", "token"]):
            return self.alpha.hunt_alpha_opportunities()
        elif any(w in q_lower for w in ["olap", "volume", "rollup", "cube", "warehouse"]):
            rollup = tool_query_olap_rollup("day")
            system_prompt = "You are Aegis Data Warehouse Architect. Explain the OLAP roll-up findings."
            user_prompt = f"User asks: {query}. Data: {rollup}"
            explanation = self.grok.generate_response(system_prompt, user_prompt)
            return {"agent": "DWH Architect", "analysis": explanation, "data": rollup}
        else:
            system_prompt = "You are AegisFi Coordinator, an autonomous Web3 AI operating on an on-chain Data Warehouse."
            resp = self.grok.generate_response(system_prompt, query)
            return {"agent": "Swarm Coordinator", "analysis": resp}

if __name__ == "__main__":
    coordinator = AegisSwarmCoordinator()
    cycle = coordinator.run_surveillance_cycle()
    print("Surveillance Cycle Completed. Threat Alert:", cycle["threat_alert"])
