"""
Basic trading examples for Hyperliquid

This script demonstrates:
1. Connecting to Hyperliquid testnet
2. Getting account info
3. Getting market data
4. Placing orders
5. Cancelling orders
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import config as cfg
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from eth_account import Account


def main():
    # Setup clients
    account = Account.from_key(cfg.PRIVATE_KEY)
    testnet_url = "https://api.hyperliquid-testnet.xyz" if cfg.TESTNET else None
    
    info = Info(base_url=testnet_url, skip_ws=True)
    exchange = Exchange(account, base_url=testnet_url, account_address=account.address)
    
    print("=" * 60)
    print("🌐 Hyperliquid Trading Examples")
    print("=" * 60)
    print(f"📍 Address: {account.address}\n")
    
    # Example 1: Get account balance
    print("1️⃣  Getting Account Balance")
    print("-" * 60)
    state = info.user_state(account.address)
    balance = float(state['marginSummary']['accountValue'])
    withdrawable = float(state['withdrawable'])
    print(f"💰 Account Value: ${balance:.2f}")
    print(f"💵 Withdrawable: ${withdrawable:.2f}")
    
    # Show positions if any
    if state['assetPositions']:
        print("\n📊 Open Positions:")
        for asset_pos in state['assetPositions']:
            pos = asset_pos['position']
            print(f"  • {pos['coin']}: {pos['szi']} @ ${pos['entryPx']} "
                  f"(PnL: ${pos['unrealizedPnl']})")
    print()
    
    # Example 2: Get market data
    print("2️⃣  Getting Market Data")
    print("-" * 60)
    symbol = "ETH"
    
    # Get orderbook
    l2_data = info.l2_snapshot(symbol)
    bids = l2_data['levels'][0]
    asks = l2_data['levels'][1]
    
    best_bid_price = float(bids[0][0])
    best_bid_size = float(bids[0][1])
    best_ask_price = float(asks[0][0])
    best_ask_size = float(asks[0][1])
    mid_price = (best_bid_price + best_ask_price) / 2
    spread = best_ask_price - best_bid_price
    spread_pct = (spread / mid_price) * 100
    
    print(f"📈 {symbol} Market Data:")
    print(f"  Best Bid: ${best_bid_price:.2f} ({best_bid_size} {symbol})")
    print(f"  Best Ask: ${best_ask_price:.2f} ({best_ask_size} {symbol})")
    print(f"  Mid Price: ${mid_price:.2f}")
    print(f"  Spread: ${spread:.2f} ({spread_pct:.3f}%)")
    print()
    
    # Example 3: Check open orders
    print("3️⃣  Checking Open Orders")
    print("-" * 60)
    open_orders = info.open_orders(account.address)
    
    if open_orders:
        print(f"📋 You have {len(open_orders)} open order(s):")
        for order in open_orders:
            side = "BUY" if order['side'] == 'B' else "SELL"
            print(f"  • {side} {order['sz']} {order['coin']} @ ${order['limitPx']} "
                  f"(ID: {order['oid']})")
    else:
        print("📋 No open orders")
    print()
    
    # Example 4: Place limit orders
    print("4️⃣  Placing Test Orders")
    print("-" * 60)
    
    # Calculate prices for test orders
    order_size = 0.01  # 0.01 ETH
    order_spread = 0.01  # 1% away from mid (so they won't fill immediately)
    
    test_bid_price = round(mid_price * (1 - order_spread), 2)
    test_ask_price = round(mid_price * (1 + order_spread), 2)
    
    print(f"Placing test orders (1% away from mid, unlikely to fill):")
    print(f"  • BUY {order_size} {symbol} @ ${test_bid_price:.2f}")
    print(f"  • SELL {order_size} {symbol} @ ${test_ask_price:.2f}")
    
    # Uncomment to actually place orders
    place_orders = input("\nPlace these orders? (y/n): ").lower() == 'y'
    
    if place_orders:
        # Place buy order
        buy_order = {
            "coin": symbol,
            "is_buy": True,
            "sz": order_size,
            "limit_px": test_bid_price,
            "order_type": {"limit": {"tif": "Gtc"}},
            "reduce_only": False
        }
        
        buy_result = exchange.order(buy_order)
        print(f"✅ Buy order result: {buy_result['status']}")
        
        # Place sell order
        sell_order = {
            "coin": symbol,
            "is_buy": False,
            "sz": order_size,
            "limit_px": test_ask_price,
            "order_type": {"limit": {"tif": "Gtc"}},
            "reduce_only": False
        }
        
        sell_result = exchange.order(sell_order)
        print(f"✅ Sell order result: {sell_result['status']}")
        
        print()
        
        # Example 5: Cancel orders
        print("5️⃣  Cancelling Orders")
        print("-" * 60)
        
        # Wait a bit
        import time
        time.sleep(2)
        
        cancel_orders = input("Cancel all orders? (y/n): ").lower() == 'y'
        
        if cancel_orders:
            result = exchange.cancel_all_orders(symbol)
            print(f"✅ Cancelled all {symbol} orders: {result['status']}")
    else:
        print("⏭️  Skipped placing orders")
    
    print()
    print("=" * 60)
    print("✅ Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

