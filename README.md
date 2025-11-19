# Pure Market Making Strategy for Hyperliquid

🤖 Market making bot สำหรับ Hyperliquid DEX ที่ใช้ Pure Market Making Strategy

## 🌟 Features

- ✅ Pure Market Making Strategy
- ✅ Inventory Skew Management
- ✅ Position Risk Management
- ✅ Testnet Support
- ✅ Configurable Parameters
- ✅ Logging System

## 📋 Requirements

- Python 3.8+
- Hyperliquid Testnet/Mainnet Account
- pip-tools

## 🚀 Quick Start

### 1. ติดตั้ง Dependencies

```bash
# ติดตั้ง pip-tools และ compile dependencies
make setup

# หรือทำทีละขั้นตอน
pip install pip-tools
make pip-compile
make pip-sync
```

### 2. ตั้งค่า Configuration

```bash
# Copy example config
cp config/secrets.env.example config/secrets.env

# แก้ไข config/secrets.env ใส่ private key ของคุณ
```

**config/secrets.env:**

```env
PRIVATE_KEY=your_private_key_here
TESTNET=True
SYMBOL=ETH
SPREAD_PCT=0.002
ORDER_SIZE=0.01
MAX_POSITION=0.05
REFRESH_INTERVAL=10
```

### 3. รัน Bot

```bash
make run

# หรือ
python main.py
```

## 🛠️ Development

### Available Make Commands

```bash
make help          # แสดง commands ทั้งหมด
make setup         # Setup project ครั้งแรก
make pip-compile   # Compile requirements.in -> requirements.txt
make pip-sync      # Sync environment กับ requirements.txt
make install       # Install dependencies
make run           # รัน bot
make test          # รัน tests
make lint          # รัน linter
make format        # Format code
make clean         # ลบ cache files
```

### โครงสร้างโปรเจกต์

```
pure-market-making-strategy/
├── config/
│   ├── config.yaml          # การตั้งค่าทั่วไป (future)
│   ├── secrets.env          # API keys, private keys (ห้าม commit!)
│   └── secrets.env.example  # ตัวอย่าง config
├── src/
│   ├── __init__.py
│   ├── exchange/
│   │   ├── __init__.py
│   │   └── hyperliquid.py  # Hyperliquid API wrapper
│   ├── strategy/
│   │   ├── __init__.py
│   │   └── market_maker.py # Market making logic
│   └── utils/
│       ├── __init__.py
│       ├── logger.py        # Logging utilities
│       └── risk_manager.py  # Risk management
├── tests/                   # Unit tests
├── logs/                    # Log files (auto-created)
├── main.py                  # Entry point
├── requirements.in          # Dependencies specification
├── requirements.txt         # Compiled dependencies (generated)
├── Makefile                 # Make commands
├── .gitignore
├── LICENSE
└── README.md
```

## 📊 Strategy Parameters

| Parameter          | Description                      | Default        |
| ------------------ | -------------------------------- | -------------- |
| `SYMBOL`           | Trading symbol                   | `ETH`          |
| `SPREAD_PCT`       | Bid-ask spread (%)               | `0.002` (0.2%) |
| `ORDER_SIZE`       | Order size per side              | `0.01`         |
| `MAX_POSITION`     | Maximum position size            | `0.05`         |
| `REFRESH_INTERVAL` | Order refresh interval (seconds) | `10`           |

## 🎯 How It Works

### Pure Market Making Strategy

1. **วาง Bid/Ask Orders**: วาง orders สองฝั่งพร้อมกัน

   - Bid: ต่ำกว่า mid price
   - Ask: สูงกว่า mid price

2. **Inventory Skew**: ปรับราคาตาม position

   - Position บวก (long): เลื่อนราคาขายลง
   - Position ลบ (short): เลื่อนราคาซื้อขึ้น

3. **Position Limit**: จำกัด max position

   - หยุดซื้อเมื่อถึง max long
   - หยุดขายเมื่อถึง max short

4. **Order Refresh**: ยกเลิก + วาง orders ใหม่ทุกๆ interval

## 🔐 Security

- ⚠️ **ห้ามเปิดเผย** `config/secrets.env` (มี private key)
- ✅ ใช้ `.gitignore` กันไม่ให้ commit secrets
- 💡 ทดสอบบน **testnet** ก่อนเสมอ

## 📚 Resources

- [Hyperliquid Docs](https://hyperliquid.gitbook.io/)
- [Hyperliquid Python SDK](https://github.com/hyperliquid-dex/hyperliquid-python-sdk)
- [Testnet App](https://app.hyperliquid-testnet.xyz)

## 🚧 TODO

- [ ] WebSocket integration for real-time data
- [ ] Volatility-based spread adjustment
- [ ] Multiple symbol support
- [ ] Backtesting framework
- [ ] Performance metrics & reporting
- [ ] Discord/Telegram notifications
- [ ] Unit tests

## ⚠️ Disclaimer

This bot is for educational purposes only. Trading cryptocurrencies involves substantial risk. Use at your own risk.

## 📄 License

Apache License 2.0
