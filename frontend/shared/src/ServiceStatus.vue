<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { getReadiness, type Readiness } from './api'

const services = ref<Readiness['services'] | null>(null)
const loading = ref(false)
const error = ref('')
const requestId = ref('')
let controller: AbortController | undefined

async function refresh() {
  controller?.abort()
  controller = new AbortController()
  const timeout = setTimeout(() => controller?.abort(), 15000)
  loading.value = true
  error.value = ''
  try {
    const result = await getReadiness(controller.signal)
    services.value = result.data.services
    requestId.value = result.request_id
  } catch {
    services.value = null
    error.value = '暂时无法连接后端，请确认 API 服务已启动后重试。'
  } finally {
    clearTimeout(timeout)
    loading.value = false
  }
}
onMounted(refresh)
onBeforeUnmount(() => controller?.abort())
</script>

<template>
  <section class="status-panel" aria-label="基础服务状态">
    <div class="section-heading">
      <div><span class="eyebrow">CONNECTIONS</span><h2>基础服务连接</h2></div>
      <el-button :loading="loading" @click="refresh">重新检查</el-button>
    </div>
    <p v-if="error" role="alert" class="error">{{ error }}</p>
    <div v-else class="status-grid" aria-live="polite">
      <article v-for="name in ['mysql', 'redis', 'minio'] as const" :key="name">
        <span class="service-name">{{ name === 'mysql' ? 'MySQL' : name === 'redis' ? 'Redis' : 'MinIO' }}</span>
        <el-tag :type="!services ? 'info' : services[name] === 'ok' ? 'success' : 'danger'">
          {{ !services ? '检查中' : services[name] === 'ok' ? '连接正常' : '暂不可用' }}
        </el-tag>
      </article>
    </div>
    <p v-if="requestId" class="request-id">请求标识 {{ requestId }}</p>
  </section>
</template>
