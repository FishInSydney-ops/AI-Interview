<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AuthLayout from '@yunshu/shared/AuthLayout.vue'
import '@yunshu/shared/auth-form.css'
const visible = ref(false)
const notice = ref('')
onMounted(() => { document.title = '学员登录 - 云枢智学' })
function submit() { notice.value = '学员账号登录暂未开放，您可以先返回首页浏览学习内容。' }
</script>
<template>
  <AuthLayout audience="学员端" title="欢迎回来" description="登录你的账户，继续自己的学习旅程。" back-href="/">
    <form class="ys-login-form" @submit.prevent="submit">
      <p v-if="notice" class="ys-login-error ys-login-info" role="status">{{ notice }}</p>
      <div class="ys-login-field"><label for="student-username">用户名</label><input id="student-username" class="ys-login-input" type="text" placeholder="请输入用户名" autocomplete="username" maxlength="64" required /></div>
      <div class="ys-login-field"><label for="student-password">密码</label><div class="ys-input-wrap"><input id="student-password" class="ys-login-input" :type="visible ? 'text' : 'password'" placeholder="请输入密码" autocomplete="current-password" maxlength="128" required /><button class="ys-password-toggle" type="button" :aria-label="visible ? '隐藏密码' : '显示密码'" :aria-pressed="visible" @click="visible = !visible"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/><path v-if="visible" d="m3 3 18 18"/></svg></button></div></div>
      <div class="ys-login-options"><span>用户名与密码登录</span><button class="ys-login-help" type="button" @click="notice = '学员账号服务开放后，可联系管理员找回密码。'">忘记密码？</button></div>
      <button class="ys-login-submit" type="submit">登 录</button>
    </form>
    <p class="ys-login-bottom">学员账号服务即将开放<br><a href="/">先去看看学习内容 →</a></p>
  </AuthLayout>
</template>
