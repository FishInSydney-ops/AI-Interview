<script setup lang="ts">
withDefaults(defineProps<{ light?: boolean }>(), { light: false })
</script>
<template>
  <svg viewBox="0 0 24 24" aria-hidden="true" class="ys-brand-mark" :class="{ 'is-light': light }">
    <path fill="currentColor" d="M13.05 3.55C14.79 11.21 14.79 11.21 22.45 12.95C14.79 14.69 14.79 14.69 13.05 22.35C11.31 14.69 11.31 14.69 3.65 12.95C11.31 11.21 11.31 11.21 13.05 3.55Z"/>
    <path fill="currentColor" opacity=".65" d="M5.65 1.65C6.41 4.99 6.41 4.99 9.75 5.75C6.41 6.51 6.41 6.51 5.65 9.85C4.89 6.51 4.89 6.51 1.55 5.75C4.89 4.99 4.89 4.99 5.65 1.65Z"/>
  </svg>
</template>
<style scoped>
.ys-brand-mark { width: 28px; height: 28px; flex: none; color: #7262d8; }
.ys-brand-mark.is-light { color: #b9b5ff; }
</style>
