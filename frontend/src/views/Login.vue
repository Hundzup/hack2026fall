<template>
  <div class="login-container">
    <h2>Вход в систему</h2>
    <form @submit.prevent="handleLogin">
      <input v-model="username" placeholder="Логин" required />
      <input v-model="password" type="password" placeholder="Пароль" required />
      <button type="submit">Войти</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api'

const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

const handleLogin = async () => {
  try {
    const res = await login(username.value, password.value)
    localStorage.setItem('token', res.token)
    router.push('/')
  } catch (e) {
    error.value = 'Неверный логин или пароль'
  }
}
</script>

<style scoped>
.login-container { max-width: 300px; margin: 100px auto; display: flex; flex-direction: column; gap: 10px; }
input, button { padding: 10px; font-size: 16px; }
.error { color: red; }
</style>