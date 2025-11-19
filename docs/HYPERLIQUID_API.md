# 🌐 Hyperliquid API Guide

คู่มือการใช้งาน Hyperliquid API สำหรับ Market Making

## 🔗 Endpoints

### Testnet
```
Base URL: https://api.hyperliquid-testnet.xyz
WebSocket: wss://api.hyperliquid-testnet.xyz/ws
Frontend: https://app.hyperliquid-testnet.xyz
```

### Mainnet
```
Base URL: https://api.hyperliquid.xyz
WebSocket: wss://api.hyperliquid.xyz/ws
Frontend: https://app.hyperliquid.xyz
```

## 📚 API Categories

### 1. Info API (Read-Only)

ไม่ต้องใช้ authentication, เรียกข้อมูลได้ฟรี

#### User State

```python
from hyperliquid.info import Info

info = Info(base_url="https://api.hyperliquid-testnet.xyz", skip_ws=True)
state = info.user_state(user_address)

# Returns
{
  "marginSummary": {
    "accountValue": "1000.0",      # Total account value
    "totalMarginUsed": "100.0",    # Used margin
    "totalNtlPos": "100.0"         # Total notional position
  },
  "crossMarginSummary": {
    "accountValue": "1000.0",
    "totalMarginUsed": "100.0"
  },
  "withdrawable": "900.0",         # Available to withdraw
  "assetPositions": [              # Open positions
    {
      "position": {
        "coin": "ETH",
        "szi": "0.1",              # Size (+ long, - short)
        "entryPx": "2000.0",       # Entry price
        "positionValue": "200.0",  # Position value
        "unrealizedPnl": "10.0",   # Unrealized P&L
        "leverage": {
          "value": 2,
          "type": "cross"
        }
      }
    }
  ]
}
```

#### L2 Order Book

```python
l2_data = info.l2_snapshot("ETH")

# Returns
{
  "coin": "ETH",
  "time": 1234567890,
  "levels": [
    # Bids [price, size]
    [
      ["1998.0", "1.5"],
      ["1997.0", "2.3"],
      ...
    ],
    # Asks [price, size]
    [
      ["2002.0", "1.2"],
      ["2003.0", "3.1"],
      ...
    ]
  ]
}

# Calculate mid price
bids = l2_data['levels'][0]
asks = l2_data['levels'][1]
best_bid = float(bids[0][0])
best_ask = float(asks[0][0])
mid_price = (best_bid + best_ask) / 2
```

#### Open Orders

```python
orders = info.open_orders(user_address)

# Returns
[
  {
    "coin": "ETH",
    "side": "B",           # B = Buy, A = Ask/Sell
    "limitPx": "1998.0",   # Limit price
    "sz": "0.01",          # Size
    "oid": 123456,         # Order ID
    "timestamp": 1234567890,
    "origSz": "0.01"       # Original size
  },
  ...
]
```

#### User Fills (Trade History)

```python
fills = info.user_fills(user_address)

# Returns
[
  {
    "coin": "ETH",
    "px": "2000.0",        # Fill price
    "sz": "0.01",          # Fill size
    "side": "B",           # B = Buy, A = Sell
    "time": 1234567890,
    "startPosition": "0.0",
    "dir": "Open Long",
    "closedPnl": "0.0",
    "fee": "-0.0004"       # Negative = rebate (maker)
  },
  ...
]
```

#### Market Summary

```python
meta = info.meta()

# Returns
{
  "universe": [
    {
      "name": "ETH",
      "szDecimals": 4,     # Size decimals
      "maxLeverage": 50,
      "onlyIsolated": false
    },
    ...
  ]
}

# Get all available symbols
symbols = [asset['name'] for asset in meta['universe']]
# ['BTC', 'ETH', 'SOL', 'MATIC', ...]
```

### 2. Exchange API (Trading)

ต้องใช้ authentication ด้วย private key

#### Place Order

```python
from hyperliquid.exchange import Exchange
from eth_account import Account

account = Account.from_key(private_key)
exchange = Exchange(
    account,
    base_url="https://api.hyperliquid-testnet.xyz",
    account_address=account.address
)

# Limit order
order = {
    "coin": "ETH",
    "is_buy": True,           # True = buy, False = sell
    "sz": 0.01,               # Size
    "limit_px": 2000.0,       # Limit price
    "order_type": {
        "limit": {
            "tif": "Gtc"      # Good-til-cancel
        }
    },
    "reduce_only": False      # False = can increase position
}

result = exchange.order(order, asset=0)

# Returns
{
  "status": "ok",
  "response": {
    "type": "order",
    "data": {
      "statuses": [
        {
          "resting": {
            "oid": 123456    # Order ID
          }
        }
      ]
    }
  }
}
```

#### Order Types

##### 1. Good-Til-Cancel (GTC)

```python
order_type = {"limit": {"tif": "Gtc"}}
# Order อยู่จนกว่าจะถูก fill หรือ cancel
```

##### 2. Immediate-or-Cancel (IOC)

```python
order_type = {"limit": {"tif": "Ioc"}}
# Fill ทันที เศษที่ fill ไม่ได้จะ cancel
```

##### 3. Fill-or-Kill (FOK)

```python
order_type = {"limit": {"tif": "Alo"}}
# ต้อง fill เต็มจำนวน ไม่งั้น cancel ทั้งหมด
```

##### 4. Market Order

```python
order = {
    "coin": "ETH",
    "is_buy": True,
    "sz": 0.01,
    "limit_px": 0,           # 0 for market order
    "order_type": {
        "market": {}
    }
}
```

#### Cancel Order

```python
# Cancel by order ID
result = exchange.cancel("ETH", order_id)

# Returns
{
  "status": "ok",
  "response": {
    "type": "cancel",
    "data": {
      "statuses": ["success"]
    }
  }
}
```

#### Cancel All Orders

```python
# Cancel all orders for a symbol
result = exchange.cancel_all_orders("ETH")

# Returns
{
  "status": "ok",
  "response": {
    "type": "cancel",
    "data": {
      "statuses": ["success", "success", ...]
    }
  }
}
```

#### Modify Order

```python
result = exchange.modify_order(
    oid=order_id,
    coin="ETH",
    is_buy=True,
    sz=0.02,           # New size
    limit_px=2001.0,   # New price
    order_type={"limit": {"tif": "Gtc"}}
)
```

## 🔐 Authentication

Hyperliquid ใช้ EIP-712 signatures

```python
from eth_account import Account
from eth_account.messages import encode_structured_data

# Load account
account = Account.from_key(private_key)

# Message structure (handled by SDK)
message = {
    "domain": {...},
    "message": {...},
    "primaryType": "Agent",
    "types": {...}
}

# Sign
signed = account.sign_message(encode_structured_data(message))
```

**หมายเหตุ:** SDK จัดการ authentication ให้อัตโนมัติ

## ⚡ WebSocket API

Realtime data streaming

### Subscribe to Order Book

```python
from hyperliquid.info import Info

# Create info client with WebSocket
info = Info(base_url="https://api.hyperliquid-testnet.xyz")

# Subscribe to L2 book
subscription = {
    "type": "l2Book",
    "coin": "ETH"
}

info.subscribe(subscription, callback)

def callback(message):
    print(f"Orderbook update: {message}")
```

### Subscribe to User Events

```python
# Subscribe to fills, orders, etc.
subscription = {
    "type": "userEvents",
    "user": user_address
}

info.subscribe(subscription, callback)

def callback(message):
    if message['data']['fills']:
        print(f"Order filled: {message['data']['fills']}")
```

### Subscribe to Trades

```python
# Subscribe to recent trades
subscription = {
    "type": "trades",
    "coin": "ETH"
}

info.subscribe(subscription, callback)
```

## 💰 Fee Structure

### Maker/Taker Fees

```
Maker: -0.002% (rebate)
Taker: 0.05%
```

**ตัวอย่าง:**

```python
# Limit order ที่ rests in orderbook (maker)
trade_value = 0.01 * 2000 = $20
maker_rebate = $20 * 0.00002 = $0.0004 (รับคืน)

# Market order (taker)
trade_value = $20
taker_fee = $20 * 0.0005 = $0.01 (จ่าย)
```

## 🎯 Best Practices

### 1. Rate Limiting

```python
import time

# ไม่ควรเกิน 10 requests/second
min_interval = 0.1  # 100ms

for order in orders:
    place_order(order)
    time.sleep(min_interval)
```

### 2. Error Handling

```python
def place_order_safe(exchange, order):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = exchange.order(order)
            if result['status'] == 'ok':
                return result
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
    return None
```

### 3. Order Validation

```python
def validate_order(order, balance):
    # Check size decimals
    if len(str(order['sz']).split('.')[-1]) > 4:
        return False, "Size too many decimals"
    
    # Check price decimals
    if len(str(order['limit_px']).split('.')[-1]) > 2:
        return False, "Price too many decimals"
    
    # Check balance
    order_value = order['sz'] * order['limit_px']
    if order_value > balance:
        return False, "Insufficient balance"
    
    return True, "OK"
```

### 4. Position Monitoring

```python
def monitor_position(info, address, max_position):
    state = info.user_state(address)
    
    for asset_pos in state['assetPositions']:
        position = asset_pos['position']
        size = abs(float(position['szi']))
        
        if size > max_position:
            print(f"⚠️ Position {position['coin']} exceeds limit!")
            return False
    
    return True
```

## 📊 Code Examples

### Complete Trading Flow

```python
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from eth_account import Account

# Setup
private_key = "your_private_key"
account = Account.from_key(private_key)

info = Info(base_url="https://api.hyperliquid-testnet.xyz", skip_ws=True)
exchange = Exchange(account, base_url="https://api.hyperliquid-testnet.xyz")

# 1. Get account balance
state = info.user_state(account.address)
balance = float(state['marginSummary']['accountValue'])
print(f"Balance: ${balance:.2f}")

# 2. Get mid price
l2 = info.l2_snapshot("ETH")
best_bid = float(l2['levels'][0][0][0])
best_ask = float(l2['levels'][1][0][0])
mid_price = (best_bid + best_ask) / 2
print(f"Mid price: ${mid_price:.2f}")

# 3. Place orders
spread = 0.002  # 0.2%
order_size = 0.01

bid_price = round(mid_price * (1 - spread), 2)
ask_price = round(mid_price * (1 + spread), 2)

# Place buy order
buy_order = {
    "coin": "ETH",
    "is_buy": True,
    "sz": order_size,
    "limit_px": bid_price,
    "order_type": {"limit": {"tif": "Gtc"}},
    "reduce_only": False
}
buy_result = exchange.order(buy_order)
print(f"Buy order: {buy_result}")

# Place sell order
sell_order = {
    "coin": "ETH",
    "is_buy": False,
    "sz": order_size,
    "limit_px": ask_price,
    "order_type": {"limit": {"tif": "Gtc"}},
    "reduce_only": False
}
sell_result = exchange.order(sell_order)
print(f"Sell order: {sell_result}")

# 4. Check open orders
open_orders = info.open_orders(account.address)
print(f"Open orders: {len(open_orders)}")

# 5. Cancel all (when done)
exchange.cancel_all_orders("ETH")
```

## 🔍 Debugging

### Enable Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Inspect API Responses

```python
import json

result = exchange.order(order)
print(json.dumps(result, indent=2))
```

## 📚 Resources

- [Hyperliquid Docs](https://hyperliquid.gitbook.io/)
- [Python SDK GitHub](https://github.com/hyperliquid-dex/hyperliquid-python-sdk)
- [API Examples](https://github.com/hyperliquid-dex/hyperliquid-python-sdk/tree/master/examples)
- [Discord Community](https://discord.gg/hyperliquid)

---

**หมายเหตุ:** API อาจมีการเปลี่ยนแปลง ตรวจสอบ documentation ล่าสุดเสมอ

