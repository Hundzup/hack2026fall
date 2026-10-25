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
            
            <!-- Обновленный блок с ползунком -->
            <div class="input-group">
              
              <div class="slider-container">
                <span class="edge-label">0</span>
                
                <div class="slider-wrapper">
                  <!-- Всплывающее облачко с числом -->
                  <div class="slider-bubble" :style="getBubbleStyle(coef.value)">
                    {{ Number(coef.value).toFixed(2) }}
                  </div>
                  
                  <input 
                    type="range" 
                    v-model.number="coef.value" 
                    min="0" 
                    max="1" 
                    step="0.01" 
                    class="slider"
                  />
                </div>
                
                <span class="edge-label">1</span>
              </div>

              <input 
                type="number" 
                v-model.number="coef.value" 
                min="0" 
                max="1" 
                step="0.01" 
                class="number-input"
                @blur="clampValue(coef)"
              />
            </div>
          </div>
          
          <button class="save-btn" @click="save" :disabled="saving">
            {{ saving ? t.savingBtn : t.saveBtn }}
          </button>
          
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

const t = computed(() => messages[currentLang.value])

const setLang = (lang) => {
  currentLang.value = lang
}

// Ограничение ручного ввода
const clampValue = (coef) => {
  if (coef.value === null || coef.value === '') {
    coef.value = 0;
  } else if (coef.value < 0) {
    coef.value = 0;
  } else if (coef.value > 1) {
    coef.value = 1;
  }
}

// Вычисление позиции для всплывающего облачка
const getBubbleStyle = (value) => {
  // Защита от пустых значений
  const val = value || 0;
  const percent = val * 100;
  // Ширина бегунка (кружочка) равна 18px. 
  // Нам нужно сместить облачко так, чтобы его центр совпадал с центром бегунка.
  const offset = 9 - (percent * 0.18); 
  return {
    left: `calc(${percent}% + ${offset}px)`
  };
}

onMounted(async () => {
  coefficients.value = await fetchSettings()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const save = async () => {
  saving.value = true
  message.value = ''
  isError.value = false
  try {
    await saveSettings(coefficients.value)
    message.value = t.value.successMsg
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
/* ... (Стили шапки остаются без изменений) ... */
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

.content {
  max-width: 1200px;
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
  padding-top: 20px; /* Добавили отступ сверху, чтобы облачко не обрезалось */
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
  width: 35%;
}

/* ── Стили для группы слайдера ── */
.input-group {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 65%;
  justify-content: flex-end;
}

/* Контейнер с нулем, ползунком и единицей */
.slider-container {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  max-width: 280px;
}

.edge-label {
  font-size: 12px;
  color: #888;
  font-weight: 500;
}

/* Обертка для самого ползунка */
.slider-wrapper {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

/* Всплывающее облачко с числом */
.slider-bubble {
  position: absolute;
  top: -28px;
  background-color: #111111;
  color: #ffffff;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 6px;
  transform: translateX(-50%);
  pointer-events: none; /* Чтобы облачко не мешало кликать по ползунку */
  transition: left 0.1s ease-out;
  white-space: nowrap;
}

/* Треугольник снизу облачка */
.slider-bubble::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 4px 4px 0;
  border-style: solid;
  border-color: #111111 transparent transparent transparent;
}

/* Сам ползунок */
.slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  outline: none;
  cursor: pointer;
  margin: 0;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #111111;
  cursor: pointer;
  transition: transform 0.1s;
}

.slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #111111;
  cursor: pointer;
  border: none;
}

.number-input {
  padding: 10px 14px;
  width: 80px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
  text-align: center;
}

.number-input:focus {
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

.success-msg.error {
  color: #d63031;
  background: #ffe3e3;
}
</style>