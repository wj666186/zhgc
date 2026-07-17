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
        redirect: '/dashboard', // 默认进入首页看板
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
    // 404兜底路由必须放在数组最后一项
    {
        path: '/:pathMatch(.*)*',
        redirect: '/login'
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 强化全局前置守卫，杜绝登录页嵌套Layout、无凭证滞留后台页面
router.beforeEach((to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
    const token = localStorage.getItem('token')
    // 访问登录页，直接放行，不校验登录凭证
    if (to.path === '/login') {
        next()
        return
    }
    // 非登录页面，无token强制跳转登录页
    if (!token) {
        next('/login')
        return
    }
    // 有登录凭证，正常放行访问后台页面
    next()
})

export default router
