import { createApp } from 'vue'
import { adminPinia } from './stores'
import { ElDropdown, ElDropdownItem, ElDropdownMenu } from 'element-plus'
import 'element-plus/es/components/dropdown/style/css'
import './styles/admin.css'
import App from './App.vue'
import { router } from './router'

createApp(App)
  .use(adminPinia)
  .use(router)
  .component('ElDropdown', ElDropdown)
  .component('ElDropdownMenu', ElDropdownMenu)
  .component('ElDropdownItem', ElDropdownItem)
  .mount('#app')
