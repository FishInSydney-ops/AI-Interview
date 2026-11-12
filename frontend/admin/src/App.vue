<template>
  <RouterView v-slot="{ Component }">
    <component :is="Component" v-if="Component" />
    <div v-else class="admin-connecting" role="status">正在连接管理后台…</div>
  </RouterView>
</template>
