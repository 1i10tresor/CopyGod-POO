<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900">Ordres</h2>
      <div class="flex space-x-3">
        <select v-model="statusFilter" class="rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500">
          <option value="">Tous les statuts</option>
          <option value="OPEN">Ouvert</option>
          <option value="PENDING">En attente</option>
          <option value="CLOSED">Fermé</option>
        </select>
        <button @click="refreshOrders" class="btn-primary">
          <ArrowPathIcon class="w-4 h-4 mr-2" />
          Actualiser
        </button>
      </div>
    </div>

    <!-- Orders Table -->
    <div class="card">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Signal</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbole</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Volume</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prix d'entrée</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SL</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">TP</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P&L</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="order in filteredOrders" :key="order.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">{{ order.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    Canal {{ order.channelId }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ order.symbol }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="order.type === 'BUY' ? 'text-green-600' : 'text-red-600'" class="text-sm font-medium">
                  {{ order.type }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ order.volume }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ order.entryPrice }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ order.sl }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ order.tp }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="`status-badge status-${order.status.toLowerCase()}`">
                  {{ order.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium" :class="order.pnl >= 0 ? 'text-green-600' : 'text-red-600'">
                {{ formatCurrency(order.pnl) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button 
                  v-if="order.status === 'OPEN' || order.status === 'PENDING'"
                  @click="closeOrder(order.id)"
                  class="text-red-600 hover:text-red-900"
                >
                  Fermer
                </button>
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
import { ArrowPathIcon } from '@heroicons/vue/24/outline'
import { useApi } from '../composables/useApi'

const { fetchOrders, closeOrder: apiCloseOrder } = useApi()

const orders = ref([])
const statusFilter = ref('')

const filteredOrders = computed(() => {
  if (!statusFilter.value) return orders.value
  return orders.value.filter(order => order.status === statusFilter.value)
})

const formatCurrency = (value) => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR'
  }).format(value)
}

const refreshOrders = async () => {
  try {
    orders.value = await fetchOrders()
  } catch (error) {
    console.error('Erreur lors du rafraîchissement des ordres:', error)
  }
}

const closeOrder = async (orderId) => {
  if (confirm('Êtes-vous sûr de vouloir fermer cet ordre ?')) {
    try {
      await apiCloseOrder(orderId)
      await refreshOrders()
    } catch (error) {
      console.error('Erreur lors de la fermeture de l\'ordre:', error)
    }
  }
}

onMounted(() => {
  refreshOrders()
})
</script>