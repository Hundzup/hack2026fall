<template>
  <div class="settings">
    <header>
      <h1>Настройка модели ISK-score</h1>
      <nav>
        <router-link to="/">Дашборд</router-link> |
        <router-link to="/settings">Настройки</router-link>
      </nav>
    </header>

    <div class="form-group">
      <div v-for="coef in coefficients" :key="coef.key" class="coef-row">
        <label>{{ coef.label }}</label>
        <input v-model.number="coef.value" type="number" step="0.1" />
      </div>
      
      <button @click="save" :disabled="saving">
        {{ saving ? 'Сохранение...' : 'Сохранить коэффициенты' }}
      </button>
      <p v-if="message" class="success">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchSettings, saveSettings } from '../api'

const coefficients = ref([])
const saving = ref(false)
const message = ref('')

onMounted(async () => {
  coefficients.value = await fetchSettings()
})

const save = async () => {
  saving.value = true
  message.value = ''
  try {
    await saveSettings(coefficients.value)
    message.value = 'Коэффициенты успешно сохранены!'
  } catch (e) {
    message.value = 'Ошибка сохранения'
  } finally {
    saving.value = false
    setTimeout(() => message.value = '', 3000)
  }
}
</script>

<style scoped>
.settings { max-width: 600px; margin: 0 auto; padding: 20px; font-family: sans-serif; }
header { margin-bottom: 30px; }
.form-group { display: flex; flex-direction: column; gap: 15px; background: #f5f6fa; padding: 20px; border-radius: 8px; }
.coef-row { display: flex; justify-content: space-between; align-items: center; }
input { padding: 8px; width: 100px; border: 1px solid #ccc; border-radius: 4px; }
button { padding: 10px; background: #0984e3; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
button:disabled { background: #b2bec3; }
.success { color: green; margin-top: 10px; }
</style>