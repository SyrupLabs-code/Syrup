from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class Platform(str, Enum):
    """Supported trading platforms."""
    SOLANA = "solana"
    POLYMARKET = "polymarket"
    KALSHI = "kalshi"


class TradeType(str, Enum):
    """Trade operation types."""
    BUY = "buy"
    SELL = "sell"
    SWAP = "swap"


class TradeStatus(str, Enum):
    """Trade execution status."""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TradeRequest(BaseModel):
    """Trade request from agent."""
    platform: Platform
    trade_type: TradeType
    symbol: str
    amount: float
    price: Optional[float] = None
    slippage: float = Field(default=0.01, ge=0, le=1)
    metadata: dict = Field(default_factory=dict)


class TradeResult(BaseModel):
    """Result of a trade execution."""
    trade_id: str
    platform: Platform
    status: TradeStatus
    transaction_hash: Optional[str] = None
    executed_amount: Optional[float] = None
    executed_price: Optional[float] = None
    fee: Optional[float] = None
    timestamp: datetime
    error: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class AgentConfig(BaseModel):
    """Configuration for trading agent."""
    name: str
    agent_type: Literal["openai", "anthropic", "custom"]
    api_key: Optional[str] = None
    model: str = "gpt-4-turbo-preview"
    system_prompt: str = "You are a trading agent."
    max_position_size: float = 1000.0
    risk_limit: float = 0.1
    platforms: list[Platform] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class PlatformCredentials(BaseModel):
    """Credentials for a specific platform."""
    platform: Platform
    rpc_url: Optional[str] = None
    api_key: Optional[str] = None
    secret: Optional[str] = None
    private_key: Optional[str] = None
    passphrase: Optional[str] = None
    wallet_address: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

