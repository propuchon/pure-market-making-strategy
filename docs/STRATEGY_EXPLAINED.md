# 📚 Pure Market Making Strategy Explained

เอกสารอธิบายกลยุทธ์ Pure Market Making แบบละเอียด

## 🎯 Pure Market Making คืออะไร?

**Market Making** คือการให้สภาพคล่อง (liquidity) แก่ตลาดโดยการวาง orders ทั้งสองฝั่ง (bid และ ask) พร้อมกัน

### หลักการพื้นฐาน

```
Bid Side    Mid Price    Ask Side
(ซื้อ)        |          (ขาย)
            $2000
   $1998  ←--+--→  $2002
              ↑
           Spread
           ($4 = 0.2%)
```

**การทำกำไร:**
- ซื้อที่ $1998 (bid ถูก fill)
- ขายที่ $2002 (ask ถูก fill)
- กำไร = $4 per cycle (0.2%)

## 🔄 Cycle ของ Market Maker

### 1. Quote Orders

วาง bid/ask orders พร้อมกัน:

```python
BID: Buy 0.01 ETH @ $1998 (2% below mid)
ASK: Sell 0.01 ETH @ $2002 (2% above mid)
```

### 2. Wait for Fills

- **Best case:** ทั้งสองฝั่งถูก fill → ได้กำไร
- **Common case:** ถูก fill ทีละฝั่ง → มี position
- **Worst case:** ราคาวิ่งทิศทางเดียว → position ขาดทุน

### 3. Refresh Orders

ยกเลิก orders เก่า และวางใหม่ตามราคาปัจจุบัน

## 📊 Components หลัก

### 1. Spread Management

**Spread** = ระยะห่างระหว่าง bid และ ask

```python
spread_pct = 0.002  # 0.2%
mid_price = 2000

# Calculate prices
half_spread = mid_price * spread_pct  # $4
bid_price = mid_price - half_spread   # $1998
ask_price = mid_price + half_spread   # $2002
```

**Trade-off:**
- **Spread แคบ:** fill บ่อย แต่กำไรน้อย, risk สูง
- **Spread กว้าง:** กำไรมาก แต่ fill น้อย

### 2. Inventory Skew

ปรับราคาตาม **position** ที่ถืออยู่

#### ปัญหา: Position Risk

```
Time 0: Position = 0
       BID: $1998, ASK: $2002

Time 1: BID filled → Position = +0.01 (long)
       ถ้าราคาตก → ขาดทุน

Time 2: BID filled again → Position = +0.02 (long มากขึ้น)
       Risk เพิ่มขึ้นเรื่อย ๆ
```

#### วิธีแก้: Inventory Skew

เลื่อนราคาเพื่อ **encourage** การ fill ฝั่งที่ต้องการ:

```python
# ถ้า position = +0.03 (long มาก)
# ต้องการขาย → เลื่อนราคาขายลง

skew_factor = position / max_position  # 0.03 / 0.05 = 0.6
skew_adjustment = mid_price * 0.0005 * skew_factor  # $0.60

# Adjust prices
bid_price = mid_price - half_spread - skew_adjustment  # ซื้อแพงขึ้น (discourage)
ask_price = mid_price + half_spread - skew_adjustment  # ขายถูกลง (encourage)
```

**ผลลัพธ์:**
```
Position = 0 (neutral)
  BID: $1998, ASK: $2002

Position = +0.03 (long)
  BID: $1997.40, ASK: $2001.40  ← ขายถูกลงเพื่อลด position

Position = -0.03 (short)
  BID: $1998.60, ASK: $2002.60  ← ซื้อถูกลงเพื่อลด position
```

### 3. Position Limits

จำกัด position ที่ถือได้สูงสุด:

```python
max_position = 0.05  # ±0.05 ETH

current_position = 0.04

# Check before placing orders
can_buy = abs(position + order_size) <= max_position
# = abs(0.04 + 0.01) <= 0.05 → True ✅

can_sell = abs(position - order_size) <= max_position
# = abs(0.04 - 0.01) <= 0.05 → True ✅
```

เมื่อ position ถึงขี้ดจำกัด:

```python
current_position = 0.05  # Max long

can_buy = abs(0.05 + 0.01) <= 0.05 → False ❌ หยุดซื้อ
can_sell = abs(0.05 - 0.01) <= 0.05 → True ✅ ขายได้
```

## 🎲 Risk Factors

### 1. Adverse Selection

ถูก fill เฉพาะเมื่อราคาเคลื่อนไหวในทิศทางที่เสียเปรียบ

**ตัวอย่าง:**
```
ราคาปกติ: $2000
BID: $1998, ASK: $2002

ข่าวดีออก → ราคากระโดดไป $2050
→ BID ถูก fill @ $1998
→ ASK ไม่ถูก fill
→ ถือ position @ $1998 แต่ราคาตลาด $2050
→ ได้ unrealized profit แต่ถ้าขายที่ $2002 จะพลาดโอกาส
```

### 2. Trending Markets

ตลาดวิ่งทิศทางเดียวต่อเนื่อง

```
Uptrend: $2000 → $2100 → $2200
→ BID ถูก fill บ่อย → long position สะสม
→ ASK ไม่ถูก fill → ไม่ได้ realize profit

จนกว่าราคาจะ pullback
```

**วิธีแก้:**
- เพิ่ม spread ในตลาดผันผวน
- Tighten position limits
- ใช้ stop loss

### 3. Liquidity Risk

Orders ถูก fill ไม่เท่ากัน

```
BID filled: 10 ครั้ง → long 0.1 ETH
ASK filled: 2 ครั้ง → ขาย 0.02 ETH
Net position: +0.08 ETH (long)
```

## 📈 P&L Breakdown

### กำไรจาก Spread

```
Cycle 1: Buy @ $1998, Sell @ $2002 → +$4
Cycle 2: Buy @ $2001, Sell @ $2005 → +$4
Cycle 3: Buy @ $1995, Sell @ $1999 → +$4
---
Total: +$12
```

### Unrealized P&L from Position

```
Entry: Buy @ $1998
Current: $2010
Position: +0.01 ETH

Unrealized P&L = (2010 - 1998) * 0.01 = +$0.12
```

### Trading Fees

Hyperliquid fees (example):
- Maker: -0.002% (รับ rebate)
- Taker: 0.05%

```
Trade Value: $2000 * 0.01 = $20
Maker rebate: $20 * 0.00002 = $0.0004 (รับคืน)
```

## 🛡️ Risk Management

### 1. Position Sizing

ควบคุมขนาด position ตาม capital:

```python
account_value = $1000
max_position_pct = 5%  # 5% of capital

max_position_value = $1000 * 0.05 = $50
eth_price = $2000
max_position_size = $50 / $2000 = 0.025 ETH
```

### 2. Drawdown Limits

หยุดเมื่อขาดทุนถึงระดับที่กำหนด:

```python
peak_balance = $1000
current_balance = $900
drawdown = (1000 - 900) / 1000 = 10%

if drawdown >= max_drawdown (10%):
    stop_trading()
```

### 3. Volatility Adjustment

เพิ่ม spread เมื่อตลาดผันผวน:

```python
normal_volatility: spread = 0.2%
high_volatility: spread = 0.5%
```

## 📊 Performance Metrics

### Key Metrics

1. **Sharpe Ratio**: Risk-adjusted returns
2. **Win Rate**: % ของ profitable cycles
3. **Avg P&L per cycle**: กำไรเฉลี่ยต่อรอบ
4. **Max Drawdown**: ขาดทุนสูงสุด
5. **Fill Rate**: % ของ orders ที่ถูก fill

## 🎯 Optimization Strategies

### 1. Dynamic Spread

ปรับ spread ตาม:
- Volatility (ผันผวน → spread กว้าง)
- Volume (volume สูง → spread แคบ)
- Time of day (active hours → spread แคบ)

### 2. Multiple Levels

วาง orders หลาย levels:

```
ASK 3: 0.005 ETH @ $2006
ASK 2: 0.01 ETH @ $2004
ASK 1: 0.01 ETH @ $2002
----------- Mid: $2000
BID 1: 0.01 ETH @ $1998
BID 2: 0.01 ETH @ $1996
BID 3: 0.005 ETH @ $1994
```

### 3. Cross-Asset Hedging

Hedge position ด้วย futures/options

## 🚀 Advanced Topics

### 1. Statistical Arbitrage

- Mean reversion models
- Cointegration pairs trading
- Time series forecasting

### 2. Machine Learning

- Predict short-term price movements
- Optimize spread dynamically
- Detect market regime changes

### 3. High-Frequency Strategies

- Latency optimization
- Co-location
- Direct market access

## 📚 Further Reading

- [Market Microstructure Theory](https://en.wikipedia.org/wiki/Market_microstructure)
- [Algorithmic Trading](https://www.quantstart.com/)
- [Options Market Making](https://www.optionseducation.org/)

---

**สรุป:**

Pure Market Making เป็นกลยุทธ์ที่:
- ✅ ให้กำไรสม่ำเสมอในตลาดที่มี liquidity
- ✅ Risk-neutral (ถ้าจัดการ inventory ดี)
- ⚠️ ต้องระวัง trending markets
- ⚠️ ต้องมี risk management ที่ดี

**Success factors:**
1. Tight spread management
2. Good inventory control
3. Fast execution
4. Proper risk limits

