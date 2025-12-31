# Syrup

Agent-based trading interface for Solana, Polymarket, and Kalshi. Configure your trading agents with AI providers (OpenAI, Anthropic) and execute trades across multiple platforms through a unified API and web interface.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Setup   │  │Dashboard │  │  Agent   │  │  Trade   │   │
│  │          │  │          │  │   Chat   │  │  Panel   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   Trade Router                        │  │
│  └──────────────────────────────────────────────────────┘  │
│         ↓                    ↓                    ↓          │
│  ┌──────────┐        ┌──────────┐        ┌──────────┐     │
│  │ Solana   │        │Polymarket│        │  Kalshi  │     │
│  │ Adapter  │        │ Adapter  │        │ Adapter  │     │
│  └──────────┘        └──────────┘        └──────────┘     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Agent System                         │  │
│  │  ┌──────────┐              ┌──────────┐             │  │
│  │  │ OpenAI   │              │Anthropic │             │  │
│  │  │  Agent   │              │  Agent   │             │  │
│  │  └──────────┘              └──────────┘             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         ↓                       ↓                    ↓
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Solana     │     │  Polymarket  │     │    Kalshi    │
│ (Jupiter)    │     │     API      │     │     API      │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Core Components

### Platform Adapters

Abstract trading operations across different platforms:

- **Solana**: DEX trading via Jupiter aggregator
- **Polymarket**: Prediction market trading
- **Kalshi**: Event contract trading

Each adapter implements:
```python
async def execute_trade(trade: TradeRequest) -> TradeResult
async def get_balance(token: Optional[str]) -> dict[str, float]
async def get_price(symbol: str) -> float
async def get_order_status(order_id: str) -> dict
async def cancel_order(order_id: str) -> bool
```

### Trade Router

Routes trades to appropriate platforms based on request. Manages platform registration and credential storage.

### Agent System

AI-powered trading agents that:
- Analyze market data
- Generate trade decisions
- Execute trades with risk management
- Support streaming analysis

Supported providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3)

## Installation

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Configuration

### Environment Variables

Create `backend/.env`:

```env
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Platform Credentials

Configure through the web interface or API:

**Solana**:
- RPC URL (optional)
- Private key (base58 encoded)

**Polymarket**:
- API key
- Secret
- Passphrase

**Kalshi**:
- API key
- Private key

## Usage

### Start Backend

```bash
cd backend
python -m uvicorn src.api.main:app --reload
```

API available at http://localhost:8000

### Start Frontend

```bash
cd frontend
npm run dev
```

Web interface available at http://localhost:3000

### API Examples

**Register Platform**:
```bash
curl -X POST http://localhost:8000/api/platforms/register \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "solana",
    "rpc_url": "https://api.mainnet-beta.solana.com",
    "private_key": "your_base58_key"
  }'
```

**Create Agent**:
```bash
curl -X POST http://localhost:8000/api/agent/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "trader-1",
    "agent_type": "openai",
    "api_key": "sk-...",
    "model": "gpt-4-turbo-preview",
    "system_prompt": "You are a trading agent.",
    "max_position_size": 1000,
    "risk_limit": 0.1,
    "platforms": ["solana"]
  }'
```

**Execute Trade**:
```bash
curl -X POST http://localhost:8000/api/trade/execute \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "solana",
    "trade_type": "swap",
    "symbol": "SOL/USDC",
    "amount": 1.0,
    "slippage": 0.01
  }'
```

**Get Agent Analysis**:
```bash
curl -X POST http://localhost:8000/api/agent/trader-1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "market_data": {
      "symbol": "SOL/USDC",
      "price": 100,
      "volume": 1000000,
      "trend": "bullish"
    },
    "context": "Should I enter a position?"
  }'
```

**Agent Trade Decision**:
```bash
curl -X POST http://localhost:8000/api/agent/trader-1/trade \
  -H "Content-Type: application/json" \
  -d '{
    "market_data": {"symbol": "SOL/USDC", "price": 100},
    "portfolio": {"SOL": 10, "USDC": 1000},
    "context": "Analyze and decide",
    "execute": false
  }'
```

## Project Structure

```
syrup/
├── backend/
│   ├── src/
│   │   ├── agents/          # AI agent implementations
│   │   │   ├── base.py
│   │   │   ├── openai_agent.py
│   │   │   └── anthropic_agent.py
│   │   ├── platforms/       # Platform adapters
│   │   │   ├── base.py
│   │   │   ├── solana_adapter.py
│   │   │   ├── polymarket_adapter.py
│   │   │   └── kalshi_adapter.py
│   │   ├── routers/         # Trade routing
│   │   │   └── trade_router.py
│   │   ├── models/          # Data models
│   │   │   └── trade.py
│   │   ├── config/          # Configuration
│   │   │   └── settings.py
│   │   └── api/             # FastAPI application
│   │       └── main.py
│   ├── requirements.txt
│   └── setup.py
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Setup.tsx
│   │   │   ├── AgentChat.tsx
│   │   │   ├── TradePanel.tsx
│   │   │   └── BalanceView.tsx
│   │   ├── services/        # API client
│   │   │   └── api.ts
│   │   ├── store/           # State management
│   │   │   └── useStore.ts
│   │   ├── types/           # TypeScript types
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── examples/                # Example scripts
└── README.md
```

## Security Notes

- Never commit API keys or private keys to version control
- Use environment variables for sensitive data
- Implement proper key management in production
- Validate all trade parameters before execution
- Set appropriate risk limits on agents
- Use testnet/devnet for development

## Development

### Adding New Platform

1. Create adapter in `backend/src/platforms/`:
```python
from .base import BasePlatform

class NewPlatformAdapter(BasePlatform):
    def _initialize(self) -> None:
        # Setup connection
        pass
    
    async def execute_trade(self, trade: TradeRequest) -> TradeResult:
        # Implement trading logic
        pass
    
    # Implement other required methods
```

2. Register in `backend/src/platforms/__init__.py`
3. Add platform enum to `backend/src/models/trade.py`
4. Update frontend types in `frontend/src/types/index.ts`

### Adding New Agent Type

1. Create agent in `backend/src/agents/`:
```python
from .base import BaseAgent

class CustomAgent(BaseAgent):
    def _initialize(self) -> None:
        # Setup AI client
        pass
    
    async def generate_trade_decision(
        self, 
        market_data: dict,
        portfolio: dict,
        context: str
    ) -> Optional[TradeRequest]:
        # Implement decision logic
        pass
    
    # Implement other required methods
```

2. Register in `backend/src/agents/__init__.py`

## License

MIT

## Contributing

Contributions welcome. Please ensure:
- Code follows existing patterns
- Tests pass
- Documentation is updated
- No sensitive data in commits

