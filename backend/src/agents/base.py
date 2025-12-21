from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator
from ..models import AgentConfig, TradeRequest


class BaseAgent(ABC):
    """Base class for AI trading agents."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self._initialize()
    
    @abstractmethod
    def _initialize(self) -> None:
        """Initialize agent-specific resources."""
        pass
    
    @abstractmethod
    async def analyze_market(
        self,
        market_data: dict,
        context: str = ""
    ) -> dict:
        """Analyze market data and return insights."""
        pass
    
    @abstractmethod
    async def generate_trade_decision(
        self,
        market_data: dict,
        portfolio: dict,
        context: str = ""
    ) -> Optional[TradeRequest]:
        """Generate a trade decision based on market data and portfolio."""
        pass
    
    @abstractmethod
    async def stream_analysis(
        self,
        market_data: dict,
        context: str = ""
    ) -> AsyncIterator[str]:
        """Stream analysis in real-time."""
        pass
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with trading guidelines."""
        base_prompt = self.config.system_prompt
        
        guidelines = """

Trading Guidelines:
- Always consider risk management and position sizing
- Analyze market conditions before making decisions
- Consider slippage and fees in trade calculations
- Never exceed maximum position size or risk limits
- Provide clear reasoning for each trade decision

Available Platforms: """ + ", ".join(p.value for p in self.config.platforms)
        
        return base_prompt + guidelines
    
    def _build_trade_context(
        self,
        market_data: dict,
        portfolio: Optional[dict] = None
    ) -> str:
        """Build context string for the agent."""
        context_parts = ["Market Data:"]
        
        for key, value in market_data.items():
            context_parts.append(f"- {key}: {value}")
        
        if portfolio:
            context_parts.append("\nPortfolio:")
            for key, value in portfolio.items():
                context_parts.append(f"- {key}: {value}")
        
        context_parts.append(f"\nMax Position Size: {self.config.max_position_size}")
        context_parts.append(f"Risk Limit: {self.config.risk_limit * 100}%")
        
        return "\n".join(context_parts)

