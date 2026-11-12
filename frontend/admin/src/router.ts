import { createRouter, createWebHistory } from 'vue-router'
import { navigationGroups } from './navigation'
import AdminLayout from './layouts/AdminLayout.vue'
import ModuleView from './ModuleView.vue'
import LoginView from './views/LoginView.vue'
import SystemView from './views/SystemView.vue'
import PasswordView from './views/PasswordView.vue'
import { useAdminAuth } from './stores/auth'
import { adminPinia } from './stores'

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/password', component: PasswordView },
    { path: '/login', name: 'admin-login', component: LoginView, meta: { public: true, title: '管理员登录' } },
    {
      path: '/', component: AdminLayout,
      children: [
        ...navigationGroups.flatMap(group => group.items.map(item => ({
          path: item.path.slice(1), component: ['/users','/roles','/logs','/settings'].includes(item.path)?SystemView:ModuleView, meta: { title: item.title },
        }))),
        { path: ':pathMatch(.*)*', component: ModuleView, meta: { title: '页面不存在', notFound: true } },
      ],
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async to => {
  const auth = useAdminAuth(adminPinia)
  try {
    await auth.refreshSession()
  } catch {
    if (to.meta.public) return true
    return { name: 'admin-login', query: { redirect: to.fullPath, reason: 'unavailable' } }
  }
  if (!auth.session && !to.meta.public) {
    return { name: 'admin-login', query: { redirect: to.fullPath } }
  }
  if (auth.session?.must_change_password && to.path !== '/password') return '/password'
  if (auth.session && to.name === 'admin-login') return '/'
  return true
})
