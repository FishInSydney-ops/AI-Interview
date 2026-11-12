import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './HomeView.vue'
import LoginView from './views/LoginView.vue'
import ModuleView from './ModuleView.vue'

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: HomeView },
    { path: '/login', component: LoginView, meta: { standalone: true, title: '学员登录' } },
    { path: '/routes', component: ModuleView, meta: { title: '学习路线' } },
    { path: '/questions', component: ModuleView, meta: { title: '题库中心' } },
    { path: '/mistakes', component: ModuleView, meta: { title: '错题本' } },
    { path: '/interview', component: ModuleView, meta: { title: 'AI 面试' } },
    { path: '/:pathMatch(.*)*', component: ModuleView, meta: { title: '页面不存在' } },
  ],
})
