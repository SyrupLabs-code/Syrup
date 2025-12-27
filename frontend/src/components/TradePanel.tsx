import React, { useState } from 'react'
import { useStore } from '../store/useStore'
import { tradeAPI } from '../services/api'
import { Platform, TradeType, TradeRequest } from '../types'

interface TradePanelProps {
  onTradeExecuted?: () => void
}

const TradePanel: React.FC<TradePanelProps> = ({ onTradeExecuted }) => {
  const { platforms } = useStore()
  
  const [platform, setPlatform] = useState<Platform>(platforms[0]?.platform || Platform.SOLANA)
  const [tradeType, setTradeType] = useState<TradeType>(TradeType.BUY)
  const [symbol, setSymbol] = useState('')
  const [amount, setAmount] = useState('')
  const [price, setPrice] = useState('')
  const [slippage, setSlippage] = useState('1')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  
  const handleExecute = async () => {
    if (!symbol || !amount) {
      alert('Please fill in all required fields')
      return
    }
    
    setLoading(true)
    setResult(null)
    
    try {
      const trade: TradeRequest = {
        platform,
        trade_type: tradeType,
        symbol,
        amount: parseFloat(amount),
        price: price ? parseFloat(price) : undefined,
        slippage: parseFloat(slippage) / 100,
      }
      
      const tradeResult = await tradeAPI.execute(trade)
      setResult(tradeResult)
      
      if (tradeResult.status === 'completed') {
        onTradeExecuted?.()
      }
    } catch (error: any) {
      setResult({ error: error.response?.data?.detail || 'Trade execution failed' })
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="bg-slate-800 rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-6">Manual Trade Execution</h2>
      
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Platform</label>
            <select
              value={platform}
              onChange={(e) => setPlatform(e.target.value as Platform)}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
            >
              {platforms.map((p) => (
                <option key={p.platform} value={p.platform}>
                  {p.platform.charAt(0).toUpperCase() + p.platform.slice(1)}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Trade Type</label>
            <select
              value={tradeType}
              onChange={(e) => setTradeType(e.target.value as TradeType)}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
            >
              <option value={TradeType.BUY}>Buy</option>
              <option value={TradeType.SELL}>Sell</option>
              <option value={TradeType.SWAP}>Swap</option>
            </select>
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Symbol / Market</label>
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            placeholder="e.g., SOL/USDC, market_id"
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
          />
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Amount</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.00"
              step="0.01"
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Price (optional)</label>
            <input
              type="number"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              placeholder="Market price"
              step="0.01"
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Slippage (%)</label>
          <input
            type="number"
            value={slippage}
            onChange={(e) => setSlippage(e.target.value)}
            step="0.1"
            min="0"
            max="100"
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
          />
        </div>
        
        <button
          onClick={handleExecute}
          disabled={loading || !symbol || !amount}
          className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed rounded font-medium transition-colors"
        >
          {loading ? 'Executing...' : 'Execute Trade'}
        </button>
        
        {result && (
          <div className={`p-4 rounded ${result.error ? 'bg-red-900/30 border border-red-500' : 'bg-green-900/30 border border-green-500'}`}>
            {result.error ? (
              <>
                <p className="font-semibold text-red-200">Trade Failed</p>
                <p className="text-sm text-red-300 mt-1">{result.error}</p>
              </>
            ) : (
              <>
                <p className="font-semibold text-green-200">Trade {result.status}</p>
                <div className="text-sm text-green-300 mt-2 space-y-1">
                  {result.transaction_hash && (
                    <p>TX: {result.transaction_hash.slice(0, 16)}...</p>
                  )}
                  {result.executed_amount && (
                    <p>Amount: {result.executed_amount}</p>
                  )}
                  {result.executed_price && (
                    <p>Price: ${result.executed_price}</p>
                  )}
                  {result.fee && (
                    <p>Fee: ${result.fee}</p>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default TradePanel

