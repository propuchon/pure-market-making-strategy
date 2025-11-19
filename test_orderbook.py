"""
Test orderbook fetching speed - Standalone version

Display realtime orderbook data and measure API call latency
No config file required - just run it!
"""

import os
import time
from datetime import datetime
from hyperliquid.info import Info


# Configuration (edit here)
SYMBOL = "ETH"
TESTNET = True
REFRESH_INTERVAL = 1  # seconds


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def format_orderbook(orderbook: dict, num_levels: int = 10) -> str:
    """Format orderbook for display"""
    bids = orderbook['bids'][:num_levels]
    asks = orderbook['asks'][:num_levels]
    
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append(f"📊 ORDER BOOK - {SYMBOL}")
    lines.append("=" * 80)
    
    # Calculate mid price
    if bids and asks:
        best_bid = float(bids[0][0])
        best_ask = float(asks[0][0])
        mid_price = (best_bid + best_ask) / 2
        spread = best_ask - best_bid
        spread_pct = (spread / mid_price) * 100
        
        lines.append(f"Mid Price: ${mid_price:,.2f} | Spread: ${spread:.2f} ({spread_pct:.3f}%)")
        lines.append("=" * 80)
    
    # Header
    lines.append(f"{'BIDS':^38} | {'ASKS':^38}")
    lines.append(f"{'Price':>15} {'Size':>10} {'Total':>10} | {'Price':>15} {'Size':>10} {'Total':>10}")
    lines.append("-" * 80)
    
    # Display levels
    max_levels = max(len(asks), len(bids))
    for i in range(min(num_levels, max_levels)):
        # Bid side
        if i < len(bids):
            bid_price = float(bids[i][0])
            bid_size = float(bids[i][1])
            bid_total = bid_price * bid_size
            bid_str = f"${bid_price:>14,.2f} {bid_size:>10.4f} ${bid_total:>9,.2f}"
        else:
            bid_str = " " * 38
        
        # Ask side
        if i < len(asks):
            ask_price = float(asks[i][0])
            ask_size = float(asks[i][1])
            ask_total = ask_price * ask_size
            ask_str = f"${ask_price:>14,.2f} {ask_size:>10.4f} ${ask_total:>9,.2f}"
        else:
            ask_str = " " * 38
        
        lines.append(f"{bid_str} | {ask_str}")
    
    lines.append("=" * 80)
    
    return "\n".join(lines)


def main():
    print("🚀 Starting Orderbook Speed Test")
    print(f"📍 Symbol: {SYMBOL}")
    print(f"🌐 Network: {'Testnet' if TESTNET else 'Mainnet'}")
    print("\nPress Ctrl+C to stop\n")
    
    # Setup client
    testnet_url = "https://api.hyperliquid-testnet.xyz" if TESTNET else None
    info = Info(base_url=testnet_url, skip_ws=True)
    
    # Statistics
    call_times = []
    total_calls = 0
    
    try:
        while True:
            # Measure API call time
            start_time = time.time()
            
            try:
                # Fetch orderbook
                l2_data = info.l2_snapshot(SYMBOL)
                
                # Calculate latency
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                
                # Update statistics
                call_times.append(latency_ms)
                total_calls += 1
                
                # Keep only last 100 samples for moving average
                if len(call_times) > 100:
                    call_times.pop(0)
                
                avg_latency = sum(call_times) / len(call_times)
                min_latency = min(call_times)
                max_latency = max(call_times)
                
                # Clear screen and display
                clear_screen()
                
                # Display statistics
                print("=" * 80)
                print("⚡ API PERFORMANCE STATISTICS")
                print("=" * 80)
                print(f"Timestamp:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                print(f"Total Calls:     {total_calls}")
                print(f"Current Latency: {latency_ms:.2f} ms")
                print(f"Avg Latency:     {avg_latency:.2f} ms (last {len(call_times)} samples)")
                print(f"Min Latency:     {min_latency:.2f} ms")
                print(f"Max Latency:     {max_latency:.2f} ms")
                
                # Parse orderbook
                orderbook = {
                    'bids': l2_data['levels'][0],
                    'asks': l2_data['levels'][1]
                }
                
                # Display orderbook
                print(format_orderbook(orderbook, num_levels=10))
                
                # Performance indicator
                if latency_ms < 100:
                    status = "🟢 EXCELLENT"
                elif latency_ms < 300:
                    status = "🟡 GOOD"
                elif latency_ms < 500:
                    status = "🟠 FAIR"
                else:
                    status = "🔴 SLOW"
                
                print(f"\nPerformance: {status}")
                print(f"\nRefreshing every {REFRESH_INTERVAL}s... (Press Ctrl+C to stop)")
                
            except Exception as e:
                print(f"\n❌ Error fetching orderbook: {e}")
                print(f"Retrying in {REFRESH_INTERVAL}s...")
            
            # Wait before next update
            time.sleep(REFRESH_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")
        
        if call_times:
            print("\n📊 Final Statistics:")
            print("=" * 80)
            print(f"Total API Calls:     {total_calls}")
            print(f"Average Latency:     {avg_latency:.2f} ms")
            print(f"Min Latency:         {min_latency:.2f} ms")
            print(f"Max Latency:         {max_latency:.2f} ms")
            print("=" * 80)
        
        print("✅ Goodbye!")


if __name__ == "__main__":
    main()

