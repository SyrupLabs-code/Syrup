import json
from typing import Optional, AsyncIterator
from openai import AsyncOpenAI

from .base import BaseAgent
from ..models import TradeRequest, Platform, TradeType


class OpenAIAgent(BaseAgent):
    """OpenAI-powered trading agent."""
    
    def _initialize(self) -> None:
        """Initialize OpenAI client."""
        api_key = self.config.api_key
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = self.config.model
    
    async def analyze_market(
        self,
        market_data: dict,
        context: str = ""
    ) -> dict:
        """Analyze market using OpenAI."""
        try:
            system_prompt = self._build_system_prompt()
            market_context = self._build_trade_context(market_data)
            
            user_message = f"{market_context}\n\n{context}\n\nProvide market analysis and insights."
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "analysis": analysis,
                "model": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def generate_trade_decision(
        self,
        market_data: dict,
        portfolio: dict,
        context: str = ""
    ) -> Optional[TradeRequest]:
        """Generate trade decision using OpenAI with function calling."""
        try:
            system_prompt = self._build_system_prompt()
            market_context = self._build_trade_context(market_data, portfolio)
            
            user_message = f"{market_context}\n\n{context}\n\nShould we execute a trade? If yes, provide trade details."
            
            # Define trade function schema
            trade_function = {
                "name": "execute_trade",
                "description": "Execute a trade on a supported platform",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "enum": [p.value for p in self.config.platforms],
                            "description": "Trading platform"
                        },
                        "trade_type": {
                            "type": "string",
                            "enum": ["buy", "sell", "swap"],
                            "description": "Type of trade"
                        },
                        "symbol": {
                            "type": "string",
                            "description": "Trading symbol or market identifier"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Amount to trade"
                        },
                        "price": {
                            "type": "number",
                            "description": "Limit price (optional for market orders)"
                        },
                        "slippage": {
                            "type": "number",
                            "description": "Acceptable slippage (0-1)"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Reasoning for this trade"
                        }
                    },
                    "required": ["platform", "trade_type", "symbol", "amount"]
                }
            }
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                functions=[trade_function],
                function_call="auto",
                temperature=0.3
            )
            
            message = response.choices[0].message
            
            # Check if agent wants to execute a trade
            if message.function_call:
                args = json.loads(message.function_call.arguments)
                
                return TradeRequest(
                    platform=Platform(args["platform"]),
                    trade_type=TradeType(args["trade_type"]),
                    symbol=args["symbol"],
                    amount=args["amount"],
                    price=args.get("price"),
                    slippage=args.get("slippage", 0.01),
                    metadata={"reasoning": args.get("reasoning", "")}
                )
            
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
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                stream=True,
                temperature=0.7
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"Error: {str(e)}"

