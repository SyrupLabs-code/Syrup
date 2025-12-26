import axios from 'axios'
import {
  Platform,
  PlatformCredentials,
  AgentConfig,
  TradeRequest,
  TradeResult,
  Balance,
} from '../types'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const platformAPI = {
  register: async (credentials: PlatformCredentials) => {
    const response = await api.post('/platforms/register', credentials)
    return response.data
  },
  
  unregister: async (platform: Platform) => {
    const response = await api.post('/platforms/unregister', { platform })
    return response.data
  },
  
  getBalance: async (platform: Platform, token?: string) => {
    const response = await api.get<{ balance: Balance }>(`/balances/${platform}`, {
      params: { token },
    })
    return response.data.balance
  },
  
  getAllBalances: async () => {
    const response = await api.get<{ balances: Record<string, Balance> }>('/balances')
    return response.data.balances
  },
  
  getPrice: async (platform: Platform, symbol: string) => {
    const response = await api.get<{ price: number }>(`/price/${platform}/${symbol}`)
    return response.data.price
  },
}

export const agentAPI = {
  create: async (config: AgentConfig) => {
    const response = await api.post('/agent/create', config)
    return response.data
  },
  
  list: async () => {
    const response = await api.get<{ agents: Array<{ name: string; type: string; platforms: string[] }> }>('/agents')
    return response.data.agents
  },
  
  delete: async (name: string) => {
    const response = await api.delete(`/agent/${name}`)
    return response.data
  },
  
  analyze: async (agentName: string, marketData: any, context: string = '') => {
    const response = await api.post(`/agent/${agentName}/analyze`, {
      market_data: marketData,
      context,
    })
    return response.data
  },
  
  generateTrade: async (
    agentName: string,
    marketData: any,
    portfolio: any,
    context: string = '',
    execute: boolean = false
  ) => {
    const response = await api.post(`/agent/${agentName}/trade`, {
      market_data: marketData,
      portfolio,
      context,
      execute,
    })
    return response.data
  },
  
  streamAnalysis: async (agentName: string, marketData: any, context: string = '') => {
    const response = await fetch(`/api/agent/${agentName}/stream?market_data=${encodeURIComponent(JSON.stringify(marketData))}&context=${encodeURIComponent(context)}`)
    return response.body
  },
}

export const tradeAPI = {
  execute: async (trade: TradeRequest): Promise<TradeResult> => {
    const response = await api.post<TradeResult>('/trade/execute', trade)
    return response.data
  },
}

export default api

