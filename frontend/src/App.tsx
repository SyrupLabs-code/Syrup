import React, { useState } from 'react'
import Dashboard from './components/Dashboard'
import Setup from './components/Setup'
import { useStore } from './store/useStore'

function App() {
  const { isConfigured } = useStore()
  const [showSetup, setShowSetup] = useState(!isConfigured)

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {showSetup ? (
        <Setup onComplete={() => setShowSetup(false)} />
      ) : (
        <Dashboard onReconfigure={() => setShowSetup(true)} />
      )}
    </div>
  )
}

export default App

