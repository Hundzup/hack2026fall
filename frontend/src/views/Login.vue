<template>
  <div class="login-wrapper">
    <div class="login-card">
      
      <!-- Левая панель -->
      <div class="left-panel">
        <div class="header">
          <h1>{{ t.title }}</h1>
          <p class="subtitle">{{ t.subtitle }}</p>
        </div>
        
        <div class="left-footer">
          <!-- Текстовый логотип -->
          <div class="logo-box">
            <span class="logo-letter">é</span>
          </div>
          
            <div class="lang-switch">
            <button 
                class="lang-btn" 
                :class="{ active: currentLang === 'ru' }"
                @click="setLang('ru')"
                title="Русский"
                >
                <img src="/ru.svg" alt="RU" class="flag-icon" />
                Русский
            </button>
            <button 
                class="lang-btn" 
                :class="{ active: currentLang === 'en' }"
                @click="setLang('en')"
                title="English"
            >
                <img src="/gb.svg" alt="GB" class="flag-icon" />
                English
            </button>
            </div>
        </div>
      </div>

      <!-- Правая панель -->
      <div class="right-panel">
        <div class="form-container">
          <form @submit.prevent="handleLogin" class="login-form">
            <!-- Добавлено поле логина и пароля -->
            <input 
              v-model="username" 
              type="text" 
              :placeholder="t.loginPlaceholder" 
              required 
              class="form-input"
            />
            <input 
              v-model="password" 
              type="password" 
              :placeholder="t.passwordPlaceholder" 
              required 
              class="form-input"
            />
            <button type="submit" class="submit-btn">{{ t.submitBtn }}</button>
          </form>
        </div>
        
        <div class="right-footer">
          <div class="forgot-password">
            <a href="#">{{ t.forgotPassword }}</a>
          </div>
          
          <div class="divider"></div>
          
          <div class="oauth-links">
            <a href="#" class="oauth-link">
              <span>yandex</span>
              <span class="oauth-icon">Я</span>
            </a>
            <a href="#" class="oauth-link">
              <span>telegram</span>
              <span class="oauth-icon">✈</span>
            </a>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api'


const username = ref('')
const password = ref('')
const router = useRouter()


const currentLang = ref('ru') // Язык по умолчанию - русский


const messages = {
  ru: {
    title: 'Вход в aéza',
    subtitle: 'введите логин и пароль для входа',
    loginPlaceholder: 'Логин',
    passwordPlaceholder: 'Пароль',
    submitBtn: 'войти',
    forgotPassword: 'забыли пароль?'
  },
  en: {
    title: 'Login to aéza',
    subtitle: 'enter login and password to sign in',
    loginPlaceholder: 'Login',
    passwordPlaceholder: 'Password',
    submitBtn: 'sign in',
    forgotPassword: 'forgot password?'
  }
}


const t = computed(() => messages[currentLang.value])


const setLang = (lang) => {
  currentLang.value = lang
}

// ── Отправка формы ──
const handleLogin = async () => {
  try {

    const res = await login(username.value, password.value)
    localStorage.setItem('token', res.token)
    router.push('/')
  } catch (e) {

    alert(currentLang.value === 'ru' ? 'Неверный логин или пароль' : 'Invalid login or password')
  }
}
</script>

<style scoped>

.login-wrapper {
  min-height: 100vh;
  background-color: #000000;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  padding: 20px;
}


.login-card {
  display: flex;
  width: 100%;
  max-width: 800px;
  height: 500px;
  position: relative;
}


.left-panel {
  flex: 1;
  background-color: #141414;
  border-radius: 24px;
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  z-index: 2;
  box-shadow: 4px 0 24px rgba(0,0,0,0.5);
}

.header h1 {
  color: #ffffff;
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 12px 0;
  letter-spacing: -0.5px;
  transition: all 0.3s ease;
}

.subtitle {
  color: #888888;
  font-size: 15px;
  line-height: 1.5;
  margin: 0;
  transition: all 0.3s ease;
}

.left-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

/* Логотип */
.logo-box {
  width: 44px;
  height: 44px;
  background-color: #ffffff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-letter {
  color: #000000;
  font-size: 32px;
  font-weight: 900;
  margin-top: -4px;
  line-height: 1;
}


.lang-switch {
  display: flex;
  background-color: #222222;
  border-radius: 20px;
  padding: 4px;
}

.lang-btn {
  background: transparent;
  border: none;
  color: #888888;
  font-size: 13px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.lang-btn:hover {
  color: #cccccc;
}

.lang-btn.active {
  color: #ffffff;
  background-color: #333333;
}

.flag {
  font-size: 16px;
}


.right-panel {
  flex: 1;
  background-color: #1c1c1c;
  border-radius: 24px;
  padding: 40px;
  margin-left: -24px; 
  padding-left: 48px; 
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  z-index: 1;
}

.form-container {
  margin-top: 10px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-input {
  background-color: #262626;
  border: 1px solid transparent;
  color: #ffffff;
  font-size: 16px;
  padding: 16px 20px;
  border-radius: 12px;
  outline: none;
  transition: all 0.2s;
}

.form-input::placeholder {
  color: #666666;
}

.form-input:focus {
  border-color: #444444;
  background-color: #2a2a2a;
}

.submit-btn {
  background-color: #888888;
  color: #000000;
  border: none;
  font-size: 16px;
  font-weight: 600;
  padding: 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 8px;
}

.submit-btn:hover {
  background-color: #999999;
}

.right-footer {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.forgot-password {
  margin-bottom: 8px;
}

.forgot-password a {
  color: #666666;
  font-size: 14px;
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-password a:hover {
  color: #999999;
}

.divider {
  height: 1px;
  background-color: #2a2a2a;
  width: 100%;
}

.oauth-links {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.oauth-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #888888;
  text-decoration: none;
  font-size: 15px;
  transition: color 0.2s;
}

.oauth-link:hover {
  color: #ffffff;
}

.oauth-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background-color: #333333;
  border-radius: 50%;
  font-size: 12px;
  color: #ffffff;
}


@media (max-width: 600px) {
  .login-card {
    flex-direction: column;
    height: auto;
  }
  .left-panel {
    border-radius: 24px 24px 0 0;
    padding-bottom: 24px;
  }
  .right-panel {
    margin-left: 0;
    padding-left: 40px;
    border-radius: 0 0 24px 24px;
    margin-top: -24px;
    padding-top: 48px;
  }
}

.flag-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  object-fit: cover;
  display: block;

  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1); 
}


.lang-btn {
  padding: 6px 12px; 
}

.lang-switch {
  gap: 8px; 
  padding: 4px;
  background-color: #222222;
}
</style>
