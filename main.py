from src import config as cfg
from src.exchange.hyperliquid import HyperliquidClient
from src.strategy.market_maker import PureMarketMaker
from src.utils.logger import setup_logger

def main():
    # Setup logger
    logger = setup_logger(log_dir=cfg.LOG_DIR)
    
    logger.info("=" * 60)
    logger.info("🤖 Hyperliquid Market Maker Bot")
    logger.info("=" * 60)
    
    # Display configuration
    cfg.display_config()
    
    # สร้าง Hyperliquid client
    client = HyperliquidClient(
        private_key=cfg.PRIVATE_KEY,
        testnet=cfg.TESTNET
    )
    
    # แสดง balance
    balance = client.get_balance()
    logger.info(f"💰 Account Value: ${balance['total_value']:.2f}")
    logger.info(f"💵 Withdrawable: ${balance['withdrawable']:.2f}")
    
    # สร้างและรัน market maker
    market_maker = PureMarketMaker(
        client=client,
        symbol=cfg.SYMBOL,
        spread_pct=cfg.SPREAD_PCT,
        order_size=cfg.ORDER_SIZE,
        max_position=cfg.MAX_POSITION,
        refresh_interval=cfg.REFRESH_INTERVAL
    )
    
    market_maker.run()

if __name__ == "__main__":
    main()

