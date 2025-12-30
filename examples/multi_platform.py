"""
Multi-platform trading example.

This script demonstrates how to:
1. Register multiple platforms
2. Get balances across all platforms
3. Execute trades on different platforms
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from src.models import Platform, TradeType, TradeRequest, PlatformCredentials
from src.routers import TradeRouter


async def main():
    router = TradeRouter()
    
    # Register Solana
    print("Registering platforms...")
    
    if os.getenv("SOLANA_PRIVATE_KEY"):
        solana_creds = PlatformCredentials(
            platform=Platform.SOLANA,
            rpc_url="https://api.devnet.solana.com",
            private_key=os.getenv("SOLANA_PRIVATE_KEY")
        )
        router.register_platform(solana_creds)
        print("✓ Solana registered")
    
    # Register Polymarket
    if os.getenv("POLYMARKET_API_KEY"):
        polymarket_creds = PlatformCredentials(
            platform=Platform.POLYMARKET,
            api_key=os.getenv("POLYMARKET_API_KEY"),
            secret=os.getenv("POLYMARKET_SECRET"),
            passphrase=os.getenv("POLYMARKET_PASSPHRASE")
        )
        router.register_platform(polymarket_creds)
        print("✓ Polymarket registered")
    
    # Register Kalshi
    if os.getenv("KALSHI_API_KEY"):
        kalshi_creds = PlatformCredentials(
            platform=Platform.KALSHI,
            api_key=os.getenv("KALSHI_API_KEY"),
            private_key=os.getenv("KALSHI_PRIVATE_KEY")
        )
        router.register_platform(kalshi_creds)
        print("✓ Kalshi registered")
    
    # Get all balances
    print("\n--- Platform Balances ---")
    all_balances = await router.get_all_balances()
    
    for platform, balances in all_balances.items():
        print(f"\n{platform.value.upper()}:")
        if balances:
            for token, amount in balances.items():
                print(f"  {token}: {amount:.6f}")
        else:
            print("  No balances or connection failed")
    
    # Example: Execute trade on Solana
    if Platform.SOLANA in router.platforms:
        print("\n--- Executing Solana Trade ---")
        
        solana_trade = TradeRequest(
            platform=Platform.SOLANA,
            trade_type=TradeType.SWAP,
            symbol="SOL/USDC",
            amount=0.1,
            slippage=0.01
        )
        
        result = await router.execute_trade(solana_trade)
        print(f"Status: {result.status.value}")
        
        if result.error:
            print(f"Error: {result.error}")
    
    # Example: Execute trade on Polymarket
    if Platform.POLYMARKET in router.platforms:
        print("\n--- Executing Polymarket Trade ---")
        
        polymarket_trade = TradeRequest(
            platform=Platform.POLYMARKET,
            trade_type=TradeType.BUY,
            symbol="MARKET_ID_HERE",
            amount=10,
            price=0.60
        )
        
        result = await router.execute_trade(polymarket_trade)
        print(f"Status: {result.status.value}")
        
        if result.error:
            print(f"Error: {result.error}")
    
    # Example: Execute trade on Kalshi
    if Platform.KALSHI in router.platforms:
        print("\n--- Executing Kalshi Trade ---")
        
        kalshi_trade = TradeRequest(
            platform=Platform.KALSHI,
            trade_type=TradeType.BUY,
            symbol="TICKER_HERE",
            amount=5,
            price=0.55
        )
        
        result = await router.execute_trade(kalshi_trade)
        print(f"Status: {result.status.value}")
        
        if result.error:
            print(f"Error: {result.error}")
    
    # Cleanup
    await router.close_all()
    print("\n✓ All connections closed")


if __name__ == "__main__":
    asyncio.run(main())

