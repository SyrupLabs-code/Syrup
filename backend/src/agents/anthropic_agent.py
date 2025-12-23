import json
from typing import Optional, AsyncIterator
from anthropic import AsyncAnthropic

from .base import BaseAgent
from ..models import TradeRequest, Platform, TradeType


class AnthropicAgent(BaseAgent):
    """Anthropic Claude-powered trading agent."""
    
    def _initialize(self) -> None:
        """Initialize Anthropic client."""
        api_key = self.config.api_key
        if not api_key:
            raise ValueError("Anthropic API key is required")
        
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = self.config.model
    
    async def analyze_market(
        self,
        market_data: dict,
        context: str = ""
    ) -> dict:
        """Analyze market using Anthropic Claude."""
        try:
            system_prompt = self._build_system_prompt()
            market_context = self._build_trade_context(market_data)
            
            user_message = f"{market_context}\n\n{context}\n\nProvide market analysis and insights."
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )
            
            analysis = response.content[0].text if response.content else ""
            
            return {
                "analysis": analysis,
                "model": self.model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def generate_trade_decision(
        self,
        market_data: dict,
        portfolio: dict,
        context: str = ""
    ) -> Optional[TradeRequest]:
        """Generate trade decision using Anthropic Claude."""
        try:
            system_prompt = self._build_system_prompt()
            system_prompt += """

If you decide to execute a trade, respond with a JSON object in this format:
{
  "action": "trade",
  "platform": "solana|polymarket|kalshi",
  "trade_type": "buy|sell|swap",
  "symbol": "symbol/market identifier",
  "amount": 0.0,
  "price": 0.0 (optional),
  "slippage": 0.01,
  "reasoning": "your reasoning"
}

If you decide not to trade, respond with:
{
  "action": "hold",
  "reasoning": "your reasoning"
}
"""
            
            market_context = self._build_trade_context(market_data, portfolio)
            user_message = f"{market_context}\n\n{context}\n\nShould we execute a trade?"
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3
            )
            
            content = response.content[0].text if response.content else ""
            
            # Extract JSON from response
            try:
                # Find JSON in response
                start = content.find('{')
                end = content.rfind('}') + 1
                
                if start >= 0 and end > start:
                    json_str = content[start:end]
                    decision = json.loads(json_str)
                    
                    if decision.get("action") == "trade":
                        return TradeRequest(
                            platform=Platform(decision["platform"]),
                            trade_type=TradeType(decision["trade_type"]),
                            symbol=decision["symbol"],
                            amount=decision["amount"],
                            price=decision.get("price"),
                            slippage=decision.get("slippage", 0.01),
                            metadata={"reasoning": decision.get("reasoning", "")}
                        )
            except json.JSONDecodeError:
                pass
            
            return None
            
        except Exception as e:
            print(f"Error generating trade decision: {e}")
            return None
    
    async def stream_analysis(
        self,
        market_data: dict,
        context: str = ""
    ) -> AsyncIterator[str]:
        """Stream analysis in real-time."""
        try:
            system_prompt = self._build_system_prompt()
            market_context = self._build_trade_context(market_data)
            
            user_message = f"{market_context}\n\n{context}\n\nProvide detailed market analysis."
            
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            yield f"Error: {str(e)}"

