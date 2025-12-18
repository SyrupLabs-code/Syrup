from .base import BasePlatform
from .solana_adapter import SolanaAdapter
from .polymarket_adapter import PolymarketAdapter
from .kalshi_adapter import KalshiAdapter
from ..models import Platform, PlatformCredentials


def get_platform_adapter(credentials: PlatformCredentials) -> BasePlatform:
    """Factory function to get appropriate platform adapter."""
    adapters = {
        Platform.SOLANA: SolanaAdapter,
        Platform.POLYMARKET: PolymarketAdapter,
        Platform.KALSHI: KalshiAdapter,
    }
    
    adapter_class = adapters.get(credentials.platform)
    if not adapter_class:
        raise ValueError(f"Unsupported platform: {credentials.platform}")
    
    return adapter_class(credentials)


__all__ = [
    "BasePlatform",
    "SolanaAdapter",
    "PolymarketAdapter",
    "KalshiAdapter",
    "get_platform_adapter",
]

