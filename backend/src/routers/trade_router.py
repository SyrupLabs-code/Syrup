from typing import Optional
from ..models import TradeRequest, TradeResult, PlatformCredentials, Platform
from ..platforms import get_platform_adapter, BasePlatform


class TradeRouter:
    """Route trades to appropriate platforms."""
    
    def __init__(self):
        self.platforms: dict[Platform, BasePlatform] = {}
    
    def register_platform(self, credentials: PlatformCredentials) -> None:
        """Register a platform with credentials."""
        adapter = get_platform_adapter(credentials)
        self.platforms[credentials.platform] = adapter
    
    def unregister_platform(self, platform: Platform) -> None:
        """Unregister a platform."""
        if platform in self.platforms:
            del self.platforms[platform]
    
    async def execute_trade(self, trade: TradeRequest) -> TradeResult:
        """Route and execute a trade."""
        platform = self.platforms.get(trade.platform)
        
        if not platform:
            from datetime import datetime
            from ..models import TradeStatus
            
            return TradeResult(
                trade_id="",
                platform=trade.platform,
                status=TradeStatus.FAILED,
                timestamp=datetime.utcnow(),
                error=f"Platform {trade.platform.value} not registered"
            )
        
        return await platform.execute_trade(trade)
    
    async def get_balance(
        self,
        platform: Platform,
        token: Optional[str] = None
    ) -> dict[str, float]:
        """Get balance from a platform."""
        adapter = self.platforms.get(platform)
        if not adapter:
            return {}
        
        return await adapter.get_balance(token)
    
    async def get_price(self, platform: Platform, symbol: str) -> float:
        """Get price from a platform."""
        adapter = self.platforms.get(platform)
        if not adapter:
            return 0.0
        
        return await adapter.get_price(symbol)
    
    async def get_all_balances(self) -> dict[Platform, dict[str, float]]:
        """Get balances from all registered platforms."""
        balances = {}
        
        for platform, adapter in self.platforms.items():
            try:
                balances[platform] = await adapter.get_balance()
            except Exception:
                balances[platform] = {}
        
        return balances
    
    async def close_all(self) -> None:
        """Close all platform connections."""
        for adapter in self.platforms.values():
            if hasattr(adapter, 'close'):
                await adapter.close()

