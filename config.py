import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "aegis_warehouse.duckdb"

# Load .env if present
load_dotenv(PROJECT_ROOT / ".env")

# Grok / Groq LLM Configuration (Auto-detects GroqCloud vs xAI)
GROK_API_KEY = os.getenv("GROK_API_KEY", "").strip()

if GROK_API_KEY.startswith("gsk_"):
    # User provided GroqCloud API key (High-speed 120B model)
    GROK_BASE_URL = os.getenv("GROK_BASE_URL", "https://api.groq.com/openai/v1")
    GROK_MODEL = os.getenv("GROK_MODEL", "openai/gpt-oss-120b")
    LLM_PROVIDER_NAME = "GroqCloud (GPT-OSS-120B)"
elif GROK_API_KEY.startswith("xai-"):
    # xAI Grok API key
    GROK_BASE_URL = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")
    GROK_MODEL = os.getenv("GROK_MODEL", "grok-beta")
    LLM_PROVIDER_NAME = "xAI (Grok-Beta)"
else:
    GROK_BASE_URL = os.getenv("GROK_BASE_URL", "https://api.groq.com/openai/v1")
    GROK_MODEL = os.getenv("GROK_MODEL", "llama-3.3-70b-versatile")
    LLM_PROVIDER_NAME = "Groq / Grok LLM"

# Check if active LLM API is available
IS_LLM_CONFIGURED = bool(GROK_API_KEY and not GROK_API_KEY.startswith("your_"))

# Web3 Configuration
WEB3_RPC_URL = os.getenv("WEB3_RPC_URL", "https://sepolia.base.org")
CHAIN_ID = int(os.getenv("CHAIN_ID", "84532"))  # Base Sepolia default
BASESCAN_API_KEY = os.getenv("BASESCAN_API_KEY", "")
DEVELOPER_WALLET_ADDRESS = os.getenv("DEVELOPER_WALLET_ADDRESS", "0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
DEVELOPER_WALLET_PRIVATE_KEY = os.getenv("DEVELOPER_WALLET_PRIVATE_KEY", "")

# Autonomous Guardian Execution Policy
AUTO_RESCUE_ENABLED = os.getenv("AUTO_RESCUE_ENABLED", "true").lower() == "true"
RISK_THRESHOLD_RESCUE = float(os.getenv("RISK_THRESHOLD_RESCUE", "0.80"))
MAX_SLIPPAGE_PERCENT = float(os.getenv("MAX_SLIPPAGE_PERCENT", "3.0"))

# Data Mining Parameters (DWDM)
ISOLATION_FOREST_CONTAMINATION = 0.05
KMEANS_WALLET_CLUSTERS = 4
FP_GROWTH_MIN_SUPPORT = 0.02
FP_GROWTH_MIN_CONFIDENCE = 0.40
