import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { Platform, AgentConfig, PlatformCredentials } from '../types'

interface StoreState {
  isConfigured: boolean
  platforms: PlatformCredentials[]
  agents: AgentConfig[]
  currentAgent?: string
  
  addPlatform: (platform: PlatformCredentials) => void
  removePlatform: (platform: Platform) => void
  addAgent: (agent: AgentConfig) => void
  removeAgent: (name: string) => void
  setCurrentAgent: (name: string) => void
  setConfigured: (value: boolean) => void
  reset: () => void
}

export const useStore = create<StoreState>()(
  persist(
    (set) => ({
      isConfigured: false,
      platforms: [],
      agents: [],
      currentAgent: undefined,
      
      addPlatform: (platform) =>
        set((state) => ({
          platforms: [...state.platforms.filter(p => p.platform !== platform.platform), platform],
        })),
      
      removePlatform: (platform) =>
        set((state) => ({
          platforms: state.platforms.filter(p => p.platform !== platform),
        })),
      
      addAgent: (agent) =>
        set((state) => ({
          agents: [...state.agents.filter(a => a.name !== agent.name), agent],
          currentAgent: state.currentAgent || agent.name,
        })),
      
      removeAgent: (name) =>
        set((state) => ({
          agents: state.agents.filter(a => a.name !== name),
          currentAgent: state.currentAgent === name ? undefined : state.currentAgent,
        })),
      
      setCurrentAgent: (name) =>
        set({ currentAgent: name }),
      
      setConfigured: (value) =>
        set({ isConfigured: value }),
      
      reset: () =>
        set({
          isConfigured: false,
          platforms: [],
          agents: [],
          currentAgent: undefined,
        }),
    }),
    {
      name: 'syrup-storage',
    }
  )
)

