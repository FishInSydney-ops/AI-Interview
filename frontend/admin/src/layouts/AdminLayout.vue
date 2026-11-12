<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import 'element-plus/es/components/message/style/css'
import 'element-plus/es/components/message-box/style/css'
import { useAdminAuth } from '../stores/auth'
import AdminIcon from '../components/AdminIcon.vue'
import { platform, loadPlatform } from '../platform'
import { navigationGroups } from '../navigation'

const route = useRoute()
const visibleGroups = computed(() => navigationGroups.map(group => ({...group, items: group.items.filter(item => {
 const permission:Record<string,string>={'/users':'user:view','/roles':'system:roles','/logs':'system:logs','/settings':'system:settings'}
 return !permission[item.path] || auth.session?.is_super || auth.session?.permissions.includes(permission[item.path])
})})).filter(group=>group.items.length))
const router = useRouter()
const auth = useAdminAuth()
const loggingOut = ref(false)

async function handleLogout() {
  if (loggingOut.value) return
  try {
    await ElMessageBox.confirm('确定退出管理后台吗？', '退出登录', {
      confirmButtonText: '退出登录', cancelButtonText: '取消', type: 'warning',
    })
  } catch { return }
  loggingOut.value = true
  try {
    await auth.logout()
    await router.replace({ name: 'admin-login' })
  } catch {
    ElMessage.error('退出失败，请检查网络后重试')
  } finally { loggingOut.value = false }
}
const collapsed = ref(false)
const mobile = ref(false)
const drawerOpen = ref(false)
const sidebar = ref<HTMLElement>()
const toggleButton = ref<HTMLButtonElement>()
const pageTitle = computed(() => String(route.meta.title || '管理后台'))
const showCompact = computed(() => collapsed.value && !mobile.value)
let media: MediaQueryList | undefined
let previousOverflow = ''

function syncViewport() {
  mobile.value = media?.matches ?? false
  if (!mobile.value) drawerOpen.value = false
}

function toggleNavigation() {
  if (mobile.value) drawerOpen.value = !drawerOpen.value
  else collapsed.value = !collapsed.value
}

async function closeDrawer(restoreFocus = true) {
  drawerOpen.value = false
  if (restoreFocus) {
    await nextTick()
    toggleButton.value?.focus()
  }
}

function handleKeys(event: KeyboardEvent) {
  if (!drawerOpen.value) return
  if (event.key === 'Escape') {
    event.preventDefault()
    closeDrawer()
  }
  if (event.key === 'Tab') {
    const controls = sidebar.value?.querySelectorAll<HTMLElement>('a[href], button:not([disabled])')
    const first = controls?.[0]
    const last = controls?.[controls.length - 1]
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault()
      last?.focus()
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault()
      first?.focus()
    }
  }
}

watch(drawerOpen, async (open) => {
  if (open) {
    previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    await nextTick()
    sidebar.value?.querySelector<HTMLElement>('a[href]')?.focus()
  } else document.body.style.overflow = previousOverflow
})
watch(() => route.path, () => {
  if (drawerOpen.value) closeDrawer()
})
watch(pageTitle, (title) => {
  document.title = `${title} - ${platform.name}后台`
}, { immediate: true })

onMounted(() => {
  void loadPlatform()
  media = window.matchMedia('(max-width: 768px)')
  syncViewport()
  media.addEventListener('change', syncViewport)
  document.addEventListener('keydown', handleKeys)
})
onBeforeUnmount(() => {
  media?.removeEventListener('change', syncViewport)
  document.removeEventListener('keydown', handleKeys)
  if (drawerOpen.value) document.body.style.overflow = previousOverflow
})
</script>

<template>
  <div class="admin-shell" :class="{ 'is-collapsed': showCompact, 'is-drawer-open': drawerOpen }">
    <a class="admin-skip-link" href="#admin-content">跳转到内容区</a>
    <div v-if="mobile && drawerOpen" class="admin-backdrop" aria-hidden="true" @click="closeDrawer()" />
    <aside id="admin-navigation" ref="sidebar" class="admin-sidebar"
      :inert="mobile && !drawerOpen"
      :role="mobile && drawerOpen ? 'dialog' : undefined"
      :aria-modal="mobile && drawerOpen ? true : undefined" aria-label="后台导航">
      <div class="admin-sidebar-header">
        <RouterLink class="admin-brand" to="/" :title="showCompact ? '云枢智学后台' : undefined" aria-label="云枢智学后台首页">
          <img v-if="platform.logo_file_id" :src="'/api/v1/platform/files/'+platform.logo_file_id" class="admin-brand-mark" alt=""><svg v-else class="admin-brand-mark" viewBox="0 0 24 24" aria-hidden="true">
            <defs><linearGradient id="admin-brand-gradient" x2="1" y2="1"><stop stop-color="#8ea2ff"/><stop offset="1" stop-color="#c9a6ff"/></linearGradient></defs>
            <g fill="url(#admin-brand-gradient)"><path d="M13.05 3.55C14.79 11.21 14.79 11.21 22.45 12.95C14.79 14.69 14.79 14.69 13.05 22.35C11.31 14.69 11.31 14.69 3.65 12.95C11.31 11.21 11.31 11.21 13.05 3.55Z"/><path opacity=".72" d="M5.65 1.65C6.41 4.99 6.41 4.99 9.75 5.75C6.41 6.51 6.41 6.51 5.65 9.85C4.89 6.51 4.89 6.51 1.55 5.75C4.89 4.99 4.89 4.99 5.65 1.65Z"/></g>
          </svg>
          <span class="admin-brand-text">{{ platform.name }}后台</span>
        </RouterLink>
        <button v-if="mobile" class="admin-icon-button admin-drawer-close" aria-label="关闭导航" @click="closeDrawer()"><AdminIcon name="close" /></button>
      </div>
      <nav class="admin-navigation" aria-label="管理菜单">
        <section v-for="group in visibleGroups" :key="group.title" class="admin-nav-group" :aria-label="group.title">
          <h2 class="admin-nav-group-title">{{ group.title }}</h2>
          <RouterLink v-for="item in group.items" :key="item.path" :to="item.path"
            class="admin-nav-item" :class="{ 'is-active': route.path === item.path }"
            :aria-current="route.path === item.path ? 'page' : undefined"
            :aria-label="item.title" :title="showCompact ? item.title : undefined">
            <AdminIcon :name="item.icon" /><span class="admin-nav-label">{{ item.title }}</span>
          </RouterLink>
        </section>
      </nav>
    </aside>

    <div class="admin-main" :inert="mobile && drawerOpen">
      <header class="admin-header">
        <div class="admin-header-left">
          <button ref="toggleButton" class="admin-icon-button" :aria-label="mobile ? '展开导航' : showCompact ? '展开侧边栏' : '折叠侧边栏'"
            :aria-expanded="mobile ? drawerOpen : !showCompact" aria-controls="admin-navigation" @click="toggleNavigation">
            <AdminIcon :name="mobile ? 'menu' : showCompact ? 'expand' : 'collapse'" />
          </button>
          <h1 class="admin-page-title">{{ pageTitle }}</h1>
        </div>
        <div class="admin-header-right">
          <button class="admin-icon-button admin-notification" disabled aria-label="通知功能暂未开放" title="通知功能暂未开放"><AdminIcon name="bell" /></button>
          <span class="admin-header-divider" aria-hidden="true" />
          <el-dropdown trigger="click" placement="bottom-end">
            <button class="admin-account-button" aria-label="打开管理员菜单">
              <img v-if="platform.avatar_file_id" :src="'/api/v1/platform/files/'+platform.avatar_file_id" style="width:32px;height:32px;border-radius:50%;object-fit:cover" alt="默认头像"><span v-else class="admin-avatar" aria-hidden="true">{{ auth.session?.username.slice(0, 1).toUpperCase() }}</span><span class="admin-account-name">{{ auth.session?.username }}</span><AdminIcon name="chevron" />
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item><a class="admin-portal-link" href="http://127.0.0.1:5173/"><AdminIcon name="home" />返回前台</a></el-dropdown-item>
                <el-dropdown-item divided :disabled="loggingOut" @click="handleLogout"><span class="admin-dropdown-action"><AdminIcon name="logout" />{{ loggingOut ? '正在退出…' : '退出登录' }}</span></el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      <main id="admin-content" class="admin-content" tabindex="-1"><RouterView /></main>
    </div>
  </div>
</template>
