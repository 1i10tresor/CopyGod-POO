<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900">Historique</h2>
      <div class="flex space-x-3">
        <select v-model="periodFilter" class="rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500">
          <option value="week">Cette semaine</option>
          <option value="month">Ce mois</option>
          <option value="all">Tout l'historique</option>
        </select>
        <button @click="refreshHistory" class="btn-primary">
          <ArrowPathIcon class="w-4 h-4 mr-2" />
          Actualiser
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ChartBarIcon class="h-8 w-8 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Trades</p>
            <p class="text-2xl font-semibold text-gray-900">{{ historySummary.totalTrades }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <CheckCircleIcon class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Trades Gagnants</p>
            <p class="text-2xl font-semibold text-green-600">{{ historySummary.winningTrades }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <XCircleIcon class="h-8 w-8 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Trades Perdants</p>
            <p class="text-2xl font-semibold text-red-600">{{ historySummary.losingTrades }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <CurrencyEuroIcon class="h-8 w-8 text-purple-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">P&L Total</p>
            <p class="text-2xl font-semibold" :class="historySummary.totalPnl >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ formatCurrency(historySummary.totalPnl) }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- History Table -->
    <div class="card">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Signal</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbole</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Volume</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prix d'entrée</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prix de sortie</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Durée</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P&L</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="trade in filteredHistory" :key="trade.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ formatDate(trade.closeTime) }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  Canal {{ trade.channelId }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ trade.symbol }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="trade.type === 'BUY' ? 'text-green-600' : 'text-red-600'" class="text-sm font-medium">
                  {{ trade.type }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ trade.volume }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ trade.entryPrice }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ trade.exitPrice }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ formatDuration(trade.duration) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium" :class="trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'">
                {{ formatCurrency(trade.pnl) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  ArrowPathIcon, 
  ChartBarIcon, 
  CheckCircleIcon, 
  XCircleIcon, 
  CurrencyEuroIcon 
} from '@heroicons/vue/24/outline'
import { useApi } from '../composables/useApi'

const { fetchHistory } = useApi()

const history = ref([])
const periodFilter = ref('week')

const filteredHistory = computed(() => {
  const now = new Date()
  const filterDate = new Date()
  
  switch (periodFilter.value) {
    case 'week':
      filterDate.setDate(now.getDate() - 7)
      break
    case 'month':
      filterDate.setMonth(now.getMonth() - 1)
      break
    default:
      return history.value
  }
  
  return history.value.filter(trade => new Date(trade.closeTime) >= filterDate)
})

const historySummary = computed(() => {
  const trades = filteredHistory.value
  const totalTrades = trades.length
  const winningTrades = trades.filter(t => t.pnl > 0).length
  const losingTrades = trades.filter(t => t.pnl < 0).length
  const totalPnl = trades.reduce((sum, t) => sum + t.pnl, 0)
  
  return {
    totalTrades,
    winningTrades,
    losingTrades,
    totalPnl
  }
})

const formatCurrency = (value) => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR'
  }).format(value)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDuration = (minutes) => {
  if (minutes < 60) return `${minutes}min`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}h${mins > 0 ? mins + 'min' : ''}`
}

const refreshHistory = async () => {
  try {
    history.value = await fetchHistory()
  } catch (error) {
    console.error('Erreur lors du rafraîchissement de l\'historique:', error)
  }
}

onMounted(() => {
  refreshHistory()
})
</script>