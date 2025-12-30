"""
Agent-based trading example.

This script demonstrates how to:
1. Create a trading agent
2. Analyze market data
3. Generate trade decisions
4. Execute trades based on agent decisions
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from src.models import (
    Platform,
    AgentConfig,
    PlatformCredentials,
)
from src.agents import get_agent
from src.routers import TradeRouter


async def main():
    # Setup trading platform
    router = TradeRouter()
    
    solana_creds = PlatformCredentials(
        platform=Platform.SOLANA,
        rpc_url="https://api.devnet.solana.com",
        private_key=os.getenv("SOLANA_PRIVATE_KEY", "your_key_here")
    )
    
    router.register_platform(solana_creds)
    print("✓ Platform registered")
    
    # Create trading agent
    agent_config = AgentConfig(
        name="momentum-trader",
        agent_type="openai",
        api_key=os.getenv("OPENAI_API_KEY", "your_key_here"),
        model="gpt-4-turbo-preview",
        system_prompt="""You are a momentum trading agent. 
        Analyze market data and make trading decisions based on price momentum and volume.
        Always consider risk management and position sizing.""",
        max_position_size=100.0,
        risk_limit=0.05,
        platforms=[Platform.SOLANA]
    )
    
    agent = get_agent(agent_config)
    print(f"✓ Agent created: {agent_config.name}")
    
    # Market data to analyze
    market_data = {
        "symbol": "SOL/USDC",
        "price": 102.50,
        "price_24h_ago": 98.00,
        "volume_24h": 5000000,
        "high_24h": 103.00,
        "low_24h": 97.50,
        "trend": "bullish"
    }
    
    # Get portfolio data
    portfolio = await router.get_balance(Platform.SOLANA)
    
    print(f"\n--- Market Analysis ---")
    print(f"Symbol: {market_data['symbol']}")
    print(f"Current Price: ${market_data['price']}")
    print(f"24h Change: +{((market_data['price'] / market_data['price_24h_ago']) - 1) * 100:.2f}%")
    
    # Get agent's market analysis
    print(f"\n--- Agent Analysis ---")
    analysis = await agent.analyze_market(market_data)
    
    if "analysis" in analysis:
        print(analysis["analysis"])
        print(f"\nTokens used: {analysis.get('tokens_used', 'N/A')}")
    
    # Generate trade decision
    print(f"\n--- Trade Decision ---")
    trade_decision = await agent.generate_trade_decision(
        market_data,
        portfolio,
        context="Strong upward momentum with high volume. Consider entry position."
    )
    
    if trade_decision:
        print(f"Decision: TRADE")
        print(f"  Platform: {trade_decision.platform.value}")
        print(f"  Type: {trade_decision.trade_type.value}")
        print(f"  Symbol: {trade_decision.symbol}")
        print(f"  Amount: {trade_decision.amount}")
        print(f"  Slippage: {trade_decision.slippage * 100}%")
        
        if trade_decision.metadata.get("reasoning"):
            print(f"\nReasoning: {trade_decision.metadata['reasoning']}")
        
        # Ask for confirmation
        response = input("\nExecute this trade? (yes/no): ")
        
        if response.lower() == 'yes':
            result = await router.execute_trade(trade_decision)
            
            print(f"\n--- Execution Result ---")
            print(f"Status: {result.status.value}")
            
            if result.transaction_hash:
                print(f"TX: {result.transaction_hash}")
            
            if result.error:
                print(f"Error: {result.error}")
        else:
            print("Trade cancelled by user")
    else:
        print("Decision: HOLD")
        print("Agent decided not to trade at this time")
    
    # Cleanup
    await router.close_all()


if __name__ == "__main__":
    asyncio.run(main())

