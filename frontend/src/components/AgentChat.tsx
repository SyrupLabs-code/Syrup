import React, { useState, useRef, useEffect } from 'react'
import { agentAPI } from '../services/api'
import { useStore } from '../store/useStore'

interface AgentChatProps {
  agentName: string
}

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const AgentChat: React.FC<AgentChatProps> = ({ agentName }) => {
  const { platforms } = useStore()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [marketData, setMarketData] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  
  const handleAnalyze = async () => {
    if (!input && !marketData) return
    
    setLoading(true)
    
    const userMessage = input || 'Analyze the current market data'
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setInput('')
    
    try {
      let parsedMarketData = {}
      
      if (marketData) {
        try {
          parsedMarketData = JSON.parse(marketData)
        } catch {
          parsedMarketData = { raw: marketData }
        }
      }
      
      const result = await agentAPI.analyze(agentName, parsedMarketData, userMessage)
      
      if (result.analysis) {
        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            content: result.analysis.analysis || JSON.stringify(result.analysis, null, 2)
          }
        ])
      }
    } catch (error: any) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${error.response?.data?.detail || 'Failed to get analysis'}`
        }
      ])
    } finally {
      setLoading(false)
    }
  }
  
  const handleGenerateTrade = async (execute: boolean = false) => {
    if (!marketData) {
      alert('Please provide market data')
      return
    }
    
    setLoading(true)
    setMessages(prev => [
      ...prev,
      { role: 'user', content: `Generate trade decision (${execute ? 'execute' : 'preview only'})` }
    ])
    
    try {
      let parsedMarketData = {}
      
      try {
        parsedMarketData = JSON.parse(marketData)
      } catch {
        parsedMarketData = { raw: marketData }
      }
      
      const portfolio = {} // Could fetch actual portfolio data
      
      const result = await agentAPI.generateTrade(
        agentName,
        parsedMarketData,
        portfolio,
        input || '',
        execute
      )
      
      if (result.decision === 'hold') {
        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            content: `Decision: HOLD\nThe agent has decided not to trade at this time.`
          }
        ])
      } else {
        const trade = result.trade_request
        const execution = result.execution_result
        
        let response = `Decision: TRADE\n\nPlatform: ${trade.platform}\nType: ${trade.trade_type}\nSymbol: ${trade.symbol}\nAmount: ${trade.amount}\n`
        
        if (trade.price) {
          response += `Price: $${trade.price}\n`
        }
        
        if (trade.metadata?.reasoning) {
          response += `\nReasoning: ${trade.metadata.reasoning}\n`
        }
        
        if (execution) {
          response += `\n--- Execution Result ---\nStatus: ${execution.status}\n`
          
          if (execution.transaction_hash) {
            response += `TX: ${execution.transaction_hash}\n`
          }
          
          if (execution.error) {
            response += `Error: ${execution.error}\n`
          }
        }
        
        setMessages(prev => [
          ...prev,
          { role: 'assistant', content: response }
        ])
      }
    } catch (error: any) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${error.response?.data?.detail || 'Failed to generate trade'}`
        }
      ])
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="bg-slate-800 rounded-lg p-6 h-[600px] flex flex-col">
      <h2 className="text-xl font-semibold mb-4">Agent: {agentName}</h2>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-slate-400 py-8">
            <p>Start a conversation with your trading agent</p>
            <p className="text-sm mt-2">Provide market data and ask for analysis or trade decisions</p>
          </div>
        )}
        
        {messages.map((message, index) => (
          <div
            key={index}
            className={`p-3 rounded ${
              message.role === 'user'
                ? 'bg-blue-900/30 ml-8'
                : 'bg-slate-700 mr-8'
            }`}
          >
            <p className="text-sm font-medium mb-1">
              {message.role === 'user' ? 'You' : 'Agent'}
            </p>
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          </div>
        ))}
        
        {loading && (
          <div className="p-3 rounded bg-slate-700 mr-8">
            <p className="text-sm font-medium mb-1">Agent</p>
            <p className="text-sm text-slate-400">Thinking...</p>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Area */}
      <div className="space-y-3 border-t border-slate-700 pt-4">
        <div>
          <label className="block text-xs font-medium mb-1 text-slate-400">
            Market Data (JSON or text)
          </label>
          <textarea
            value={marketData}
            onChange={(e) => setMarketData(e.target.value)}
            placeholder='{"symbol": "SOL/USDC", "price": 100, "volume": 1000000}'
            rows={2}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-sm"
          />
        </div>
        
        <div>
          <label className="block text-xs font-medium mb-1 text-slate-400">
            Message / Context
          </label>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !loading && handleAnalyze()}
            placeholder="Ask for analysis or insights..."
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-sm"
          />
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed rounded font-medium text-sm transition-colors"
          >
            Analyze
          </button>
          <button
            onClick={() => handleGenerateTrade(false)}
            disabled={loading}
            className="flex-1 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 disabled:cursor-not-allowed rounded font-medium text-sm transition-colors"
          >
            Preview Trade
          </button>
          <button
            onClick={() => handleGenerateTrade(true)}
            disabled={loading}
            className="flex-1 py-2 bg-green-600 hover:bg-green-700 disabled:bg-slate-600 disabled:cursor-not-allowed rounded font-medium text-sm transition-colors"
          >
            Execute Trade
          </button>
        </div>
      </div>
    </div>
  )
}

export default AgentChat

