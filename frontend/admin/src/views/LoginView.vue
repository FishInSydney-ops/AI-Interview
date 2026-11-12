<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ApiError } from '@yunshu/shared/api'
import AuthLayout from '@yunshu/shared/AuthLayout.vue'
import '@yunshu/shared/auth-form.css'
import { useAdminAuth } from '../stores/auth'

const auth = useAdminAuth()
const route = useRoute()
const router = useRouter()
const username = ref('')
const password = ref('')
const visible = ref(false)
const pending = ref(false)
const error = ref(route.query.reason === 'unavailable' ? '暂时无法连接后台服务，请稍后重试。' : '')
const help = ref(false)

async function submit() {
  if (pending.value) return
  error.value = ''
  if (!username.value.trim() || !password.value) {
    error.value = '请输入管理员账号和密码'
    return
  }
  pending.value = true
  try {
    await auth.login(username.value, password.value)
    password.value = ''
    const redirect = route.query.redirect
    const destination = typeof redirect === 'string' && redirect.startsWith('/')
      && !redirect.startsWith('//') && !redirect.includes('\\') && !redirect.startsWith('/login')
      ? redirect : '/'
    await router.replace(destination)
  } catch (cause) {
    error.value = cause instanceof ApiError ? cause.message : '暂时无法连接后台服务，请稍后重试'
  } finally {
    pending.value = false
  }
}
onMounted(() => { document.title = '管理员登录 - 云枢智学' })
</script>

<template>
  <AuthLayout audience="管理后台" title="管理员登录" description="欢迎回来，请登录以管理学习内容。" back-href="http://127.0.0.1:5173/">
    <form class="ys-login-form" @submit.prevent="submit">
      <p v-if="error" class="ys-login-error" role="alert">{{ error }}</p>
      <div class="ys-login-field"><label for="admin-username">管理员账号</label><input id="admin-username" v-model="username" class="ys-login-input" type="text" placeholder="请输入管理员账号" autocomplete="username" maxlength="64" required :disabled="pending" /></div>
      <div class="ys-login-field"><label for="admin-password">登录密码</label><div class="ys-input-wrap"><input id="admin-password" v-model="password" class="ys-login-input" :type="visible ? 'text' : 'password'" placeholder="请输入登录密码" autocomplete="current-password" maxlength="128" required :disabled="pending" /><button type="button" class="ys-password-toggle" :aria-label="visible ? '隐藏密码' : '显示密码'" :aria-pressed="visible" @click="visible = !visible"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/><path v-if="visible" d="m3 3 18 18"/></svg></button></div></div>
      <div class="ys-login-options"><span>登录后有效期为 7 天</span><button class="ys-login-help" type="button" @click="help = !help">忘记密码？</button></div>
      <p v-if="help" class="ys-login-error ys-login-info" role="status">请联系系统维护人员处理管理员账号，切勿向他人提供密码。</p>
      <button class="ys-login-submit" type="submit" :disabled="pending" :aria-busy="pending">{{ pending ? '正在登录…' : '登 录' }}</button>
    </form>
    <p class="ys-login-bottom">管理员账号与学员账号独立<br><a href="http://127.0.0.1:5173/">返回学员首页 →</a></p>
  </AuthLayout>
</template>
