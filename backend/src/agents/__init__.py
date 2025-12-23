from .base import BaseAgent
from .openai_agent import OpenAIAgent
from .anthropic_agent import AnthropicAgent
from ..models import AgentConfig


def get_agent(config: AgentConfig) -> BaseAgent:
    """Factory function to get appropriate agent."""
    agents = {
        "openai": OpenAIAgent,
        "anthropic": AnthropicAgent,
    }
    
    agent_class = agents.get(config.agent_type)
    if not agent_class:
        raise ValueError(f"Unsupported agent type: {config.agent_type}")
    
    return agent_class(config)


__all__ = [
    "BaseAgent",
    "OpenAIAgent",
    "AnthropicAgent",
    "get_agent",
]

