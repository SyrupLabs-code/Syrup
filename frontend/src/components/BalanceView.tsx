import React from 'react'
import { Balance } from '../types'

interface BalanceViewProps {
  balances: Record<string, Balance>
  onRefresh: () => void
}

const BalanceView: React.FC<BalanceViewProps> = ({ balances, onRefresh }) => {
  return (
    <div className="bg-slate-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Account Balances</h2>
        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded transition-colors"
        >
          Refresh
        </button>
      </div>
      
      <div className="space-y-4">
        {Object.entries(balances).map(([platform, balance]) => (
          <div key={platform} className="border border-slate-700 rounded p-4">
            <h3 className="font-medium mb-3 capitalize">{platform}</h3>
            
            {Object.entries(balance).length > 0 ? (
              <div className="space-y-2">
                {Object.entries(balance).map(([token, amount]) => (
                  <div key={token} className="flex items-center justify-between p-2 bg-slate-700 rounded">
                    <span className="font-medium">{token}</span>
                    <span className="text-slate-300">{amount.toFixed(6)}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-400">No balances available</p>
            )}
          </div>
        ))}
        
        {Object.keys(balances).length === 0 && (
          <p className="text-center text-slate-400 py-8">
            No platform balances loaded
          </p>
        )}
      </div>
    </div>
  )
}

export default BalanceView

