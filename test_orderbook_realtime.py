"""
Realtime Orderbook Monitor with WebSocket (Low Latency!)

Press Ctrl+C to stop
"""

from hyperliquid.info import Info
import time
import sys
import os
import threading
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Configuration
SYMBOL = "ETH"
TESTNET = True
NUM_LEVELS = 10
UPDATE_DISPLAY_INTERVAL = 0.5  # Display refresh rate (seconds)

# Global state
latest_orderbook = None
latest_update_time = None
total_updates = 0
update_latencies = []
ws_connected = False


def clear_screen():
    """Clear terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


def on_orderbook_update(message):
    """Callback when orderbook updates via WebSocket"""
    global latest_orderbook, latest_update_time, total_updates, update_latencies

    start_time = time.time()

    try:
        # Debug: print first update
        if total_updates == 0:
            print(f"✓ First update received! Message type: {type(message)}", flush=True)
            print(
                f"Message keys: {message.keys() if isinstance(message, dict) else 'Not a dict'}",
                flush=True,
            )
            if isinstance(message, dict) and "data" in message:
                print(f"Data keys: {message['data'].keys()}", flush=True)

        # Extract orderbook data from WebSocket message
        # WebSocket format: {'channel': 'l2Book', 'data': {...}}
        if isinstance(message, dict) and "data" in message:
            orderbook_data = message["data"]
        else:
            orderbook_data = message

        # Store the orderbook data
        latest_orderbook = orderbook_data
        latest_update_time = datetime.now()
        total_updates += 1

        # Calculate processing latency
        processing_latency = (time.time() - start_time) * 1000
        update_latencies.append(processing_latency)

        # Keep only last 100 samples
        if len(update_latencies) > 100:
            update_latencies.pop(0)

    except Exception as e:
        print(f"❌ Error in callback: {e}", flush=True)
        import traceback

        traceback.print_exc()


def display_orderbook():
    """Display the latest orderbook data"""
    global latest_orderbook, latest_update_time, total_updates, update_latencies, ws_connected

    if not latest_orderbook:
        return

    try:
        # Parse orderbook
        bids = latest_orderbook["levels"][0]
        asks = latest_orderbook["levels"][1]

        # Calculate statistics
        if update_latencies:
            avg_latency = sum(update_latencies) / len(update_latencies)
            min_latency = min(update_latencies)
            max_latency = max(update_latencies)
            current_latency = update_latencies[-1]
        else:
            avg_latency = min_latency = max_latency = current_latency = 0

        # Calculate time since last update
        if latest_update_time:
            time_since_update = (
                datetime.now() - latest_update_time
            ).total_seconds() * 1000
        else:
            time_since_update = 0

        # Clear screen
        clear_screen()

        # Display header
        print("=" * 100)
        print(
            f"WEBSOCKET ORDERBOOK - {SYMBOL} {'(Testnet)' if TESTNET else '(Mainnet)'}".center(
                100
            )
        )
        print("=" * 100)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        print(
            f"Connection: {'CONNECTED' if ws_connected else 'DISCONNECTED'} | Total Updates: {total_updates}"
        )
        print(
            f"Processing: Current={current_latency:.1f}ms | Avg={avg_latency:.1f}ms | Min={min_latency:.1f}ms | Max={max_latency:.1f}ms"
        )
        print(f"Last Update: {time_since_update:.0f}ms ago")

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
                bid_str = (
                    f"${b_price:>14,.2f} {b_size:>12.4f} ${b_total:>9,.2f} {b_num:>5}"
                )
            else:
                bid_str = " " * 48

            # Ask side
            if i < len(asks):
                ask = asks[i]
                a_price = float(ask["px"])
                a_size = float(ask["sz"])
                a_total = a_price * a_size
                a_num = ask["n"]
                ask_str = (
                    f"${a_price:>14,.2f} {a_size:>12.4f} ${a_total:>9,.2f} {a_num:>5}"
                )
            else:
                ask_str = " " * 48

            print(f"{bid_str} | {ask_str}")

        print("=" * 100)

        # Performance indicator
        if current_latency < 10:
            status = "[EXCELLENT - WebSocket]"
        elif current_latency < 50:
            status = "[VERY GOOD - WebSocket]"
        elif current_latency < 100:
            status = "[GOOD]"
        else:
            status = "[NORMAL]"

        print(f"\nPerformance: {status} | Updates arrive via PUSH (no polling!)")
        print(f"Press Ctrl+C to stop")

    except Exception as e:
        print(f"Error displaying orderbook: {e}")


def main():
    global ws_connected

    print(f"Starting WebSocket Orderbook Monitor for {SYMBOL}", flush=True)
    print(f"Network: {'Testnet' if TESTNET else 'Mainnet'}", flush=True)
    print("Connecting to WebSocket...\n", flush=True)
    # Setup WebSocket client
    testnet_url = "https://api.hyperliquid-testnet.xyz" if TESTNET else None
    start_time = time.time()

    try:
        # Create Info client with WebSocket enabled
        print("Creating WebSocket connection...", flush=True)
        info = Info(base_url=testnet_url, skip_ws=False)
        print("WebSocket client created successfully!", flush=True)

        print("Subscribing to orderbook updates...", flush=True)

        # Subscribe to L2 orderbook
        subscription = {"type": "l2Book", "coin": SYMBOL}

        # Subscribe with callback
        print(f"Attempting to subscribe to {SYMBOL}...", flush=True)
        info.subscribe(subscription, on_orderbook_update)
        ws_connected = True

        print(
            f"✓ Connected! Waiting for orderbook updates for {SYMBOL}...\n", flush=True
        )
        time.sleep(2)

        # Display loop
        try:
            while True:
                display_orderbook()
                time.sleep(UPDATE_DISPLAY_INTERVAL)

        except KeyboardInterrupt:
            print("\n\n" + "=" * 100)
            print("STOPPED BY USER".center(100))
            print("=" * 100)

            if update_latencies:
                duration = time.time() - start_time
                avg_latency = sum(update_latencies) / len(update_latencies)
                min_latency = min(update_latencies)
                max_latency = max(update_latencies)

                print("\nFinal Statistics:")
                print(f"  Total Updates:         {total_updates}")
                print(f"  Average Latency:       {avg_latency:.2f} ms")
                print(f"  Min Latency:           {min_latency:.2f} ms")
                print(f"  Max Latency:           {max_latency:.2f} ms")
                print(
                    f"  Update Frequency:      {total_updates / duration:.2f} updates/sec"
                )
                print(f"  Total Duration:        {duration:.1f} seconds")
                print("=" * 100)

            print("\nGoodbye!")

    except Exception as e:
        print(f"\n❌ Error: {e}", flush=True)
        print(f"Error type: {type(e).__name__}", flush=True)
        import traceback

        print("\nFull traceback:", flush=True)
        traceback.print_exc()
        print(
            "\nWebSocket connection failed. Make sure hyperliquid-python-sdk supports WebSocket.",
            flush=True,
        )
        print(
            "You may need to update: pip install --upgrade hyperliquid-python-sdk",
            flush=True,
        )


if __name__ == "__main__":
    main()
