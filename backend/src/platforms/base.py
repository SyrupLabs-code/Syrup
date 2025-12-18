from abc import ABC, abstractmethod
from typing import Optional
from ..models import TradeRequest, TradeResult, PlatformCredentials


class BasePlatform(ABC):
    """Base class for trading platform adapters."""
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self._initialize()
    
    @abstractmethod
    def _initialize(self) -> None:
        """Initialize platform-specific connections."""
        pass
    
    @abstractmethod
    async def execute_trade(self, trade: TradeRequest) -> TradeResult:
        """Execute a trade on the platform."""
        pass
    
    @abstractmethod
    async def get_balance(self, token: Optional[str] = None) -> dict[str, float]:
        """Get account balance(s)."""
        pass
    
    @abstractmethod
    async def get_price(self, symbol: str) -> float:
        """Get current price for a symbol."""
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> dict:
        """Get status of an order."""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order."""
        pass
    
    async def validate_trade(self, trade: TradeRequest) -> tuple[bool, Optional[str]]:
        """Validate trade parameters before execution."""
        try:
            # Check balance
            balances = await self.get_balance()
            
            # Basic validation
            if trade.amount <= 0:
                return False, "Amount must be positive"
            
            if trade.slippage < 0 or trade.slippage > 1:
                return False, "Slippage must be between 0 and 1"
            
            return True, None
        except Exception as e:
            return False, f"Validation error: {str(e)}"

