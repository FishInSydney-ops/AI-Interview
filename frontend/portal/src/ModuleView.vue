<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
</script>
<template>
  <section class="placeholder"><span class="eyebrow">YUNSHU</span><h1>{{ route.meta.title }}</h1>
    <p>{{ route.path === '/interview' ? 'AI 面试即将上线，首发暂不开放。' : '此页面已预留路由，业务功能尚未实现。' }}</p>
    <RouterLink to="/">返回工程概览 →</RouterLink>
  </section>
</template>
