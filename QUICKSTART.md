# 🚀 Quick Start Guide

คู่มือเริ่มต้นใช้งาน Hyperliquid Market Making Bot แบบง่าย ๆ

## 📦 ติดตั้งและตั้งค่า

### 1. Clone และ Setup Project

```bash
# Clone repository (ถ้ายังไม่ได้ clone)
git clone <your-repo-url>
cd pure-market-making-strategy

# Setup dependencies ครั้งเดียว
make setup
```

คำสั่ง `make setup` จะทำ:
- ติดตั้ง pip-tools
- Compile requirements.in → requirements.txt
- ติดตั้ง dependencies ทั้งหมด

### 2. สร้าง Testnet Wallet

1. เปิด [Hyperliquid Testnet](https://app.hyperliquid-testnet.xyz)
2. เชื่อมต่อ/สร้าง wallet (Metamask, WalletConnect, etc.)
3. ขอ testnet USDC จาก faucet
4. Export private key จาก wallet

**⚠️ สำคัญ:** Private key ห้ามเปิดเผยและใช้เฉพาะ testnet เท่านั้น!

### 3. ตั้งค่า Configuration

```bash
# Copy example config
cp config/secrets.env.example config/secrets.env

# แก้ไขด้วย text editor
notepad config/secrets.env  # Windows
# หรือ
nano config/secrets.env     # Linux/Mac
```

**config/secrets.env:**
```env
PRIVATE_KEY=abc123def456...  # ใส่ private key ของคุณ (ไม่ต้องมี 0x)
TESTNET=True                 # ใช้ testnet

# Parameters (ปรับได้ตามต้องการ)
SYMBOL=ETH
SPREAD_PCT=0.002             # 0.2% spread
ORDER_SIZE=0.01              # 0.01 ETH per order
MAX_POSITION=0.05            # Max ±0.05 ETH
REFRESH_INTERVAL=10          # Refresh ทุก 10 วินาที
```

### 4. รัน Bot

```bash
make run
```

หรือ

```bash
python main.py
```

## 📊 ตัวอย่าง Output

```
✅ Connected to Hyperliquid Testnet
📍 Address: 0x1234...5678
💰 Account Value: $1000.00
💵 Withdrawable: $1000.00

🚀 Starting Market Maker for ETH
📈 Spread: 0.20%
💰 Order Size: 0.01
⚖️  Max Position: ±0.05

📊 Mid Price: $2000.00 | Position: 0.0000
🟢 Placing BID: 0.01 @ $1998.00
🔴 Placing ASK: 0.01 @ $2002.00
✅ Order placed: {...}

⏳ Waiting 10s before refresh...
```

## 🎯 ทดสอบการทำงาน

### ตรวจสอบ Orders

1. เปิด [Hyperliquid Testnet App](https://app.hyperliquid-testnet.xyz)
2. ไปที่หน้า "Orders"
3. จะเห็น bid/ask orders ที่ bot วาง

### ดู Logs

```bash
# Logs จะถูกเก็บใน logs/ directory
cat logs/market_maker_*.log

# หรือดูแบบ real-time
tail -f logs/market_maker_*.log
```

## ⚙️ ปรับแต่ง Strategy

### เปลี่ยน Spread

```env
# Spread กว้างขึ้น = ปลอดภัยกว่า แต่ถูก fill น้อยลง
SPREAD_PCT=0.005  # 0.5% spread
```

### เปลี่ยนขนาด Order

```env
# Order เล็กลง = risk น้อยลง
ORDER_SIZE=0.005  # 0.005 ETH
```

### เปลี่ยน Refresh Rate

```env
# Refresh เร็วขึ้น = ติดตามราคาดีกว่า แต่ใช้ gas มากกว่า
REFRESH_INTERVAL=5  # 5 วินาที
```

### เปลี่ยน Symbol

```env
# ลอง symbol อื่น
SYMBOL=BTC
# หรือ
SYMBOL=SOL
```

## 🛑 หยุดการทำงาน

กด `Ctrl+C` เพื่อหยุด bot

Bot จะ:
1. ยกเลิก orders ที่ค้างอยู่ทั้งหมด
2. แสดงสถานะสุดท้าย
3. ปิดการทำงานอย่างปลอดภัย

```
^C
🛑 Stopping Market Maker...
✅ All orders cancelled for ETH
✅ All orders cancelled. Goodbye!
```

## 📚 คำสั่งที่มีประโยชน์

```bash
# Compile dependencies ใหม่ (เมื่อแก้ requirements.in)
make pip-compile

# Sync environment กับ requirements.txt
make pip-sync

# รัน tests
make test

# Format code
make format

# ลบ cache files
make clean
```

## ❓ Troubleshooting

### ❌ Error: PRIVATE_KEY not found

**วิธีแก้:** ตรวจสอบว่าสร้างไฟล์ `config/secrets.env` และใส่ PRIVATE_KEY แล้ว

### ❌ Error getting balance / orderbook

**วิธีแก้:** 
1. ตรวจสอบ internet connection
2. ตรวจสอบว่า Hyperliquid testnet ทำงานปกติ
3. ลอง refresh อีกครั้ง

### ❌ Orders ไม่ถูก fill

**สาเหตุ:**
- Spread กว้างเกินไป → ลด SPREAD_PCT
- ตลาดไม่มี volume → ลองเปลี่ยน symbol หรือเวลา
- Price movement เร็วเกินไป → เพิ่ม REFRESH_INTERVAL

### ⚠️ Position เกิน limit

Bot จะหยุดวาง orders ฝั่งที่เกิน MAX_POSITION อัตโนมัติ

## 🎓 เรียนรู้เพิ่มเติม

- [README.md](README.md) - Documentation หลัก
- [Hyperliquid Docs](https://hyperliquid.gitbook.io/)
- [Python SDK Examples](https://github.com/hyperliquid-dex/hyperliquid-python-sdk/tree/master/examples)

## 💬 ติดปัญหา?

1. ตรวจสอบ logs ใน `logs/` directory
2. ตรวจสอบ Hyperliquid testnet status
3. ดู error messages ในคอนโซล

---

**Happy Trading! 🚀**

