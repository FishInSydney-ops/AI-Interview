<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<template>
  <section class="admin-empty-page" :aria-label="`${route.meta.title}内容区`">
    <div v-if="route.meta.notFound" class="admin-empty-message">
      <span class="admin-not-found-code">404</span><p>页面不存在</p><RouterLink to="/">返回数据看板</RouterLink>
    </div>
    <p v-else class="admin-empty-hint">页面内容待完善</p>
  </section>
</template>
