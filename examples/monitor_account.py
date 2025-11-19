"""
Account monitoring script

Real-time monitoring of:
- Account balance
- Open positions
- Open orders
- Recent fills
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import config as cfg
from hyperliquid.info import Info
from eth_account import Account


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def format_pnl(pnl: float) -> str:
    """Format P&L with color"""
    if pnl > 0:
        return f"+${pnl:.2f}"
    elif pnl < 0:
        return f"-${abs(pnl):.2f}"
    else:
        return f"${pnl:.2f}"


def main():
    # Setup client
    account = Account.from_key(cfg.PRIVATE_KEY)
    testnet_url = "https://api.hyperliquid-testnet.xyz" if cfg.TESTNET else None
    info = Info(base_url=testnet_url, skip_ws=True)
    
    print("🔍 Starting Account Monitor...")
    print(f"📍 Address: {account.address}")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        while True:
            clear_screen()
            
            # Header
            print("=" * 80)
            print("🔍 HYPERLIQUID ACCOUNT MONITOR".center(80))
            print("=" * 80)
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Address: {account.address}")
            print("=" * 80)
            
            # Get account state
            try:
                state = info.user_state(account.address)
                
                # Account Summary
                print("\n💰 ACCOUNT SUMMARY")
                print("-" * 80)
                account_value = float(state['marginSummary']['accountValue'])
                margin_used = float(state['marginSummary']['totalMarginUsed'])
                withdrawable = float(state['withdrawable'])
                
                margin_pct = (margin_used / account_value * 100) if account_value > 0 else 0
                
                print(f"Account Value:    ${account_value:>12,.2f}")
                print(f"Margin Used:      ${margin_used:>12,.2f} ({margin_pct:.1f}%)")
                print(f"Available:        ${withdrawable:>12,.2f}")
                
                # Positions
                print("\n📊 OPEN POSITIONS")
                print("-" * 80)
                
                if state['assetPositions']:
                    total_upnl = 0
                    
                    print(f"{'Symbol':<8} {'Size':>12} {'Entry':>12} "
                          f"{'Current':>12} {'UPnL':>15} {'Value':>12}")
                    print("-" * 80)
                    
                    for asset_pos in state['assetPositions']:
                        pos = asset_pos['position']
                        coin = pos['coin']
                        size = float(pos['szi'])
                        entry_px = float(pos['entryPx'])
                        position_value = float(pos['positionValue'])
                        upnl = float(pos['unrealizedPnl'])
                        
                        # Get current price
                        try:
                            l2 = info.l2_snapshot(coin)
                            current_px = (float(l2['levels'][0][0][0]) + 
                                        float(l2['levels'][1][0][0])) / 2
                        except:
                            current_px = 0
                        
                        total_upnl += upnl
                        
                        direction = "LONG" if size > 0 else "SHORT"
                        print(f"{coin:<8} {size:>12.4f} ${entry_px:>11,.2f} "
                              f"${current_px:>11,.2f} {format_pnl(upnl):>15} "
                              f"${position_value:>11,.2f}")
                    
                    print("-" * 80)
                    print(f"{'Total Unrealized P&L:':>65} {format_pnl(total_upnl):>15}")
                else:
                    print("No open positions")
                
                # Open Orders
                print("\n📋 OPEN ORDERS")
                print("-" * 80)
                
                open_orders = info.open_orders(account.address)
                
                if open_orders:
                    print(f"{'Symbol':<8} {'Side':>6} {'Size':>12} "
                          f"{'Price':>12} {'Value':>12} {'Order ID':>12}")
                    print("-" * 80)
                    
                    for order in open_orders:
                        coin = order['coin']
                        side = "BUY" if order['side'] == 'B' else "SELL"
                        size = float(order['sz'])
                        price = float(order['limitPx'])
                        value = size * price
                        oid = order['oid']
                        
                        print(f"{coin:<8} {side:>6} {size:>12.4f} "
                              f"${price:>11,.2f} ${value:>11,.2f} {oid:>12}")
                    
                    print("-" * 80)
                    print(f"Total orders: {len(open_orders)}")
                else:
                    print("No open orders")
                
                # Recent Fills
                print("\n✅ RECENT FILLS (Last 5)")
                print("-" * 80)
                
                fills = info.user_fills(account.address)
                
                if fills:
                    recent_fills = fills[:5]
                    
                    print(f"{'Time':<20} {'Symbol':<8} {'Side':>6} "
                          f"{'Size':>12} {'Price':>12} {'Fee':>10}")
                    print("-" * 80)
                    
                    for fill in recent_fills:
                        timestamp = datetime.fromtimestamp(fill['time'] / 1000)
                        time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                        coin = fill['coin']
                        side = "BUY" if fill['side'] == 'B' else "SELL"
                        size = float(fill['sz'])
                        price = float(fill['px'])
                        fee = float(fill['fee'])
                        
                        print(f"{time_str:<20} {coin:<8} {side:>6} "
                              f"{size:>12.4f} ${price:>11,.2f} "
                              f"{format_pnl(fee):>10}")
                else:
                    print("No recent fills")
                
            except Exception as e:
                print(f"\n❌ Error fetching data: {e}")
            
            # Footer
            print("\n" + "=" * 80)
            print("Refreshing in 5 seconds... (Press Ctrl+C to stop)")
            print("=" * 80)
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor stopped by user")
        print("✅ Goodbye!")


if __name__ == "__main__":
    main()

