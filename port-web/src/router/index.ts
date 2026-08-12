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
                path: 'vessel',
                name: 'VesselPlan',
                component: () => import('@/views/VesselPlan.vue'),
                meta: { title: '船舶计划管理' }
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
                path: 'truck',
                name: 'TruckDispatch',
                component: () => import('@/views/TruckDispatch.vue'),
                meta: { title: '集卡调度管理' }
            },
            {
                path: 'gate',
                name: 'GateManage',
                component: () => import('@/views/GateManage.vue'),
                meta: { title: '闸口无感通行' }
            },
            {
                path: 'equipment',
                name: 'EquipmentManage',
                component: () => import('@/views/EquipmentManage.vue'),
                meta: { title: '设备管控' }
            },
            {
                path: 'aiRecognition',
                name: 'AiRecognition',
                component: () => import('@/views/AiRecognition.vue'),
                meta: { title: 'AI智能识别' }
            },
            {
                path: 'digitalTwin',
                name: 'DigitalTwin',
                component: () => import('@/views/DigitalTwin.vue'),
                meta: { title: '数字孪生港口时空视图' }
            },
            {
                path: 'command',
                name: 'CommandCenter',
                component: () => import('@/views/CommandCenter.vue'),
                meta: { title: '实时协同指挥' }
            },
            {
                path: 'userManage',
                name: 'UserManage',
                component: () => import('@/views/UserManage.vue'),
                meta: { title: '用户管理' },
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
                path: 'operationLog',
                name: 'OperationLog',
                component: () => import('@/views/OperationLog.vue'),
                meta: { title: '审计日志' }
            }
        ]
    },
    {
        path: '/:pathMatch(.*)*',
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
        return
    }
    if (!token) {
        next('/login')
        return
    }
    next()
})

export default router
