import asyncio
from typing import Optional
from datetime import datetime
import aiohttp
import base64

from .base import BasePlatform
from ..models import TradeRequest, TradeResult, TradeStatus, Platform


class KalshiAdapter(BasePlatform):
    """Kalshi prediction market adapter."""
    
    BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
    
    def _initialize(self) -> None:
        """Initialize Kalshi connection."""
        self.api_key = self.credentials.api_key
        self.private_key = self.credentials.private_key
        self.session: Optional[aiohttp.ClientSession] = None
        self.token: Optional[str] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _authenticate(self) -> bool:
        """Authenticate with Kalshi API."""
        try:
            session = await self._get_session()
            
            auth_data = {
                "email": self.api_key,
                "password": self.private_key  # In production, use proper key management
            }
            
            async with session.post(
                f"{self.BASE_URL}/login",
                json=auth_data
            ) as response:
                data = await response.json()
                
                if data.get("token"):
                    self.token = data["token"]
                    return True
            
            return False
        except Exception:
            return False
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None
    ) -> dict:
        """Make authenticated API request."""
        if not self.token:
            await self._authenticate()
        
        session = await self._get_session()
        url = f"{self.BASE_URL}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        async with session.request(
            method,
            url,
            headers=headers,
            json=data
        ) as response:
            return await response.json()
    
    async def execute_trade(self, trade: TradeRequest) -> TradeResult:
        """Execute trade on Kalshi."""
        try:
            # Validate trade
            is_valid, error = await self.validate_trade(trade)
            if not is_valid:
                return TradeResult(
                    trade_id="",
                    platform=Platform.KALSHI,
                    status=TradeStatus.FAILED,
                    timestamp=datetime.utcnow(),
                    error=error
                )
            
            # Create order
            order_data = {
                "ticker": trade.symbol,
                "action": trade.trade_type.value.upper(),
                "count": int(trade.amount),
                "type": "market",
                "side": "yes"  # Can be customized via metadata
            }
            
            if trade.price:
                order_data["type"] = "limit"
                order_data["yes_price"] = int(trade.price * 100)  # Convert to cents
            
            response = await self._make_request("POST", "/portfolio/orders", order_data)
            
            if response.get("order"):
                order = response["order"]
                return TradeResult(
                    trade_id=order.get("order_id", ""),
                    platform=Platform.KALSHI,
                    status=TradeStatus.COMPLETED,
                    executed_amount=order.get("quantity", 0),
                    executed_price=order.get("yes_price", 0) / 100,
                    fee=order.get("fee", 0) / 100,
                    timestamp=datetime.utcnow()
                )
            
            return TradeResult(
                trade_id="",
                platform=Platform.KALSHI,
                status=TradeStatus.FAILED,
                timestamp=datetime.utcnow(),
                error=response.get("error", "Unknown error")
            )
            
        except Exception as e:
            return TradeResult(
                trade_id="",
                platform=Platform.KALSHI,
                status=TradeStatus.FAILED,
                timestamp=datetime.utcnow(),
                error=str(e)
            )
    
    async def get_balance(self, token: Optional[str] = None) -> dict[str, float]:
        """Get account balance."""
        try:
            response = await self._make_request("GET", "/portfolio/balance")
            
            if response.get("balance"):
                balance = response["balance"] / 100  # Convert cents to dollars
                return {"USD": balance}
            
            return {}
        except Exception:
            return {}
    
    async def get_price(self, symbol: str) -> float:
        """Get current market price."""
        try:
            response = await self._make_request("GET", f"/markets/{symbol}")
            
            if response.get("market"):
                market = response["market"]
                return market.get("last_price", 0) / 100
            
            return 0.0
        except Exception:
            return 0.0
    
    async def get_order_status(self, order_id: str) -> dict:
        """Get order status."""
        try:
            response = await self._make_request("GET", f"/portfolio/orders/{order_id}")
            return response
        except Exception as e:
            return {"error": str(e)}
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        try:
            response = await self._make_request("DELETE", f"/portfolio/orders/{order_id}")
            return response.get("order", {}).get("status") == "canceled"
        except Exception:
            return False
    
    async def close(self):
        """Close session."""
        if self.session and not self.session.closed:
            await self.session.close()

