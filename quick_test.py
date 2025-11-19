from hyperliquid.info import Info
import time
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Testing Hyperliquid API speed...")
info = Info(base_url='https://api.hyperliquid-testnet.xyz', skip_ws=True)

start = time.time()
data = info.l2_snapshot('ETH')
latency = (time.time() - start) * 1000

print(f'[OK] Latency: {latency:.2f} ms')
print(f'\nData structure: {type(data)}')
print(f'Keys: {data.keys() if isinstance(data, dict) else "N/A"}')

# Parse orderbook
levels = data['levels']
print(f'\nLevels type: {type(levels)}')
print(f'Levels length: {len(levels)}')
print(f'First element type: {type(levels[0])}')
print(f'First 2 items: {levels[:2] if isinstance(levels, list) else "N/A"}')

bids = levels[0] if isinstance(levels, list) else levels
asks = levels[1] if isinstance(levels, list) else levels

print(f'\nBids type: {type(bids)}')
if isinstance(bids, dict):
    print(f'Bids keys: {bids.keys()}')
elif isinstance(bids, list) and bids:
    print(f'First bid: {bids[0]}')

if isinstance(bids, list) and isinstance(asks, list) and bids and asks:
    best_bid = float(bids[0]['px']) if isinstance(bids[0], dict) else float(bids[0][0])
    best_ask = float(asks[0]['px']) if isinstance(asks[0], dict) else float(asks[0][0])
    mid = (best_bid + best_ask) / 2
    spread = best_ask - best_bid
    spread_pct = (spread / mid) * 100
    
    print(f'\nBest bid: ${best_bid:,.2f}')
    print(f'Best ask: ${best_ask:,.2f}')
    print(f'Mid price: ${mid:,.2f}')
    print(f'Spread: ${spread:.2f} ({spread_pct:.3f}%)')
else:
    print('Cannot parse orderbook data')

