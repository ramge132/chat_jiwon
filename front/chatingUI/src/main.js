// front/chatingUI/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Bootstrap CSS 및 JS 임포트
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

createApp(App).use(router).mount('#app')
