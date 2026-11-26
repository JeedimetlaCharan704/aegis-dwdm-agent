import unittest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from agents.grok_client import GrokAgentClient
from agents.sentinel_agent import SentinelAgent
from agents.alpha_agent import AlphaScoutAgent
from agents.swarm_coordinator import AegisSwarmCoordinator
from web3_execution.executor import AegisWeb3Executor
from config import DEVELOPER_WALLET_ADDRESS

class TestAgentsAndWeb3(unittest.TestCase):
    def test_grok_client(self):
        client = GrokAgentClient()
        resp = client.generate_response("System", "Analyze threat on pool_test")
        self.assertIsInstance(resp, str)
        self.assertGreater(len(resp), 20)

    def test_sentinel_agent(self):
        sentinel = SentinelAgent()
        res = sentinel.analyze_security_threats(0.70)
        self.assertIn("analysis", res)
        self.assertIn("recommended_action", res)

    def test_alpha_agent(self):
        alpha = AlphaScoutAgent()
        res = alpha.hunt_alpha_opportunities()
        self.assertIn("analysis", res)
        self.assertIn("smart_wallets_tracked", res)

    def test_swarm_coordinator(self):
        coord = AegisSwarmCoordinator()
        res = coord.run_surveillance_cycle()
        self.assertEqual(res["cycle_status"], "COMPLETED")

    def test_web3_executor_rescue(self):
        executor = AegisWeb3Executor()
        rescue = executor.execute_emergency_rescue(
            user_wallet=DEVELOPER_WALLET_ADDRESS,
            pool_id="pool_pepe_weth",
            token_symbol="PEPE-SAFE",
            amount_tokens=10000.0,
            threat_score=0.95
        )
        self.assertEqual(rescue["status"], "SUCCESS")
        self.assertTrue(rescue["approval_revoked"])
        self.assertIsNotNone(rescue["tx_hash"])

if __name__ == "__main__":
    unittest.main()
