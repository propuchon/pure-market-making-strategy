import time
from typing import Dict, Optional, Tuple
from ..exchange.hyperliquid import HyperliquidClient

class PureMarketMaker:
    """Pure Market Making Strategy"""
    
    def __init__(
        self,
        client: HyperliquidClient,
        symbol: str,
        spread_pct: float = 0.001,  # 0.1% spread
        order_size: float = 0.01,    # ขนาด order (ETH)
        max_position: float = 0.1,   # position สูงสุด
        refresh_interval: int = 10   # refresh ทุก 10 วินาที
    ):
        self.client = client
        self.symbol = symbol
        self.spread_pct = spread_pct
        self.order_size = order_size
        self.max_position = max_position
        self.refresh_interval = refresh_interval
        
        self.bid_order_id = None
        self.ask_order_id = None
        
    def get_current_position(self) -> float:
        """ดึง position ปัจจุบัน"""
        balance = self.client.get_balance()
        for pos in balance.get('positions', []):
            if pos['position']['coin'] == self.symbol:
                return float(pos['position']['szi'])
        return 0.0
    
    def calculate_order_prices(self, mid_price: float, position: float) -> Tuple[float, float]:
        """
        คำนวณราคา bid/ask พร้อม inventory skew
        
        Returns:
            (bid_price, ask_price)
        """
        base_spread = mid_price * self.spread_pct
        
        # Inventory skew: ถ้า position บวก (long) -> เลื่อนขายถูกลง/ซื้อแพงขึ้น
        skew_factor = position / self.max_position if self.max_position > 0 else 0
        skew_adjustment = mid_price * 0.0005 * skew_factor  # 0.05% per full position
        
        bid_price = mid_price - base_spread - skew_adjustment
        ask_price = mid_price + base_spread - skew_adjustment
        
        # ปัดเศษตาม tick size (Hyperliquid ใช้ significant figures)
        bid_price = round(bid_price, 2)
        ask_price = round(ask_price, 2)
        
        return bid_price, ask_price
    
    def cancel_existing_orders(self):
        """ยกเลิก orders เดิมทั้งหมด"""
        self.client.cancel_all_orders(self.symbol)
        self.bid_order_id = None
        self.ask_order_id = None
    
    def place_market_making_orders(self):
        """วาง bid/ask orders"""
        # ดึงข้อมูลตลาด
        mid_price = self.client.get_mid_price(self.symbol)
        if not mid_price:
            print("❌ Cannot get mid price")
            return
        
        position = self.get_current_position()
        print(f"\n📊 Mid Price: ${mid_price:.2f} | Position: {position:.4f}")
        
        # คำนวณราคา
        bid_price, ask_price = self.calculate_order_prices(mid_price, position)
        
        # ตรวจสอบ position limit
        can_buy = abs(position + self.order_size) <= self.max_position
        can_sell = abs(position - self.order_size) <= self.max_position
        
        # วาง bid order
        if can_buy:
            print(f"🟢 Placing BID: {self.order_size} @ ${bid_price:.2f}")
            self.client.place_order(
                symbol=self.symbol,
                is_buy=True,
                price=bid_price,
                size=self.order_size
            )
        else:
            print(f"⚠️  Skip BID: Position limit reached")
        
        # วาง ask order
        if can_sell:
            print(f"🔴 Placing ASK: {self.order_size} @ ${ask_price:.2f}")
            self.client.place_order(
                symbol=self.symbol,
                is_buy=False,
                price=ask_price,
                size=self.order_size
            )
        else:
            print(f"⚠️  Skip ASK: Position limit reached")
    
    def run(self):
        """เริ่มรัน market making strategy"""
        print(f"\n🚀 Starting Market Maker for {self.symbol}")
        print(f"📈 Spread: {self.spread_pct*100:.2f}%")
        print(f"💰 Order Size: {self.order_size}")
        print(f"⚖️  Max Position: ±{self.max_position}")
        
        try:
            while True:
                # ยกเลิก orders เก่า
                self.cancel_existing_orders()
                
                # วาง orders ใหม่
                self.place_market_making_orders()
                
                # รอจนกว่าจะถึงเวลา refresh
                print(f"\n⏳ Waiting {self.refresh_interval}s before refresh...")
                time.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping Market Maker...")
            self.cancel_existing_orders()
            print("✅ All orders cancelled. Goodbye!")

