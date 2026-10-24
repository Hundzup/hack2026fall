<template>
  <!-- Убрали padding у главного контейнера, чтобы шапка была на всю ширину -->
  <div class="dashboard-page">
    
    <!-- Верхняя панель (теперь sticky и на всю ширину) -->
    <header class="top-navbar" :class="{ 'is-scrolled': isScrolled }">
      <!-- Внутренний контейнер для ограничения ширины контента -->
      <div class="nav-container">
        <nav class="nav-links">
          <router-link to="/" class="nav-item">{{ t.navDashboard }}</router-link>
          <router-link to="/settings" class="nav-item">{{ t.navSettings }}</router-link>
          <a href="/metrics" target="_blank" class="nav-item">{{ t.navMetrics }}</a>
        </nav>

        <div class="logo-container">
          <div class="logo-box">
            <span class="logo-letter">é</span>
          </div>
        </div>

        <div class="nav-actions">
          
          <!-- Меню языков (открывается по наведению) -->
          <div 
            class="lang-selector" 
            @mouseenter="isLangMenuOpen = true" 
            @mouseleave="isLangMenuOpen = false"
          >
            <button class="icon-btn" :class="{ 'active': isLangMenuOpen }" title="Язык">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="2" y1="12" x2="22" y2="12"></line>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
              </svg>
            </button>

            <!-- Выпадающее меню -->
            <div v-if="isLangMenuOpen" class="lang-dropdown">
              <button class="lang-option" @click="setLang('en')">
                <div class="lang-info">
                  <img src="/gb.svg" alt="English" class="lang-flag" />
                  <span>English</span>
                </div>
                <svg v-if="currentLang === 'en'" class="check-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00b894" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </button>

              <button class="lang-option" @click="setLang('ru')">
                <div class="lang-info">
                  <img src="/ru.svg" alt="Русский" class="lang-flag" />
                  <span>Русский</span>
                </div>
                <svg v-if="currentLang === 'ru'" class="check-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00b894" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </button>
            </div>
          </div>

          <button class="logout-btn" @click="logout">{{ t.navLogout }}</button>
        </div>
      </div>
    </header>

    <!-- Контентная часть (с отступами) -->
    <main class="content">
      
      <!-- Денежная панель -->
      <section class="money-panel">
        <p class="money-title">{{ t.moneyTitle }}</p>
        <h2 class="money-value">{{ metrics.potential_loss?.toLocaleString() }} ₽</h2>
        <p class="money-subtitle">{{ t.moneySubtitle }}</p>
      </section>

      <!-- Оценка клиентов -->
      <section class="clients-section">
        <h2>{{ t.clientsTitle }}</h2>
        <div class="grid">
          <div v-for="client in clients" :key="client.id" class="client-card">
            <div class="card-header">
              <h3>{{ client.email }}</h3>
              <span 
                v-if="client.risk_level" 
                class="risk-badge" 
                :class="client.risk_level"
              >
                {{ translateRisk(client.risk_level) }}
              </span>
            </div>
            
            <div v-if="client.score === null" class="no-data">
              {{ t.noData }}
            </div>
            
            <div v-else class="card-body">
              <div class="score-row">
                <span class="score-label">{{ t.scoreLabel }}</span>
                <span class="score-value">{{ client.score }}</span>
              </div>
              <p class="risk-reason"><b>{{ t.reason }}</b> {{ client.risk_reason }}</p>
              
              <div class="loyalty-bar">
                <div class="loyalty-labels">
                  <span>{{ t.loyalty }}</span>
                  <span>{{ 100 - client.score }}%</span>
                </div>
                <div class="bar-bg">
                  <div class="bar-fill" :style="{ width: (100 - client.score) + '%' }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Таблица под риском -->
      <section class="table-section">
        <h2>{{ t.topClients }}</h2>
        <RiskTable :clients="clients" />
      </section>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchClients, fetchMetrics } from '../api'
import RiskTable from '../components/RiskTable.vue'

const clients = ref([])
const metrics = ref({})
const router = useRouter()
let intervalId = null

// ── Логика скролла для шапки ──
const isScrolled = ref(false)
const handleScroll = () => {
  isScrolled.value = window.scrollY > 10
}

// ── Логика перевода (Всё внутри файла) ──
const currentLang = ref('ru')
const isLangMenuOpen = ref(false)

const messages = {
  ru: {
    navDashboard: 'Дашборд',
    navSettings: 'Настройки',
    navMetrics: 'Метрики',
    navLogout: 'Выйти',
    
    moneyTitle: 'Потенциальные потери бизнеса',
    moneySubtitle: 'С учетом балансов, стоимости услуг и уровня риска',
    clientsTitle: 'Оценка клиентов',
    noData: 'Оценка отсутствует (недостаточно данных)',
    scoreLabel: 'Risk-score:',
    reason: 'Причина:',
    loyalty: 'Лояльность',
    topClients: 'Топ клиентов под риском',
    
    riskHigh: 'Высокий',
    riskMedium: 'Средний',
    riskLow: 'Низкий'
  },
  en: {
    navDashboard: 'Dashboard',
    navSettings: 'Settings',
    navMetrics: 'Metrics',
    navLogout: 'Logout',
    
    moneyTitle: 'Potential business losses',
    moneySubtitle: 'Taking into account balances, service costs and risk level',
    clientsTitle: 'Client Assessment',
    noData: 'No assessment (insufficient data)',
    scoreLabel: 'Risk-score:',
    reason: 'Reason:',
    loyalty: 'Loyalty',
    topClients: 'Top clients at risk',
    
    riskHigh: 'High',
    riskMedium: 'Medium',
    riskLow: 'Low'
  }
}

const t = computed(() => messages[currentLang.value])

const setLang = (lang) => {
  currentLang.value = lang
}

// ── Загрузка данных ──
const loadData = async () => {
  clients.value = await fetchClients()
  metrics.value = await fetchMetrics()
}

// ── Функция перевода риска ──
const translateRisk = (level) => {
  const map = {
    high: t.value.riskHigh,
    medium: t.value.riskMedium,
    low: t.value.riskLow
  }
  return map[level] || level
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

onMounted(() => {
  loadData()
  intervalId = setInterval(loadData, 1000)
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* ── Общий фон страницы ── */
.dashboard-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #eef5f7 0%, #f8f9fa 100%);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  color: #111;
}

/* ── Верхняя панель (Sticky) ── */
.top-navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  width: 100%;
  background-color: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid transparent;
  transition: all 0.3s ease;
}

.top-navbar.is-scrolled {
  background-color: rgba(255, 255, 255, 0.85);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-links {
  display: flex;
  gap: 8px;
  flex: 1;
}

.nav-item {
  text-decoration: none;
  color: #555;
  font-size: 15px;
  font-weight: 500;
  padding: 10px 20px;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
  color: #000;
}

.nav-item.router-link-active {
  background-color: #e5e7eb;
  color: #111;
}

.logo-container {
  flex: 1;
  display: flex;
  justify-content: center;
}

.logo-box {
  width: 40px;
  height: 40px;
  background-color: #ffffff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 2px 2px 0px #b3b3b3;
  border: 1px solid #e0e0e0;
}

.logo-letter {
  color: #000000;
  font-size: 28px;
  font-weight: 900;
  margin-top: -3px;
  line-height: 1;
}

.nav-actions {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16px;
}

/* ── Кнопка планеты и меню языков ── */
.icon-btn {
  background: transparent;
  border: none;
  color: #555;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border-radius: 50%;
  transition: background 0.2s, color 0.2s;
}

.icon-btn:hover, .icon-btn.active {
  background-color: rgba(0, 0, 0, 0.06);
  color: #000;
}

.lang-selector {
  position: relative;
  padding-bottom: 8px;
  margin-bottom: -8px; 
}

.lang-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 180px;
  background-color: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08), 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.04);
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  z-index: 200;
  animation: fadeIn 0.2s ease;
}

/* Мостик, чтобы меню не закрывалось при наведении */
.lang-dropdown::before {
  content: '';
  position: absolute;
  top: -10px;
  left: 0;
  right: 0;
  height: 10px;
  background: transparent;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

.lang-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  background: transparent;
  border: none;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
  color: #333;
  font-size: 15px;
  font-weight: 500;
}

.lang-option:hover {
  background-color: #f5f5f5;
}

.lang-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.lang-flag {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.08);
}

.check-icon {
  color: #00b894;
}

.logout-btn {
  background-color: #111111;
  color: #ffffff;
  border: none;
  padding: 10px 24px;
  border-radius: 20px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.logout-btn:hover {
  background-color: #333333;
}

/* ── Контент ── */
.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

h2 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #111;
}

/* ── Денежная панель ── */
.money-panel {
  background-color: #ffffff;
  border-radius: 24px;
  padding: 32px;
  text-align: center;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.02);
  margin-bottom: 40px;
}

.money-title {
  color: #666;
  font-size: 15px;
  margin-bottom: 8px;
}

.money-value {
  font-size: 42px;
  font-weight: 800;
  color: #d63031;
  margin: 0 0 8px 0;
  letter-spacing: -1px;
}

.money-subtitle {
  color: #999;
  font-size: 13px;
}

/* ── Карточки клиентов ── */
.clients-section {
  margin-bottom: 40px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.client-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  border: 1px solid #f0f0f0;
  transition: transform 0.2s;
}

.client-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #111;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.risk-badge {
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.risk-badge.high { background: #ffe3e3; color: #d63031; }
.risk-badge.medium { background: #fff3cd; color: #d35400; }
.risk-badge.low { background: #d4edda; color: #00b894; }

.no-data {
  color: #999;
  font-size: 14px;
  font-style: italic;
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
}

.score-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
}

.score-label {
  font-size: 14px;
  color: #666;
}

.score-value {
  font-size: 24px;
  font-weight: 700;
  color: #111;
}

.risk-reason {
  font-size: 13px;
  color: #666;
  margin-bottom: 16px;
}

.loyalty-bar {
  font-size: 12px;
}

.loyalty-labels {
  display: flex;
  justify-content: space-between;
  color: #888;
  margin-bottom: 6px;
}

.bar-bg {
  background: #f0f0f0;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  background: #111111;
  height: 100%;
  transition: width 0.3s ease;
}

/* ── Секция таблицы ── */
.table-section {
  background: #ffffff;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.02);
}
</style>