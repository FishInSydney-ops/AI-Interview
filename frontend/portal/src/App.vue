<script setup lang="ts">
import { useRoute } from 'vue-router'
import BrandMark from '@yunshu/shared/BrandMark.vue'
const route = useRoute()
</script>
<template>
  <RouterView v-if="route.meta.standalone" />
  <div v-else class="portal-shell">
    <header class="portal-header"><div class="portal-header-inner"><RouterLink class="portal-brand" to="/"><BrandMark /><span>云枢智学</span></RouterLink>
      <nav aria-label="主导航"><RouterLink to="/">首页</RouterLink><RouterLink to="/routes">学习路线</RouterLink><RouterLink to="/questions">题库中心</RouterLink><RouterLink to="/interview">AI 面试<span class="portal-soon">即将上线</span></RouterLink></nav>
      <RouterLink to="/login" class="portal-login-link">登录 / 注册</RouterLink>
    </div></header>
    <main class="portal-main"><RouterView /></main>
    <footer class="portal-footer"><div><span>云枢智学</span><p>让学习更有章法，让成长清晰可见。</p></div><a href="http://127.0.0.1:5174/admin/login">管理后台 ↗</a></footer>
  </div>
</template>
