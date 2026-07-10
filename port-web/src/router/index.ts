import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Container from '../views/Container.vue'

const routes = [
    {
        path: '/',
        redirect: '/login'
    },
    {
        path: '/login',
        component: Login
    },
    {
        path: '/container',
        component: Container
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router