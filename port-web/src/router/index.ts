import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
    {
        path: '/',
        redirect: '/dashboard'
    },
    {
        path: '/dashboard',
        name: '首页看板',
        component: () => import('../views/Dashboard.vue')
    },
    {
        path: '/container',
        name: '集装箱管理',
        component: () => import('../views/Container.vue')
    },
    {
        path: '/yard',
        name: '堆场调度',
        component: () => import('../views/Yard.vue')
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router