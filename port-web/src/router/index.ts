import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Container from '../views/Container.vue'
// 导入首页看板组件
import Dashboard from '../views/Dashboard.vue'
// 导入AI识别页面
import AiRecognition from '../views/AiRecognition.vue'

const routes = [
    {
        path: '/',
        redirect: '/login'
    },
    {
        path: '/login',
        component: Login
    },
    // 新增首页看板路由
    {
        path: '/dashboard',
        component: Dashboard
    },
    {
        path: '/container',
        component: Container
    },
    // AI集装箱识别模块路由
    {
        path: '/aiRecognition',
        name: 'AiRecognition',
        component: AiRecognition
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router