from typing import Dict, Optional

class RiskManager:
    """Risk management utilities"""
    
    def __init__(
        self,
        max_position_value: float = 1000.0,  # USD
        max_drawdown_pct: float = 0.10,      # 10%
        initial_balance: Optional[float] = None
    ):
        """
        Initialize risk manager
        
        Args:
            max_position_value: Maximum position value in USD
            max_drawdown_pct: Maximum drawdown percentage (0.10 = 10%)
            initial_balance: Initial balance for drawdown calculation
        """
        self.max_position_value = max_position_value
        self.max_drawdown_pct = max_drawdown_pct
        self.initial_balance = initial_balance
        self.peak_balance = initial_balance
        
    def update_balance(self, current_balance: float):
        """Update peak balance for drawdown calculation"""
        if self.peak_balance is None:
            self.peak_balance = current_balance
            self.initial_balance = current_balance
        elif current_balance > self.peak_balance:
            self.peak_balance = current_balance
    
    def check_drawdown(self, current_balance: float) -> bool:
        """
        Check if drawdown limit is exceeded
        
        Returns:
            True if trading should continue, False if should stop
        """
        if self.peak_balance is None:
            return True
        
        drawdown = (self.peak_balance - current_balance) / self.peak_balance
        
        if drawdown >= self.max_drawdown_pct:
            print(f"🚨 RISK ALERT: Max drawdown exceeded! {drawdown*100:.2f}%")
            return False
        
        return True
    
    def check_position_size(
        self,
        position_value: float,
        current_balance: float
    ) -> bool:
        """
        Check if position size is within limits
        
        Args:
            position_value: Value of position in USD
            current_balance: Current account balance
        
        Returns:
            True if position is acceptable, False otherwise
        """
        # Check absolute position value
        if abs(position_value) > self.max_position_value:
            print(f"⚠️  Position value ${position_value:.2f} exceeds limit ${self.max_position_value:.2f}")
            return False
        
        # Check position as percentage of balance
        if current_balance > 0:
            position_pct = abs(position_value) / current_balance
            if position_pct > 0.5:  # 50% max
                print(f"⚠️  Position is {position_pct*100:.1f}% of balance (max 50%)")
                return False
        
        return True
    
    def calculate_order_size(
        self,
        price: float,
        current_balance: float,
        base_size: float
    ) -> float:
        """
        Calculate safe order size based on risk limits
        
        Args:
            price: Current market price
            current_balance: Current account balance
            base_size: Desired order size
        
        Returns:
            Adjusted order size
        """
        # Maximum order value (10% of balance or max position value, whichever is smaller)
        max_order_value = min(
            current_balance * 0.1,
            self.max_position_value * 0.2
        )
        
        max_size = max_order_value / price
        
        # Return smaller of base_size or max_size
        return min(base_size, max_size)

