import { createRouter, createWebHistory } from 'vue-router'
import Login from './views/Login.vue'
import Dashboard from './views/Dashboard.vue'
import Settings from './views/Settings.vue'

const routes = [
  { 
    path: '/login', 
    component: Login,
    meta: { title: 'Вход — Aeza' } 
  },
  { 
    path: '/', 
    component: Dashboard, 
    meta: { title: 'Дашборд — Aeza', requiresAuth: true } 
  },
  { 
    path: '/settings', 
    component: Settings, 
    meta: { title: 'Настройки — Aeza', requiresAuth: true } 
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuth = localStorage.getItem('token')
  if (to.meta.requiresAuth && !isAuth) next('/login')
  else if (to.path === '/login' && isAuth) next('/')
  else next()
})

router.afterEach((to, from) => {
  const defaultTitle = 'Aeza | Панель рисков'
  document.title = to.meta.title || defaultTitle
})

export default router