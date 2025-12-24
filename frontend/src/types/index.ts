export enum Platform {
  SOLANA = 'solana',
  POLYMARKET = 'polymarket',
  KALSHI = 'kalshi',
}

export enum TradeType {
  BUY = 'buy',
  SELL = 'sell',
  SWAP = 'swap',
}

export enum TradeStatus {
  PENDING = 'pending',
  EXECUTING = 'executing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export enum AgentType {
  OPENAI = 'openai',
  ANTHROPIC = 'anthropic',
}

export interface PlatformCredentials {
  platform: Platform
  rpc_url?: string
  api_key?: string
  secret?: string
  private_key?: string
  passphrase?: string
  wallet_address?: string
  metadata?: Record<string, any>
}

export interface AgentConfig {
  name: string
  agent_type: AgentType
  api_key?: string
  model: string
  system_prompt: string
  max_position_size: number
  risk_limit: number
  platforms: Platform[]
  metadata?: Record<string, any>
}

export interface TradeRequest {
  platform: Platform
  trade_type: TradeType
  symbol: string
  amount: number
  price?: number
  slippage: number
  metadata?: Record<string, any>
}

export interface TradeResult {
  trade_id: string
  platform: Platform
  status: TradeStatus
  transaction_hash?: string
  executed_amount?: number
  executed_price?: number
  fee?: number
  timestamp: string
  error?: string
  metadata?: Record<string, any>
}

export interface Balance {
  [token: string]: number
}

export interface MarketData {
  symbol: string
  price: number
  volume?: number
  change_24h?: number
  [key: string]: any
}

