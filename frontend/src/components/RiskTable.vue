<template>
  <div class="table-container">
    <table>
      <thead>
        <tr>
          <th @click="sort('id')">ID <span class="sort-icon">{{ getSortIcon('id') }}</span></th>
          <th @click="sort('email')">Email <span class="sort-icon">{{ getSortIcon('email') }}</span></th>
          <th @click="sort('balance')">Баланс <span class="sort-icon">{{ getSortIcon('balance') }}</span></th>
          <th @click="sort('total_deposits')">Пополнения <span class="sort-icon">{{ getSortIcon('total_deposits') }}</span></th>
          <th @click="sort('score')">Risk-score <span class="sort-icon">{{ getSortIcon('score') }}</span></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="client in sortedClients" :key="client.id">
          <td><span class="text-muted">#</span>{{ client.id }}</td>
          <td class="email-col">{{ client.email }}</td>
          <td>{{ client.balance.toLocaleString() }} ₽</td>
          <td>{{ client.total_deposits.toLocaleString() }} ₽</td>
          <td>
            <span v-if="client.score !== null" class="score-cell">{{ client.score }}</span>
            <span v-else class="text-muted">Нет данных</span>
          </td>
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
const sortOrder = ref('desc')

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

    if (valA === null) return 1;
    if (valB === null) return -1;

    if (valA < valB) return sortOrder.value === 'asc' ? -1 : 1
    if (valA > valB) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
})
</script>

<style scoped>
.table-container {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

th, td {
  padding: 16px 12px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}

th {
  color: #888;
  font-weight: 500;
  cursor: pointer;
  user-select: none;
  transition: color 0.2s;
}

th:hover {
  color: #111;
}

.sort-icon {
  font-size: 12px;
  margin-left: 4px;
  color: #ccc;
}

tbody tr {
  transition: background 0.2s;
}

tbody tr:hover {
  background-color: #fafafa;
}

td {
  color: #333;
}

.text-muted {
  color: #999;
}

.email-col {
  font-weight: 500;
  color: #111;
}

.score-cell {
  font-weight: 600;
  background: #eef5f7;
  padding: 4px 10px;
  border-radius: 6px;
  color: #111;
}
</style>