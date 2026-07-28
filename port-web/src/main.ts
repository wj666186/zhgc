import { createApp } from 'vue'
import App from './App.vue'
import './style.css'
import router from './router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'

// 1. 创建Axios实例
const api = axios.create({
    baseURL: 'http://localhost:8080',
    timeout: 12000
})

// 2. 请求拦截器：只传纯token，不带Bearer
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    if (token) {
        // 删掉 Bearer 前缀，直接赋值token
        config.headers.Authorization = token
    }
    return config
})

// 3. 响应拦截器：捕获401跳转登录
api.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token')
            localStorage.removeItem('userRole')
            router.push('/login')
        }
        return Promise.reject(error)
    }
)

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.config.globalProperties.$api = api

app.mount('#app')
