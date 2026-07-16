import type { RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

const routes: RouteRecordRaw[] = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/Login.vue')
    },
    // 父布局Layout，所有后台页面作为子路由
    {
        path: '/',
        component: () => import('@/views/Layout.vue'),
        children: [
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: () => import('@/views/Dashboard.vue')
            },
            {
                path: 'container',
                name: 'Container',
                component: () => import('@/views/Container.vue')
            },
            {
                path: 'yard',
                name: 'Yard',
                component: () => import('@/views/Yard.vue')
            },
            {
                path: 'aiRecognition',
                name: 'AiRecognition',
                component: () => import('@/views/AiRecognition.vue')
            },
            {
                path: 'userManage',
                name: 'UserManage',
                component: () => import('@/views/UserManage.vue'),
                beforeEnter: (_to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
                    const role = localStorage.getItem('userRole')
                    if (role === 'admin') {
                        next()
                    } else {
                        ElMessage.warning('仅管理员可访问')
                        next(from.path)
                    }
                }
            }
        ]
    },
    {
        path: '/:pathMatch(.*)',
        redirect: '/login'
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
    const token = localStorage.getItem('token')
    if (to.path === '/login') {
        next()
    } else {
        token ? next() : next('/login')
    }
})

export default router