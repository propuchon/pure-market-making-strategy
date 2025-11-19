from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from eth_account import Account
import os
from typing import Optional, Dict, List

class HyperliquidClient:
    """Client สำหรับเชื่อมต่อ Hyperliquid Exchange"""
    
    def __init__(self, private_key: str, testnet: bool = True):
        """
        Initialize Hyperliquid client
        
        Args:
            private_key: Private key ของ wallet
            testnet: ใช้ testnet หรือไม่ (default: True)
        """
        self.testnet = testnet
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        
        # เลือก base URL ตาม testnet/mainnet
        base_url = "https://api.hyperliquid-testnet.xyz" if testnet else None
        
        # สร้าง Info client (สำหรับ read data)
        self.info = Info(base_url=base_url, skip_ws=True)
        
        # สร้าง Exchange client (สำหรับ place orders)
        self.exchange = Exchange(
            self.account,
            base_url=base_url,
            account_address=self.address
        )
        
        print(f"✅ Connected to Hyperliquid {'Testnet' if testnet else 'Mainnet'}")
        print(f"📍 Address: {self.address}")
    
    def get_balance(self) -> Dict:
        """ดึงยอด balance ของ account"""
        try:
            state = self.info.user_state(self.address)
            return {
                'total_value': float(state['marginSummary']['accountValue']),
                'withdrawable': float(state['withdrawable']),
                'positions': state.get('assetPositions', [])
            }
        except Exception as e:
            print(f"❌ Error getting balance: {e}")
            return {}
    
    def get_orderbook(self, symbol: str) -> Dict:
        """
        ดึง orderbook ของ symbol
        
        Args:
            symbol: เช่น "ETH", "BTC"
        """
        try:
            l2_data = self.info.l2_snapshot(symbol)
            return {
                'bids': l2_data['levels'][0],  # [[price, size], ...]
                'asks': l2_data['levels'][1],
                'timestamp': l2_data['time']
            }
        except Exception as e:
            print(f"❌ Error getting orderbook: {e}")
            return {'bids': [], 'asks': []}
    
    def get_mid_price(self, symbol: str) -> Optional[float]:
        """คำนวณ mid price จาก orderbook"""
        orderbook = self.get_orderbook(symbol)
        if not orderbook['bids'] or not orderbook['asks']:
            return None
        
        best_bid = float(orderbook['bids'][0][0])
        best_ask = float(orderbook['asks'][0][0])
        return (best_bid + best_ask) / 2
    
    def place_order(
        self,
        symbol: str,
        is_buy: bool,
        price: float,
        size: float,
        reduce_only: bool = False
    ) -> Optional[Dict]:
        """
        วาง limit order
        
        Args:
            symbol: เช่น "ETH"
            is_buy: True = buy, False = sell
            price: ราคา limit
            size: ขนาด order
            reduce_only: reduce position only (default: False)
        """
        try:
            order = {
                "coin": symbol,
                "is_buy": is_buy,
                "sz": size,
                "limit_px": price,
                "order_type": {"limit": {"tif": "Gtc"}},  # Good-til-cancel
                "reduce_only": reduce_only
            }
            
            result = self.exchange.order(order, asset=0)
            print(f"✅ Order placed: {result}")
            return result
        except Exception as e:
            print(f"❌ Error placing order: {e}")
            return None
    
    def cancel_order(self, symbol: str, order_id: int) -> bool:
        """ยกเลิก order"""
        try:
            result = self.exchange.cancel(symbol, order_id)
            print(f"✅ Order cancelled: {result}")
            return True
        except Exception as e:
            print(f"❌ Error cancelling order: {e}")
            return False
    
    def cancel_all_orders(self, symbol: str) -> bool:
        """ยกเลิก orders ทั้งหมดของ symbol"""
        try:
            result = self.exchange.cancel_all_orders(symbol)
            print(f"✅ All orders cancelled for {symbol}")
            return True
        except Exception as e:
            print(f"❌ Error cancelling all orders: {e}")
            return False
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """ดึง open orders ทั้งหมด"""
        try:
            orders = self.info.open_orders(self.address)
            if symbol:
                orders = [o for o in orders if o['coin'] == symbol]
            return orders
        except Exception as e:
            print(f"❌ Error getting open orders: {e}")
            return []

