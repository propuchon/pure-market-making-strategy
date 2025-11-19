"""Centralized configuration management"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logger
logger = logging.getLogger(__name__)

# Load environment variables
_config_path = Path("config/secrets.env")
if _config_path.exists():
    load_dotenv(_config_path)
    logger.debug(f"Loaded config from {_config_path}")
else:
    load_dotenv()
    logger.debug("Loaded config from environment")


# ############# REQUIRED SETTINGS #############

PRIVATE_KEY: str = os.getenv(key="PRIVATE_KEY", default="")
TESTNET: bool = os.getenv(key="TESTNET", default="True").lower() in ("true", "1", "yes", "t")


# ############# STRATEGY PARAMETERS #############

SYMBOL: str = os.getenv(key="SYMBOL", default="ETH")
SPREAD_PCT: float = float(os.getenv(key="SPREAD_PCT", default="0.002"))
ORDER_SIZE: float = float(os.getenv(key="ORDER_SIZE", default="0.01"))
MAX_POSITION: float = float(os.getenv(key="MAX_POSITION", default="0.05"))
REFRESH_INTERVAL: int = int(os.getenv(key="REFRESH_INTERVAL", default="10"))


# ############# RISK MANAGEMENT #############

MAX_POSITION_VALUE: float = float(os.getenv(key="MAX_POSITION_VALUE", default="1000.0"))
MAX_DRAWDOWN_PCT: float = float(os.getenv(key="MAX_DRAWDOWN_PCT", default="0.10"))


# ############# LOGGING #############

LOG_LEVEL: str = os.getenv(key="LOG_LEVEL", default="INFO")
LOG_DIR: str = os.getenv(key="LOG_DIR", default="logs")


# ############# VALIDATION #############

def validate_config() -> None:
    """Validate configuration values"""
    if not PRIVATE_KEY:
        raise ValueError(
            "PRIVATE_KEY not found in environment variables. "
            "Please create config/secrets.env from config/secrets.env.example"
        )
    
    if SPREAD_PCT <= 0:
        raise ValueError("SPREAD_PCT must be positive")
    
    if ORDER_SIZE <= 0:
        raise ValueError("ORDER_SIZE must be positive")
    
    if MAX_POSITION <= 0:
        raise ValueError("MAX_POSITION must be positive")
    
    if REFRESH_INTERVAL < 1:
        raise ValueError("REFRESH_INTERVAL must be at least 1 second")
    
    if MAX_DRAWDOWN_PCT <= 0 or MAX_DRAWDOWN_PCT > 1:
        raise ValueError("MAX_DRAWDOWN_PCT must be between 0 and 1")


def display_config() -> None:
    """Display configuration (hide sensitive info)"""
    logger.info("=" * 60)
    logger.info("⚙️  CONFIGURATION")
    logger.info("=" * 60)
    logger.info(f"Network:            {'Testnet' if TESTNET else 'Mainnet'}")
    logger.info(f"Symbol:             {SYMBOL}")
    logger.info(f"Spread:             {SPREAD_PCT * 100:.2f}%")
    logger.info(f"Order Size:         {ORDER_SIZE}")
    logger.info(f"Max Position:       ±{MAX_POSITION}")
    logger.info(f"Refresh Interval:   {REFRESH_INTERVAL}s")
    logger.info(f"Max Position Value: ${MAX_POSITION_VALUE:,.2f}")
    logger.info(f"Max Drawdown:       {MAX_DRAWDOWN_PCT * 100:.1f}%")
    logger.info(f"Log Level:          {LOG_LEVEL}")
    if PRIVATE_KEY:
        logger.info(f"Private Key:        {'*' * 10}{PRIVATE_KEY[-6:]}")
    else:
        logger.info(f"Private Key:        ❌ NOT SET")
    logger.info("=" * 60)


# Validate on import
validate_config()

