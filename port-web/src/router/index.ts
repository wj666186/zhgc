import type { RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

const routes: RouteRecordRaw[] = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/Login.vue'),
        meta: { title: '系统登录' }
    },
    // 后台整体布局父路由
    {
        path: '/',
        component: () => import('@/views/Layout.vue'),
        redirect: '/dashboard',
        children: [
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: () => import('@/views/Dashboard.vue'),
                meta: { title: '首页看板' }
            },
            {
                path: 'container',
                name: 'Container',
                component: () => import('@/views/Container.vue'),
                meta: { title: '集装箱信息管理' }
            },
            {
                path: 'yard',
                name: 'Yard',
                component: () => import('@/views/Yard.vue'),
                meta: { title: '堆场调度管理' }
            },
            {
                path: 'aiRecognition',
                name: 'AiRecognition',
                component: () => import('@/views/AiRecognition.vue'),
                meta: { title: 'AI视觉巡检' }
            },
            {
                path: 'userManage',
                name: 'UserManage',
                component: () => import('@/views/UserManage.vue'),
                meta: { title: '用户管理' },
                // 管理员专属页面路由守卫
                beforeEnter: (_to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
                    const role = localStorage.getItem('userRole')
                    if (role === 'admin') {
                        next()
                    } else {
                        ElMessage.warning('仅管理员账号可访问用户管理页面')
                        next(from.path)
                    }
                }
            },
            {
                path: 'digitalTwin',
                name: 'DigitalTwin',
                component: () => import('@/views/DigitalTwin.vue'),
                meta: { title: '数字孪生港口时空视图' }
            }

        ]
    },
    // 全局404页面兜底
    {
        path: '/:pathMatch(.*)*',
        redirect: '/login'
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 全局登录鉴权前置守卫
router.beforeEach((to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
    const token = localStorage.getItem('token')
    // 访问登录页直接放行
    if (to.path === '/login') {
        next()
        return
    }
    // 未登录无token，强制跳转登录
    if (!token) {
        next('/login')
        return
    }
    // 已登录正常访问
    next()
})

export default router
