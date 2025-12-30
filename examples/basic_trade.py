"""
Basic trade execution example.

This script demonstrates how to:
1. Register a platform
2. Execute a simple trade
3. Check trade status
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from src.models import Platform, TradeType, TradeRequest, PlatformCredentials
from src.routers import TradeRouter


async def main():
    # Initialize router
    router = TradeRouter()
    
    # Register Solana platform
    solana_creds = PlatformCredentials(
        platform=Platform.SOLANA,
        rpc_url="https://api.devnet.solana.com",  # Use devnet for testing
        private_key=os.getenv("SOLANA_PRIVATE_KEY", "your_key_here")
    )
    
    router.register_platform(solana_creds)
    print("✓ Platform registered")
    
    # Create a trade request
    trade = TradeRequest(
        platform=Platform.SOLANA,
        trade_type=TradeType.SWAP,
        symbol="SOL/USDC",
        amount=0.1,
        slippage=0.01
    )
    
    print(f"\nExecuting trade:")
    print(f"  Platform: {trade.platform.value}")
    print(f"  Type: {trade.trade_type.value}")
    print(f"  Symbol: {trade.symbol}")
    print(f"  Amount: {trade.amount}")
    
    # Execute trade
    result = await router.execute_trade(trade)
    
    print(f"\nResult:")
    print(f"  Status: {result.status.value}")
    print(f"  Trade ID: {result.trade_id}")
    
    if result.transaction_hash:
        print(f"  TX Hash: {result.transaction_hash}")
    
    if result.error:
        print(f"  Error: {result.error}")
    
    # Get balance
    balances = await router.get_balance(Platform.SOLANA)
    print(f"\nBalances:")
    for token, amount in balances.items():
        print(f"  {token}: {amount}")
    
    # Cleanup
    await router.close_all()


if __name__ == "__main__":
    asyncio.run(main())

