import React, { useState } from 'react'
import { Platform, AgentType, PlatformCredentials, AgentConfig } from '../types'
import { useStore } from '../store/useStore'
import { platformAPI, agentAPI } from '../services/api'

interface SetupProps {
  onComplete: () => void
}

const Setup: React.FC<SetupProps> = ({ onComplete }) => {
  const { addPlatform, addAgent, setConfigured } = useStore()
  
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  // Platform state
  const [selectedPlatforms, setSelectedPlatforms] = useState<Platform[]>([])
  const [platformCreds, setPlatformCreds] = useState<Record<Platform, Partial<PlatformCredentials>>>({
    [Platform.SOLANA]: {},
    [Platform.POLYMARKET]: {},
    [Platform.KALSHI]: {},
  })
  
  // Agent state
  const [agentName, setAgentName] = useState('trading-agent-1')
  const [agentType, setAgentType] = useState<AgentType>(AgentType.OPENAI)
  const [apiKey, setApiKey] = useState('')
  const [model, setModel] = useState('gpt-4-turbo-preview')
  const [systemPrompt, setSystemPrompt] = useState(
    'You are a professional trading agent. Analyze market data carefully and make informed trading decisions based on risk management principles.'
  )
  const [maxPositionSize, setMaxPositionSize] = useState(1000)
  const [riskLimit, setRiskLimit] = useState(0.1)
  
  const handlePlatformToggle = (platform: Platform) => {
    setSelectedPlatforms(prev =>
      prev.includes(platform)
        ? prev.filter(p => p !== platform)
        : [...prev, platform]
    )
  }
  
  const handlePlatformCredChange = (platform: Platform, field: string, value: string) => {
    setPlatformCreds(prev => ({
      ...prev,
      [platform]: {
        ...prev[platform],
        [field]: value,
      },
    }))
  }
  
  const handleRegisterPlatforms = async () => {
    setLoading(true)
    setError('')
    
    try {
      for (const platform of selectedPlatforms) {
        const creds: PlatformCredentials = {
          platform,
          ...platformCreds[platform],
        }
        
        await platformAPI.register(creds)
        addPlatform(creds)
      }
      
      setStep(2)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to register platforms')
    } finally {
      setLoading(false)
    }
  }
  
  const handleCreateAgent = async () => {
    setLoading(true)
    setError('')
    
    try {
      const config: AgentConfig = {
        name: agentName,
        agent_type: agentType,
        api_key: apiKey,
        model,
        system_prompt: systemPrompt,
        max_position_size: maxPositionSize,
        risk_limit: riskLimit,
        platforms: selectedPlatforms,
      }
      
      await agentAPI.create(config)
      addAgent(config)
      setConfigured(true)
      onComplete()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create agent')
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-slate-800 rounded-lg shadow-xl p-8">
        <h1 className="text-3xl font-bold mb-2">Syrup Setup</h1>
        <p className="text-slate-400 mb-8">Configure your trading platforms and agent</p>
        
        {error && (
          <div className="mb-4 p-4 bg-red-900/50 border border-red-500 rounded text-red-200">
            {error}
          </div>
        )}
        
        {step === 1 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">Step 1: Platform Configuration</h2>
            
            <div className="space-y-4">
              {/* Solana */}
              <div className="border border-slate-700 rounded p-4">
                <label className="flex items-center mb-3">
                  <input
                    type="checkbox"
                    checked={selectedPlatforms.includes(Platform.SOLANA)}
                    onChange={() => handlePlatformToggle(Platform.SOLANA)}
                    className="mr-2"
                  />
                  <span className="font-medium">Solana</span>
                </label>
                
                {selectedPlatforms.includes(Platform.SOLANA) && (
                  <div className="space-y-2 ml-6">
                    <input
                      type="text"
                      placeholder="RPC URL (optional)"
                      value={platformCreds[Platform.SOLANA].rpc_url || ''}
                      onChange={(e) => handlePlatformCredChange(Platform.SOLANA, 'rpc_url', e.target.value)}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
                    />
                    <input
                      type="password"
                      placeholder="Private Key"
                      value={platformCreds[Platform.SOLANA].private_key || ''}
                      onChange={(e) => handlePlatformCredChange(Platform.SOLANA, 'private_key', e.target.value)}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
                    />
                  </div>
                )}
              </div>
              
              {/* Polymarket */}
              <div className="border border-slate-700 rounded p-4">
                <label className="flex items-center mb-3">
                  <input
                    type="checkbox"
                    checked={selectedPlatforms.includes(Platform.POLYMARKET)}
                    onChange={() => handlePlatformToggle(Platform.POLYMARKET)}
                    className="mr-2"
                  />
                  <span className="font-medium">Polymarket</span>
                </label>
                
                {selectedPlatforms.includes(Platform.POLYMARKET) && (
                  <div className="space-y-2 ml-6">
                    <input
                      type="text"
                      placeholder="API Key"
                      value={platformCreds[Platform.POLYMARKET].api_key || ''}
                      onChange={(e) => handlePlatformCredChange(Platform.POLYMARKET, 'api_key', e.target.value)}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
                    />
                    <input
                      type="password"
                      placeholder="Secret"
                      value={platformCreds[Platform.POLYMARKET].secret || ''}
                      onChange={(e) => handlePlatformCredChange(Platform.POLYMARKET, 'secret', e.target.value)}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
                    />
                    <input
                      type="password"
                      placeholder="Passphrase"
                      value={platformCreds[Platform.POLYMARKET].passphrase || ''}
                      onChange={(e) => handlePlatformCredChange(Platform.POLYMARKET, 'passphrase', e.target.value)}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
                    />
                  </div>
                )}
              </div>
              
              {/* Kalshi */}
              <div className="border border-slate-700 rounded p-4">
                <label className="flex items-center mb-3">
                  <input
                    type="checkbox"
                    checked={selectedPlatforms.includes(Platform.KALSHI)}
                    onChange={() => handlePlatformToggle(Platform.KALSHI)}
                    className="mr-2"
                  />
                  <span className="font-medium">Kalshi</span>
                </label>
                
                {selectedPlatforms.includes(Platform.KALSHI) && (
                  <div className="space-y-2 ml-6">
                    <input
                      type="text"
                      placeholder="API Key"
                      value={platformCreds[Platform.KALSHI].api_key || ''}
                      onChange={(e) => handlePlatformCredChange(Platform.KALSHI, 'api_key', e.target.value)}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
                    />
                    <input
                      type="password"
                      placeholder="Private Key"
                      value={platformCreds[Platform.KALSHI].private_key || ''}
                      onChange={(e) => handlePlatformCredChange(Platform.KALSHI, 'private_key', e.target.value)}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
                    />
                  </div>
                )}
              </div>
            </div>
            
            <button
              onClick={handleRegisterPlatforms}
              disabled={selectedPlatforms.length === 0 || loading}
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed rounded font-medium transition-colors"
            >
              {loading ? 'Registering...' : 'Continue to Agent Setup'}
            </button>
          </div>
        )}
        
        {step === 2 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">Step 2: Agent Configuration</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Agent Name</label>
                <input
                  type="text"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Agent Type</label>
                <select
                  value={agentType}
                  onChange={(e) => {
                    setAgentType(e.target.value as AgentType)
                    setModel(e.target.value === AgentType.OPENAI ? 'gpt-4-turbo-preview' : 'claude-3-opus-20240229')
                  }}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
                >
                  <option value={AgentType.OPENAI}>OpenAI</option>
                  <option value={AgentType.ANTHROPIC}>Anthropic</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">API Key</label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
                  placeholder={`Enter your ${agentType === AgentType.OPENAI ? 'OpenAI' : 'Anthropic'} API key`}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Model</label>
                <input
                  type="text"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">System Prompt</label>
                <textarea
                  value={systemPrompt}
                  onChange={(e) => setSystemPrompt(e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Max Position Size</label>
                  <input
                    type="number"
                    value={maxPositionSize}
                    onChange={(e) => setMaxPositionSize(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Risk Limit (%)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={riskLimit * 100}
                    onChange={(e) => setRiskLimit(Number(e.target.value) / 100)}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded"
                  />
                </div>
              </div>
            </div>
            
            <div className="flex gap-4">
              <button
                onClick={() => setStep(1)}
                className="flex-1 py-3 bg-slate-600 hover:bg-slate-700 rounded font-medium transition-colors"
              >
                Back
              </button>
              <button
                onClick={handleCreateAgent}
                disabled={!agentName || !apiKey || loading}
                className="flex-1 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed rounded font-medium transition-colors"
              >
                {loading ? 'Creating...' : 'Complete Setup'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Setup

