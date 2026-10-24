<template>
  <div class="table-container">
    <table>
      <thead>
        <tr>
          <th @click="sort('id')">ID {{ getSortIcon('id') }}</th>
          <th @click="sort('email')">Email {{ getSortIcon('email') }}</th>
          <th @click="sort('balance')">Баланс {{ getSortIcon('balance') }}</th>
          <th @click="sort('total_deposits')">Сумма пополнений {{ getSortIcon('total_deposits') }}</th>
          <th @click="sort('score')">ISK-Score {{ getSortIcon('score') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="client in sortedClients" :key="client.id">
          <td>{{ client.id }}</td>
          <td>{{ client.email }}</td>
          <td>{{ client.balance.toLocaleString() }} ₽</td>
          <td>{{ client.total_deposits.toLocaleString() }} ₽</td>
          <td>{{ client.score ?? 'Нет данных' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  clients: Array
})

const sortKey = ref('score')
const sortOrder = ref('desc') // 'asc' или 'desc'

const sort = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'desc'
  }
}

const getSortIcon = (key) => {
  if (sortKey.value !== key) return '↕'
  return sortOrder.value === 'asc' ? '↑' : '↓'
}

const sortedClients = computed(() => {
  return [...props.clients].sort((a, b) => {
    let valA = a[sortKey.value]
    let valB = b[sortKey.value]

    // Обработка null значений (например, отсутствие score)
    if (valA === null) return 1;
    if (valB === null) return -1;

    if (valA < valB) return sortOrder.value === 'asc' ? -1 : 1
    if (valA > valB) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
})
</script>

<style scoped>
.table-container { overflow-x: auto; margin-top: 15px; }
table { width: 100%; border-collapse: collapse; text-align: left; }
th, td { padding: 12px; border-bottom: 1px solid #ddd; }
th { cursor: pointer; background: #f5f6fa; user-select: none; }
th:hover { background: #dcdde1; }
</style>