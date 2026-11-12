<script setup lang="ts">
defineProps<{ name: string }>()

const paths: Record<string, string> = {
  dashboard: 'M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z',
  subjects: 'm2 8 10-5 10 5-10 5L2 8Z M6 10v7c4 3 8 3 12 0v-7 M22 8v8',
  video: 'M4 4h16a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1Z m6 4 6 4-6 4V8Z',
  books: 'M3 4h5v16H3z M8 4h5v16H8z m6 1 4-1 4 15-4 1-4-15Z',
  archive: 'M3 8h18v12H3z M2 4h20v4H2z M9 12h6',
  route: 'M5 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z M19 21a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z M5 7v6a3 3 0 0 0 3 3h8a3 3 0 0 0 0-6h-4',
  student: 'M15 7a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z M5 21v-3a7 7 0 0 1 14 0v3 M9 15l3 3 3-3',
  users: 'M14 7a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z M3 21v-3a7 7 0 0 1 14 0v3 M17 4a3 3 0 0 1 0 6 M21 21v-3a6 6 0 0 0-3-5',
  shield: 'm12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z m-3 9 2 2 4-4',
  document: 'M5 3h10l4 4v14H5V3Z M14 3v5h5 M9 12h6 M9 16h6',
  settings: 'M9 3h6l1 3 3 1 2 5-2 5-3 1-1 3H9l-1-3-3-1-2-5 2-5 3-1 1-3Z M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z',
  collapse: 'M3 5h18v14H3V5Z M9 5v14 m7-10-3 3 3 3',
  expand: 'M3 5h18v14H3V5Z M9 5v14 m4-10 3 3-3 3',
  menu: 'M4 6h16 M4 12h16 M4 18h16',
  bell: 'M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9 M10 21h4',
  chevron: 'm8 10 4 4 4-4',
  home: 'm3 10 9-7 9 7 M5 9v12h14V9 M9 21v-7h6v7',
  logout: 'M9 3H4v18h5 M9 12h12 m-4-4 4 4-4 4',
  close: 'm6 6 12 12 M6 18 18 6',
}
</script>

<template>
  <svg class="admin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path :d="paths[name] || paths.document" />
  </svg>
</template>
