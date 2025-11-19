"""
Unit tests for market making strategy
"""

import pytest
from src.strategy.market_maker import PureMarketMaker
from src.utils.risk_manager import RiskManager


class TestMarketMaker:
    """Tests for PureMarketMaker"""
    
    def test_calculate_order_prices_no_position(self):
        """Test price calculation with no position"""
        # Mock client (simplified for testing)
        class MockClient:
            pass
        
        client = MockClient()
        mm = PureMarketMaker(
            client=client,
            symbol="ETH",
            spread_pct=0.002,  # 0.2%
            order_size=0.01,
            max_position=0.05
        )
        
        mid_price = 2000.0
        position = 0.0
        
        bid_price, ask_price = mm.calculate_order_prices(mid_price, position)
        
        # With 0.2% spread, bid/ask should be ~$4 apart
        spread = ask_price - bid_price
        expected_spread = mid_price * 0.002 * 2
        
        assert bid_price < mid_price
        assert ask_price > mid_price
        assert abs(spread - expected_spread) < 0.1
    
    def test_calculate_order_prices_with_position(self):
        """Test price calculation with existing position"""
        class MockClient:
            pass
        
        client = MockClient()
        mm = PureMarketMaker(
            client=client,
            symbol="ETH",
            spread_pct=0.002,
            order_size=0.01,
            max_position=0.05
        )
        
        mid_price = 2000.0
        position = 0.03  # 60% of max (long)
        
        bid_price_no_pos, ask_price_no_pos = mm.calculate_order_prices(mid_price, 0.0)
        bid_price_with_pos, ask_price_with_pos = mm.calculate_order_prices(mid_price, position)
        
        # With long position, both prices should be lower (encourage selling)
        assert bid_price_with_pos < bid_price_no_pos
        assert ask_price_with_pos < ask_price_no_pos


class TestRiskManager:
    """Tests for RiskManager"""
    
    def test_check_drawdown_ok(self):
        """Test drawdown check when within limits"""
        rm = RiskManager(max_drawdown_pct=0.10, initial_balance=1000.0)
        
        # 5% drawdown - should be OK
        assert rm.check_drawdown(950.0) is True
    
    def test_check_drawdown_exceeded(self):
        """Test drawdown check when limit exceeded"""
        rm = RiskManager(max_drawdown_pct=0.10, initial_balance=1000.0)
        
        # 15% drawdown - should fail
        assert rm.check_drawdown(850.0) is False
    
    def test_check_position_size_ok(self):
        """Test position size check when within limits"""
        rm = RiskManager(max_position_value=1000.0)
        
        # Position value $500 - OK
        assert rm.check_position_size(500.0, 2000.0) is True
    
    def test_check_position_size_exceeded(self):
        """Test position size check when limit exceeded"""
        rm = RiskManager(max_position_value=1000.0)
        
        # Position value $1500 - exceeds limit
        assert rm.check_position_size(1500.0, 2000.0) is False
    
    def test_calculate_order_size(self):
        """Test order size calculation"""
        rm = RiskManager(max_position_value=1000.0)
        
        price = 2000.0
        current_balance = 5000.0
        base_size = 1.0
        
        # Should limit order size based on risk
        adjusted_size = rm.calculate_order_size(price, current_balance, base_size)
        
        assert adjusted_size <= base_size
        assert adjusted_size * price <= current_balance * 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

