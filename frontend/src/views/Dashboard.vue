<template>
  <div class="dashboard">
    <header>
      <h1>Панель рисков</h1>
      <nav>
        <router-link to="/">Дашборд</router-link> |
        <router-link to="/settings">Настройки</router-link> |
        <a href="/metrics" target="_blank">Метрики Prometheus</a> |
        <button @click="logout">Выйти</button>
      </nav>
    </header>

    
    <section class="money-panel">
      <h2>Потенциальные потери бизнеса</h2>
      <p class="money-value">{{ metrics.potential_loss?.toLocaleString() }} ₽</p>
      <p><small>С учетом балансов, стоимости услуг и уровня риска</small></p>
    </section>

    
    <section class="clients-grid">
      <h2>Оценка клиентов</h2>
      <div class="grid">
        <div v-for="client in clients" :key="client.id" class="card" :class="client.risk_level">
          <h3>{{ client.email }}</h3>
          
          
          <div v-if="client.score === null" class="no-data">
            Оценка отсутствует (недостаточно данных)
          </div>
          
          <div v-else>
            <p><b>ISK-score:</b> {{ client.score }}</p>
            <p><b>Риск:</b> {{ translateRisk(client.risk_level) }}</p>
            <p><b>Причина:</b> {{ client.risk_reason }}</p>
            
            
            <div class="loyalty-bar">
              <span>Лояльность:</span>
              <div class="bar-bg">
                <div class="bar-fill" :style="{ width: (100 - client.score) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    
    <section>
      <h2>Топ клиентов под риском</h2>
      <RiskTable :clients="clients" />
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchClients, fetchMetrics } from '../api'
import RiskTable from '../components/RiskTable.vue'

const clients = ref([])
const metrics = ref({})
const router = useRouter()
let intervalId = null

const loadData = async () => {
  clients.value = await fetchClients()
  metrics.value = await fetchMetrics()
}

const translateRisk = (level) => {
  const map = { high: 'Высокий', medium: 'Средний', low: 'Низкий' }
  return map[level] || level
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

onMounted(() => {
  loadData()
  
  intervalId = setInterval(loadData, 1000)
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
})
</script>

<style scoped>
.dashboard { padding: 20px; font-family: sans-serif; max-width: 1200px; margin: 0 auto; }
header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.money-panel { background: #ffeaa7; padding: 20px; border-radius: 8px; margin-bottom: 30px; text-align: center; }
.money-value { font-size: 32px; font-weight: bold; margin: 10px 0; color: #d63031; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }
.card { padding: 15px; border-radius: 8px; border: 1px solid #ddd; background: #fff; }
.card.high { border-left: 5px solid #d63031; }
.card.medium { border-left: 5px solid #fdcb6e; }
.card.low { border-left: 5px solid #00b894; }
.no-data { color: #636e72; font-style: italic; margin-top: 10px; }
.loyalty-bar { margin-top: 15px; font-size: 12px; }
.bar-bg { background: #dfe6e9; height: 10px; border-radius: 5px; overflow: hidden; margin-top: 5px; }
.bar-fill { background: #0984e3; height: 100%; transition: width 0.3s; }
</style>