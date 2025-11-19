"""
Realtime Orderbook Monitor with Latency Tracking

Press Ctrl+C to stop
"""

from hyperliquid.info import Info
import time
import sys
import os

# Fix Windows console encoding
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Configuration
SYMBOL = "ETH"
TESTNET = True
REFRESH_INTERVAL = 1  # seconds
NUM_LEVELS = 10


def clear_screen():
    """Clear terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


def main():
    print(f"Starting Orderbook Monitor for {SYMBOL}")
    print(f"Network: {'Testnet' if TESTNET else 'Mainnet'}\n")
    time.sleep(1)

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
                data = info.l2_snapshot(SYMBOL)

                # Calculate latency
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000

                # Update statistics
                call_times.append(latency_ms)
                total_calls += 1

                # Keep only last 100 samples
                if len(call_times) > 100:
                    call_times.pop(0)

                avg_latency = sum(call_times) / len(call_times)
                min_latency = min(call_times)
                max_latency = max(call_times)

                # Parse orderbook
                bids = data["levels"][0]  # list of dicts with 'px', 'sz', 'n'
                asks = data["levels"][1]

                # Clear screen
                clear_screen()

                # Display header
                print("=" * 100)
                print(
                    f"ORDERBOOK MONITOR - {SYMBOL} {'(Testnet)' if TESTNET else '(Mainnet)'}".center(
                        100
                    )
                )
                print("=" * 100)
                print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Total Calls: {total_calls}")
                print(
                    f"Latency: Current={latency_ms:.1f}ms | Avg={avg_latency:.1f}ms | Min={min_latency:.1f}ms | Max={max_latency:.1f}ms"
                )

                # Calculate mid price and spread
                if bids and asks:
                    best_bid_price = float(bids[0]["px"])
                    best_bid_size = float(bids[0]["sz"])
                    best_ask_price = float(asks[0]["px"])
                    best_ask_size = float(asks[0]["sz"])
                    mid_price = (best_bid_price + best_ask_price) / 2
                    spread = best_ask_price - best_bid_price
                    spread_pct = (spread / mid_price) * 100

                    print(
                        f"Mid Price: ${mid_price:,.2f} | Spread: ${spread:.2f} ({spread_pct:.3f}%)"
                    )

                # Display orderbook
                print("=" * 100)
                print(f"{'BIDS':^48} | {'ASKS':^48}")
                print(
                    f"{'Price':>15} {'Size':>12} {'Total':>10} {'Num':>5} | {'Price':>15} {'Size':>12} {'Total':>10} {'Num':>5}"
                )
                print("-" * 100)

                # Display levels
                for i in range(min(NUM_LEVELS, max(len(bids), len(asks)))):
                    # Bid side
                    if i < len(bids):
                        bid = bids[i]
                        b_price = float(bid["px"])
                        b_size = float(bid["sz"])
                        b_total = b_price * b_size
                        b_num = bid["n"]
                        bid_str = f"${b_price:>14,.2f} {b_size:>12.4f} ${b_total:>9,.2f} {b_num:>5}"
                    else:
                        bid_str = " " * 48

                    # Ask side
                    if i < len(asks):
                        ask = asks[i]
                        a_price = float(ask["px"])
                        a_size = float(ask["sz"])
                        a_total = a_price * a_size
                        a_num = ask["n"]
                        ask_str = f"${a_price:>14,.2f} {a_size:>12.4f} ${a_total:>9,.2f} {a_num:>5}"
                    else:
                        ask_str = " " * 48

                    print(f"{bid_str} | {ask_str}")

                print("=" * 100)

                # Performance indicator
                if latency_ms < 100:
                    status = "[EXCELLENT]"
                elif latency_ms < 300:
                    status = "[GOOD]"
                elif latency_ms < 500:
                    status = "[FAIR]"
                else:
                    status = "[SLOW]"

                print(
                    f"\nPerformance: {status} | Refreshing every {REFRESH_INTERVAL}s... (Press Ctrl+C to stop)"
                )

            except Exception as e:
                print(f"\nError fetching orderbook: {e}")
                print(f"Retrying in {REFRESH_INTERVAL}s...")

            # Wait before next update
            time.sleep(REFRESH_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 100)
        print("STOPPED BY USER".center(100))
        print("=" * 100)

        if call_times:
            print("\nFinal Statistics:")
            print(f"  Total API Calls:   {total_calls}")
            print(f"  Average Latency:   {avg_latency:.2f} ms")
            print(f"  Min Latency:       {min_latency:.2f} ms")
            print(f"  Max Latency:       {max_latency:.2f} ms")
            print("=" * 100)

        print("\nGoodbye!")


if __name__ == "__main__":
    main()
