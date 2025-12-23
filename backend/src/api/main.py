from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional
import uvicorn

from ..config import settings
from ..models import (
    TradeRequest,
    TradeResult,
    AgentConfig,
    PlatformCredentials,
    Platform,
)
from ..routers import TradeRouter
from ..agents import get_agent

# Initialize FastAPI app
app = FastAPI(
    title="Syrup Trading API",
    description="Agent-based trading interface for Solana, Polymarket, and Kalshi",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global router instance
trade_router = TradeRouter()

# Store active agents
active_agents: dict[str, any] = {}


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "name": "Syrup Trading API",
        "version": "0.1.0",
        "status": "running"
    }


@app.post("/api/platforms/register")
async def register_platform(credentials: PlatformCredentials):
    """Register a trading platform."""
    try:
        trade_router.register_platform(credentials)
        return {
            "success": True,
            "platform": credentials.platform.value,
            "message": "Platform registered successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/platforms/unregister")
async def unregister_platform(platform: Platform):
    """Unregister a trading platform."""
    try:
        trade_router.unregister_platform(platform)
        return {
            "success": True,
            "platform": platform.value,
            "message": "Platform unregistered successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/balances")
async def get_all_balances():
    """Get balances from all registered platforms."""
    try:
        balances = await trade_router.get_all_balances()
        return {
            "success": True,
            "balances": {
                platform.value: balance
                for platform, balance in balances.items()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/balances/{platform}")
async def get_platform_balance(platform: Platform, token: Optional[str] = None):
    """Get balance from a specific platform."""
    try:
        balance = await trade_router.get_balance(platform, token)
        return {
            "success": True,
            "platform": platform.value,
            "balance": balance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/price/{platform}/{symbol}")
async def get_price(platform: Platform, symbol: str):
    """Get price from a platform."""
    try:
        price = await trade_router.get_price(platform, symbol)
        return {
            "success": True,
            "platform": platform.value,
            "symbol": symbol,
            "price": price
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/trade/execute", response_model=TradeResult)
async def execute_trade(trade: TradeRequest):
    """Execute a trade."""
    try:
        result = await trade_router.execute_trade(trade)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/create")
async def create_agent(config: AgentConfig):
    """Create and register a new agent."""
    try:
        agent = get_agent(config)
        active_agents[config.name] = agent
        
        return {
            "success": True,
            "agent_name": config.name,
            "agent_type": config.agent_type,
            "message": "Agent created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/agent/{agent_name}/analyze")
async def analyze_market(
    agent_name: str,
    market_data: dict,
    context: str = ""
):
    """Get market analysis from an agent."""
    agent = active_agents.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    
    try:
        analysis = await agent.analyze_market(market_data, context)
        return {
            "success": True,
            "agent": agent_name,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/{agent_name}/trade")
async def agent_generate_trade(
    agent_name: str,
    market_data: dict,
    portfolio: dict,
    context: str = "",
    execute: bool = False
):
    """Generate trade decision from an agent."""
    agent = active_agents.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    
    try:
        trade_request = await agent.generate_trade_decision(
            market_data,
            portfolio,
            context
        )
        
        if not trade_request:
            return {
                "success": True,
                "agent": agent_name,
                "decision": "hold",
                "message": "Agent decided not to trade"
            }
        
        result = None
        if execute:
            result = await trade_router.execute_trade(trade_request)
        
        return {
            "success": True,
            "agent": agent_name,
            "decision": "trade",
            "trade_request": trade_request.dict(),
            "execution_result": result.dict() if result else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agent/{agent_name}/stream")
async def stream_analysis(
    agent_name: str,
    market_data: dict,
    context: str = ""
):
    """Stream market analysis from an agent."""
    agent = active_agents.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    
    async def generate():
        try:
            async for chunk in agent.stream_analysis(market_data, context):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/agents")
async def list_agents():
    """List all active agents."""
    return {
        "success": True,
        "agents": [
            {
                "name": name,
                "type": agent.config.agent_type,
                "platforms": [p.value for p in agent.config.platforms]
            }
            for name, agent in active_agents.items()
        ]
    }


@app.delete("/api/agent/{agent_name}")
async def delete_agent(agent_name: str):
    """Delete an agent."""
    if agent_name not in active_agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    
    del active_agents[agent_name]
    
    return {
        "success": True,
        "message": f"Agent {agent_name} deleted"
    }


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await trade_router.close_all()


def start():
    """Start the API server."""
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )


if __name__ == "__main__":
    start()

