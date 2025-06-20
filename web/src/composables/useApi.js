import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

export function useApi() {
  // Mock data pour le développement
  const mockAccountInfo = {
    balance: 10000,
    equity: 10250,
    freeMargin: 8500
  }

  const mockOrders = [
    {
      id: 'ORD001',
      channelId: 1,
      symbol: 'XAUUSD',
      type: 'BUY',
      volume: 0.05,
      entryPrice: 2329.79,
      sl: 2314.90,
      tp: 2350.00,
      status: 'OPEN',
      pnl: 125.50,
      timestamp: '2024-01-15T10:30:00Z'
    },
    {
      id: 'ORD002',
      channelId: 1,
      symbol: 'XAUUSD',
      type: 'BUY',
      volume: 0.05,
      entryPrice: 2329.79,
      sl: 2314.90,
      tp: 2375.00,
      status: 'OPEN',
      pnl: 125.50,
      timestamp: '2024-01-15T10:30:00Z'
    },
    {
      id: 'ORD003',
      channelId: 2,
      symbol: 'EURUSD',
      type: 'SELL',
      volume: 0.10,
      entryPrice: 1.0850,
      sl: 1.0890,
      tp: 1.0800,
      status: 'PENDING',
      pnl: 0,
      timestamp: '2024-01-15T11:00:00Z'
    }
  ]

  const mockHistory = [
    {
      id: 'HIS001',
      channelId: 1,
      symbol: 'XAUUSD',
      type: 'BUY',
      volume: 0.05,
      entryPrice: 2320.00,
      exitPrice: 2340.00,
      pnl: 100.00,
      duration: 120,
      closeTime: '2024-01-14T15:30:00Z'
    },
    {
      id: 'HIS002',
      channelId: 2,
      symbol: 'EURUSD',
      type: 'SELL',
      volume: 0.08,
      entryPrice: 1.0900,
      exitPrice: 1.0850,
      pnl: 40.00,
      duration: 85,
      closeTime: '2024-01-13T14:20:00Z'
    },
    {
      id: 'HIS003',
      channelId: 1,
      symbol: 'GBPUSD',
      type: 'BUY',
      volume: 0.06,
      entryPrice: 1.2700,
      exitPrice: 1.2680,
      pnl: -12.00,
      duration: 45,
      closeTime: '2024-01-12T09:15:00Z'
    }
  ]

  const mockStatistics = {
    global: {
      winRate: 67,
      avgRR: 2.3,
      totalSignals: 45
    },
    channels: {
      channel1: {
        totalSignals: 28,
        winRate: 71,
        avgRR: 2.5,
        totalPnl: 850.00,
        bestTrade: 250.00,
        worstTrade: -45.00
      },
      channel2: {
        totalSignals: 17,
        winRate: 59,
        avgRR: 2.0,
        totalPnl: 320.00,
        bestTrade: 180.00,
        worstTrade: -60.00
      }
    },
    symbols: [
      {
        symbol: 'XAUUSD',
        totalTrades: 15,
        winRate: 73,
        avgRR: 2.8,
        totalPnl: 650.00
      },
      {
        symbol: 'EURUSD',
        totalTrades: 12,
        winRate: 58,
        avgRR: 2.1,
        totalPnl: 280.00
      },
      {
        symbol: 'GBPUSD',
        totalTrades: 8,
        winRate: 62,
        avgRR: 1.9,
        totalPnl: 120.00
      }
    ]
  }

  const fetchAccountInfo = async () => {
    try {
      // En production, remplacer par: const response = await api.get('/account')
      // return response.data
      return mockAccountInfo
    } catch (error) {
      console.error('Erreur API fetchAccountInfo:', error)
      return mockAccountInfo
    }
  }

  const fetchOrders = async () => {
    try {
      // En production, remplacer par: const response = await api.get('/orders')
      // return response.data
      return mockOrders
    } catch (error) {
      console.error('Erreur API fetchOrders:', error)
      return mockOrders
    }
  }

  const fetchHistory = async () => {
    try {
      // En production, remplacer par: const response = await api.get('/history')
      // return response.data
      return mockHistory
    } catch (error) {
      console.error('Erreur API fetchHistory:', error)
      return mockHistory
    }
  }

  const fetchStatistics = async () => {
    try {
      // En production, remplacer par: const response = await api.get('/statistics')
      // return response.data
      return mockStatistics
    } catch (error) {
      console.error('Erreur API fetchStatistics:', error)
      return mockStatistics
    }
  }

  const closeOrder = async (orderId) => {
    try {
      // En production, remplacer par: const response = await api.post(`/orders/${orderId}/close`)
      // return response.data
      console.log(`Fermeture de l'ordre ${orderId}`)
      return { success: true }
    } catch (error) {
      console.error('Erreur API closeOrder:', error)
      throw error
    }
  }

  return {
    fetchAccountInfo,
    fetchOrders,
    fetchHistory,
    fetchStatistics,
    closeOrder
  }
}