<script setup lang="ts">
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import {apiRequest} from '@yunshu/shared/api'
import {useAdminAuth} from '../stores/auth'
const password=ref(''), confirmation=ref(''), error=ref(''), busy=ref(false), router=useRouter(), auth=useAdminAuth()
async function save(){if(password.value!==confirmation.value){error.value='两次密码不一致';return}busy.value=true;try{await apiRequest('/api/v1/admin/auth/password',{method:'POST',body:JSON.stringify({new_password:password.value})});await auth.refreshSession();await router.replace('/')}catch(e){error.value=e instanceof Error?e.message:'修改失败'}finally{busy.value=false}}
</script>
<template><main style="max-width:440px;margin:15vh auto;background:white;padding:40px;border-radius:16px"><h1>设置新密码</h1><p>请先设置自己的密码，再进入管理后台。</p><p role="alert">{{error}}</p><form @submit.prevent="save" style="display:grid;gap:20px"><label>新密码<input v-model="password" type="password" minlength="8" maxlength="128" required autocomplete="new-password"></label><label>确认密码<input v-model="confirmation" type="password" required autocomplete="new-password"></label><button :disabled="busy">保存并进入后台</button></form></main></template>
