<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900">Statistiques</h2>
      <button @click="refreshStats" class="btn-primary">
        <ArrowPathIcon class="w-4 h-4 mr-2" />
        Actualiser
      </button>
    </div>

    <!-- Global Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="card">
        <div class="text-center">
          <div class="text-3xl font-bold text-primary-600">{{ globalStats.winRate }}%</div>
          <div class="text-sm text-gray-500 mt-1">Win Rate Global</div>
        </div>
      </div>
      
      <div class="card">
        <div class="text-center">
          <div class="text-3xl font-bold text-green-600">{{ globalStats.avgRR }}</div>
          <div class="text-sm text-gray-500 mt-1">Risk/Reward Moyen</div>
        </div>
      </div>
      
      <div class="card">
        <div class="text-center">
          <div class="text-3xl font-bold text-blue-600">{{ globalStats.totalSignals }}</div>
          <div class="text-sm text-gray-500 mt-1">Signaux Traités</div>
        </div>
      </div>
    </div>

    <!-- Channel Comparison -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Canal 1 Stats -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">📡 Canal 1</h3>
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Signaux traités</span>
            <span class="font-medium">{{ channelStats.channel1.totalSignals }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Win Rate</span>
            <span class="font-medium" :class="channelStats.channel1.winRate >= 50 ? 'text-green-600' : 'text-red-600'">
              {{ channelStats.channel1.winRate }}%
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Risk/Reward Moyen</span>
            <span class="font-medium text-blue-600">{{ channelStats.channel1.avgRR }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">P&L Total</span>
            <span class="font-medium" :class="channelStats.channel1.totalPnl >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ formatCurrency(channelStats.channel1.totalPnl) }}
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Meilleur Trade</span>
            <span class="font-medium text-green-600">{{ formatCurrency(channelStats.channel1.bestTrade) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Pire Trade</span>
            <span class="font-medium text-red-600">{{ formatCurrency(channelStats.channel1.worstTrade) }}</span>
          </div>
        </div>
      </div>

      <!-- Canal 2 Stats -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">📡 Canal 2</h3>
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Signaux traités</span>
            <span class="font-medium">{{ channelStats.channel2.totalSignals }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Win Rate</span>
            <span class="font-medium" :class="channelStats.channel2.winRate >= 50 ? 'text-green-600' : 'text-red-600'">
              {{ channelStats.channel2.winRate }}%
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Risk/Reward Moyen</span>
            <span class="font-medium text-blue-600">{{ channelStats.channel2.avgRR }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">P&L Total</span>
            <span class="font-medium" :class="channelStats.channel2.totalPnl >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ formatCurrency(channelStats.channel2.totalPnl) }}
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Meilleur Trade</span>
            <span class="font-medium text-green-600">{{ formatCurrency(channelStats.channel2.bestTrade) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Pire Trade</span>
            <span class="font-medium text-red-600">{{ formatCurrency(channelStats.channel2.worstTrade) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Chart -->
    <div class="card">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Performance par Symbole</h3>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbole</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trades</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Win Rate</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RR Moyen</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P&L Total</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="symbol in symbolStats" :key="symbol.symbol" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ symbol.symbol }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ symbol.totalTrades }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm" :class="symbol.winRate >= 50 ? 'text-green-600' : 'text-red-600'">
                {{ symbol.winRate }}%
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-blue-600">{{ symbol.avgRR }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium" :class="symbol.totalPnl >= 0 ? 'text-green-600' : 'text-red-600'">
                {{ formatCurrency(symbol.totalPnl) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ArrowPathIcon } from '@heroicons/vue/24/outline'
import { useApi } from '../composables/useApi'

const { fetchStatistics } = useApi()

const globalStats = ref({
  winRate: 0,
  avgRR: 0,
  totalSignals: 0
})

const channelStats = ref({
  channel1: {
    totalSignals: 0,
    winRate: 0,
    avgRR: 0,
    totalPnl: 0,
    bestTrade: 0,
    worstTrade: 0
  },
  channel2: {
    totalSignals: 0,
    winRate: 0,
    avgRR: 0,
    totalPnl: 0,
    bestTrade: 0,
    worstTrade: 0
  }
})

const symbolStats = ref([])

const formatCurrency = (value) => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR'
  }).format(value)
}

const refreshStats = async () => {
  try {
    const stats = await fetchStatistics()
    globalStats.value = stats.global
    channelStats.value = stats.channels
    symbolStats.value = stats.symbols
  } catch (error) {
    console.error('Erreur lors du rafraîchissement des statistiques:', error)
  }
}

onMounted(() => {
  refreshStats()
})
</script>