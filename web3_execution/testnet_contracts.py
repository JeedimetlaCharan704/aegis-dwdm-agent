"""
Contract ABIs and Addresses for Web3 Execution Layer.
Targeted for Base Sepolia (Chain ID: 84532) and local simulation.
"""

# Base Sepolia Testnet Addresses
BASE_SEPOLIA_CONFIG = {
    "chain_id": 84532,
    "chain_name": "Base Sepolia",
    "router_address": "0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24",
    "weth_address": "0x4200000000000000000000000000000000000006",
    "usdc_address": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
    "block_explorer": "https://sepolia.basescan.org"
}

# Standard ERC-20 Minimal ABI
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}],
        "name": "approve",
        "outputs": [{"name": "success", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}],
        "name": "allowance",
        "outputs": [{"name": "remaining", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
        "name": "transfer",
        "outputs": [{"name": "success", "type": "bool"}],
        "type": "function"
    }
]

# Minimal DEX Router ABI (Uniswap V2 / BaseSwap compatible)
ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForTokens",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
