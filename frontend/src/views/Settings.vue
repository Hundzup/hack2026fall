<template>
  <div class="settings-page">
    
    <header class="top-navbar" :class="{ 'is-scrolled': isScrolled }">
      <div class="nav-container">
    
        <nav class="nav-links">
          <router-link to="/" class="nav-item">{{ t.navDashboard }}</router-link>
          <router-link to="/settings" class="nav-item">{{ t.navSettings }}</router-link>
        </nav>

    
        <div class="logo-container">
          <div class="logo-box">
            <span class="logo-letter">é</span>
          </div>
        </div>

    
        <div class="nav-actions">
          
    
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

    
    <main class="content">
      <div class="settings-card">
        <h1>{{ t.settingsTitle }}</h1>
        <p class="subtitle">{{ t.settingsSubtitle }}</p>

        <div class="form-group">
          <div v-for="coef in coefficients" :key="coef.key" class="coef-row">
            <label>{{ coef.label }}</label>
            <input v-model.number="coef.value" type="number" step="0.1" />
          </div>
          
          <button class="save-btn" @click="save" :disabled="saving">
            {{ saving ? t.savingBtn : t.saveBtn }}
          </button>
          
          <!-- Вывод сообщения -->
          <p v-if="message" class="success-msg" :class="{ 'error': isError }">{{ message }}</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchSettings, saveSettings } from '../api'

// ── Состояние формы ──
const coefficients = ref([])
const saving = ref(false)
const message = ref('')
const isError = ref(false)
const router = useRouter()


const isScrolled = ref(false)
const handleScroll = () => {
  isScrolled.value = window.scrollY > 10
}


const currentLang = ref('ru') 
const isLangMenuOpen = ref(false) 

// Словари
const messages = {
  ru: {
    navDashboard: 'Дашборд',
    navSettings: 'Настройки',
    navLogout: 'Выйти',
    settingsTitle: 'Настройка модели Risk-score',
    settingsSubtitle: 'Изменения вступают в силу сразу после сохранения',
    saveBtn: 'Сохранить коэффициенты',
    savingBtn: 'Сохранение...',
    successMsg: 'Коэффициенты успешно сохранены!',
    errorMsg: 'Ошибка сохранения'
  },
  en: {
    navDashboard: 'Dashboard',
    navSettings: 'Settings',
    navLogout: 'Logout',
    settingsTitle: 'Risk-score Model Settings',
    settingsSubtitle: 'Changes take effect immediately after saving',
    saveBtn: 'Save coefficients',
    savingBtn: 'Saving...',
    successMsg: 'Coefficients saved successfully!',
    errorMsg: 'Save error'
  }
}

// Вычисляемый объект с текущим переводом
const t = computed(() => messages[currentLang.value])

// Функция смены языка
const setLang = (lang) => {
  currentLang.value = lang
}

onMounted(async () => {
  coefficients.value = await fetchSettings()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

// ── Сохранение формы ──
const save = async () => {
  saving.value = true
  message.value = ''
  isError.value = false
  try {
    await saveSettings(coefficients.value)
    message.value = t.value.successMsg // Берем перевод из текущего языка
  } catch (e) {
    message.value = t.value.errorMsg
    isError.value = true
  } finally {
    saving.value = false
    setTimeout(() => message.value = '', 3000)
  }
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>

.settings-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #eef5f7 0%, #f8f9fa 100%);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  color: #111;
}


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

/* Левая навигация */
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

/* Центральный логотип */
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

/* Правая часть с кнопками */
.nav-actions {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16px;
}

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

/* ── Выпадающее меню языков ── */
.lang-selector {
  position: relative;
  /* Отступы и отрицательный margin нужны, чтобы меню не закрывалось, когда ведешь мышку вниз */
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

/* Невидимый мостик, чтобы меню не закрывалось, когда ведешь мышку от планеты к списку */
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

/* ── Контентная часть ── */
.content {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 24px;
}

.settings-card {
  background-color: #ffffff;
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.02);
}

.settings-card h1 {
  margin: 0 0 8px;
  font-size: 24px;
  color: #111;
}

.subtitle {
  color: #777;
  font-size: 14px;
  margin-bottom: 32px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.coef-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.coef-row label {
  font-size: 15px;
  font-weight: 500;
  color: #333;
}

.coef-row input {
  padding: 10px 14px;
  width: 120px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.coef-row input:focus {
  border-color: #111;
}

.save-btn {
  margin-top: 10px;
  padding: 14px;
  background-color: #111111;
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: background 0.2s;
}

.save-btn:hover {
  background-color: #333333;
}

.save-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.success-msg {
  color: #00b894;
  background: #e6f8f3;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  font-size: 14px;
  margin-top: 10px;
}

/* Стиль для ошибки */
.success-msg.error {
  color: #d63031;
  background: #ffe3e3;
}
</style>