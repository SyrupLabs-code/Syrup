import React, { useState, useEffect } from 'react'
import { useStore } from '../store/useStore'
import { platformAPI, agentAPI, tradeAPI } from '../services/api'
import { Platform, TradeType, Balance } from '../types'
import TradePanel from './TradePanel'
import BalanceView from './BalanceView'
import AgentChat from './AgentChat'

interface DashboardProps {
  onReconfigure: () => void
}

const Dashboard: React.FC<DashboardProps> = ({ onReconfigure }) => {
  const { currentAgent, agents, platforms } = useStore()
  const [balances, setBalances] = useState<Record<string, Balance>>({})
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'trade' | 'analyze' | 'balances'>('analyze')
  
  const currentAgentConfig = agents.find(a => a.name === currentAgent)
  
  useEffect(() => {
    loadBalances()
  }, [platforms])
  
  const loadBalances = async () => {
    setLoading(true)
    try {
      const data = await platformAPI.getAllBalances()
      setBalances(data)
    } catch (error) {
      console.error('Failed to load balances:', error)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Syrup</h1>
            <p className="text-sm text-slate-400">Agent-Based Trading Interface</p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm text-slate-400">Active Agent</p>
              <p className="font-medium">{currentAgent || 'None'}</p>
            </div>
            
            <button
              onClick={onReconfigure}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded transition-colors"
            >
              Settings
            </button>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-slate-700">
          <button
            onClick={() => setActiveTab('analyze')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'analyze'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Agent Analysis
          </button>
          <button
            onClick={() => setActiveTab('trade')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'trade'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Manual Trade
          </button>
          <button
            onClick={() => setActiveTab('balances')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'balances'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Balances
          </button>
        </div>
        
        {/* Tab Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            {activeTab === 'analyze' && currentAgent && (
              <AgentChat agentName={currentAgent} />
            )}
            
            {activeTab === 'trade' && (
              <TradePanel onTradeExecuted={loadBalances} />
            )}
            
            {activeTab === 'balances' && (
              <BalanceView balances={balances} onRefresh={loadBalances} />
            )}
          </div>
          
          {/* Sidebar */}
          <div className="space-y-4">
            <div className="bg-slate-800 rounded-lg p-4">
              <h3 className="font-semibold mb-3">Connected Platforms</h3>
              <div className="space-y-2">
                {platforms.map((platform) => (
                  <div
                    key={platform.platform}
                    className="flex items-center justify-between p-2 bg-slate-700 rounded"
                  >
                    <span className="capitalize">{platform.platform}</span>
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  </div>
                ))}
                {platforms.length === 0 && (
                  <p className="text-sm text-slate-400">No platforms connected</p>
                )}
              </div>
            </div>
            
            <div className="bg-slate-800 rounded-lg p-4">
              <h3 className="font-semibold mb-3">Quick Stats</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-slate-400">Total Platforms</p>
                  <p className="text-2xl font-bold">{platforms.length}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Active Agents</p>
                  <p className="text-2xl font-bold">{agents.length}</p>
                </div>
                {currentAgentConfig && (
                  <div>
                    <p className="text-sm text-slate-400">Max Position</p>
                    <p className="text-xl font-bold">${currentAgentConfig.max_position_size}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

