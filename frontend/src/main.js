import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import { i18nPlugin } from './plugins/i18n'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(i18nPlugin)
app.mount('#app')
