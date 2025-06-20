<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900">Dashboard</h2>
      <button @click="refreshData" class="btn-primary">
        <ArrowPathIcon class="w-4 h-4 mr-2" />
        Actualiser
      </button>
    </div>

    <!-- Account Summary -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <CurrencyEuroIcon class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Balance</p>
            <p class="text-2xl font-semibold text-gray-900">{{ formatCurrency(accountInfo.balance) }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <BanknotesIcon class="h-8 w-8 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Équité</p>
            <p class="text-2xl font-semibold text-gray-900">{{ formatCurrency(accountInfo.equity) }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ShieldCheckIcon class="h-8 w-8 text-purple-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Marge Libre</p>
            <p class="text-2xl font-semibold text-gray-900">{{ formatCurrency(accountInfo.freeMargin) }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ChartBarIcon class="h-8 w-8 text-orange-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Positions</p>
            <p class="text-2xl font-semibold text-gray-900">{{ openOrders.length }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Orders -->
    <div class="card">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-medium text-gray-900">Ordres Récents</h3>
        <router-link to="/orders" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
          Voir tout →
        </router-link>
      </div>
      
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbole</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Volume</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prix</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P&L</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="order in recentOrders" :key="order.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ order.symbol }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="order.type === 'BUY' ? 'text-green-600' : 'text-red-600'" class="text-sm font-medium">
                  {{ order.type }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ order.volume }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ order.price }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="`status-badge status-${order.status.toLowerCase()}`">
                  {{ order.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm" :class="order.pnl >= 0 ? 'text-green-600' : 'text-red-600'">
                {{ formatCurrency(order.pnl) }}
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
import { 
  ArrowPathIcon, 
  CurrencyEuroIcon, 
  BanknotesIcon, 
  ShieldCheckIcon, 
  ChartBarIcon 
} from '@heroicons/vue/24/outline'
import { useApi } from '../composables/useApi'

const { fetchAccountInfo, fetchOrders } = useApi()

const accountInfo = ref({
  balance: 0,
  equity: 0,
  freeMargin: 0
})

const openOrders = ref([])
const recentOrders = ref([])

const formatCurrency = (value) => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR'
  }).format(value)
}

const refreshData = async () => {
  try {
    const [account, orders] = await Promise.all([
      fetchAccountInfo(),
      fetchOrders()
    ])
    
    accountInfo.value = account
    openOrders.value = orders.filter(o => o.status === 'OPEN')
    recentOrders.value = orders.slice(0, 5)
  } catch (error) {
    console.error('Erreur lors du rafraîchissement:', error)
  }
}

onMounted(() => {
  refreshData()
  // Actualisation automatique toutes les 30 secondes
  setInterval(refreshData, 30000)
})
</script>