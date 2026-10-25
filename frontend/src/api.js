// Весь калл заменить на реальный запросы

export const login = async (username, password) => {

  if (username === 'admin' && password === 'admin') return { token: 'fake-jwt-token' }
  throw new Error('Unauthorized')
}

export const fetchClients = async () => {
  // данные клиентов
  return [
    { id: 1, email: 'a@a.com', balance: 15000, total_deposits: 50000, score: 85, risk_level: 'high', risk_reason: 'Частые снятия' },
    { id: 2, email: 'b@b.com', balance: 2000, total_deposits: 5000, score: 20, risk_level: 'low', risk_reason: 'Стабильный доход' },
    { id: 3, email: 'c@c.com', balance: 100000, total_deposits: 120000, score: 55, risk_level: 'medium', risk_reason: 'Снижение активности' },
    { id: 4, email: 'd@d.com', balance: 0, total_deposits: 0, score: null, risk_level: null, risk_reason: 'Недостаточно данных' },
  ]
}

export const fetchMetrics = async () => {
  // Заглушка: агрегированные данные и денежные потери
  return {
    potential_loss: 152000,
    total_clients: 4,
    risk_distribution: { high: 1, medium: 1, low: 1, unknown: 1 }
  }
}

export const fetchSettings = async () => {
  // коэффициенты
  return [
    { key: 'coef_balance', label: 'Отключено автопродление', value: 0.3 },
    { key: 'coef_deposits', label: 'Близко истекает услуга', value: 0.7 },
    { key: 'coef_activity', label: 'Услуга ждёт оплаты', value: 0.1 },
    { key: 'coef_deposits', label: 'Не хватает средств', value: 0.7 },
    { key: 'coef_activity', label: 'История неоплаченных продлений', value: 0.1 },
    { key: 'coef_deposits', label: 'Низкие пополнения', value: 0.7 }
  ]
}

export const saveSettings = async (settings) => {
  // сохранения
  console.log('Сохранено на бэкенд:', settings)
  return { success: true }
}