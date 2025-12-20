import asyncio
import hmac
import hashlib
import time
from typing import Optional
from datetime import datetime
import aiohttp

from .base import BasePlatform
from ..models import TradeRequest, TradeResult, TradeStatus, Platform


class PolymarketAdapter(BasePlatform):
    """Polymarket prediction market adapter."""
    
    BASE_URL = "https://api.polymarket.com"
    
    def _initialize(self) -> None:
        """Initialize Polymarket connection."""
        self.api_key = self.credentials.api_key
        self.secret = self.credentials.secret
        self.passphrase = self.credentials.passphrase
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    def _generate_signature(
        self,
        timestamp: str,
        method: str,
        path: str,
        body: str = ""
    ) -> str:
        """Generate HMAC signature for Polymarket API."""
        message = timestamp + method + path + body
        signature = hmac.new(
            self.secret.encode() if self.secret else b"",
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None
    ) -> dict:
        """Make authenticated API request."""
        session = await self._get_session()
        url = f"{self.BASE_URL}{endpoint}"
        
        timestamp = str(int(time.time()))
        body = ""
        if data:
            import json
            body = json.dumps(data)
        
        signature = self._generate_signature(timestamp, method, endpoint, body)
        
        headers = {
            "POLY-API-KEY": self.api_key or "",
            "POLY-SIGNATURE": signature,
            "POLY-TIMESTAMP": timestamp,
            "POLY-PASSPHRASE": self.passphrase or "",
            "Content-Type": "application/json"
        }
        
        async with session.request(method, url, headers=headers, json=data) as response:
            return await response.json()
    
    async def execute_trade(self, trade: TradeRequest) -> TradeResult:
        """Execute trade on Polymarket."""
        try:
            # Validate trade
            is_valid, error = await self.validate_trade(trade)
            if not is_valid:
                return TradeResult(
                    trade_id="",
                    platform=Platform.POLYMARKET,
                    status=TradeStatus.FAILED,
                    timestamp=datetime.utcnow(),
                    error=error
                )
            
            # Create order
            order_data = {
                "market": trade.symbol,
                "side": "BUY" if trade.trade_type.value == "buy" else "SELL",
                "size": trade.amount,
                "price": trade.price,
                "type": "LIMIT" if trade.price else "MARKET"
            }
            
            response = await self._make_request("POST", "/orders", order_data)
            
            if response.get("success"):
                return TradeResult(
                    trade_id=response.get("orderId", ""),
                    platform=Platform.POLYMARKET,
                    status=TradeStatus.COMPLETED,
                    transaction_hash=response.get("transactionHash"),
                    executed_amount=trade.amount,
                    executed_price=response.get("executedPrice"),
                    fee=response.get("fee", 0),
                    timestamp=datetime.utcnow()
                )
            
            return TradeResult(
                trade_id="",
                platform=Platform.POLYMARKET,
                status=TradeStatus.FAILED,
                timestamp=datetime.utcnow(),
                error=response.get("error", "Unknown error")
            )
            
        except Exception as e:
            return TradeResult(
                trade_id="",
                platform=Platform.POLYMARKET,
                status=TradeStatus.FAILED,
                timestamp=datetime.utcnow(),
                error=str(e)
            )
    
    async def get_balance(self, token: Optional[str] = None) -> dict[str, float]:
        """Get account balances."""
        try:
            response = await self._make_request("GET", "/balances")
            
            if response.get("success"):
                balances = response.get("balances", {})
                return balances
            
            return {}
        except Exception:
            return {}
    
    async def get_price(self, symbol: str) -> float:
        """Get current market price."""
        try:
            response = await self._make_request("GET", f"/markets/{symbol}")
            
            if response.get("success"):
                return float(response.get("lastPrice", 0))
            
            return 0.0
        except Exception:
            return 0.0
    
    async def get_order_status(self, order_id: str) -> dict:
        """Get order status."""
        try:
            response = await self._make_request("GET", f"/orders/{order_id}")
            return response
        except Exception as e:
            return {"error": str(e)}
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        try:
            response = await self._make_request("DELETE", f"/orders/{order_id}")
            return response.get("success", False)
        except Exception:
            return False
    
    async def close(self):
        """Close session."""
        if self.session and not self.session.closed:
            await self.session.close()

