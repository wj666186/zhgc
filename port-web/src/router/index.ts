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
                meta: { title: '首页看板', roles: ['admin', 'operator'] }
            },
            {
                path: 'vessel',
                name: 'VesselPlan',
                component: () => import('@/views/VesselPlan.vue'),
                meta: { title: '船舶计划管理', roles: ['admin', 'operator'] }
            },
            {
                path: 'container',
                name: 'Container',
                component: () => import('@/views/Container.vue'),
                meta: { title: '集装箱信息管理', roles: ['admin', 'operator'] }
            },
            {
                path: 'yard',
                name: 'Yard',
                component: () => import('@/views/Yard.vue'),
                meta: { title: '堆场调度管理', roles: ['admin', 'operator'] }
            },
            {
                path: 'truck',
                name: 'TruckDispatch',
                component: () => import('@/views/TruckDispatch.vue'),
                meta: { title: '集卡调度管理', roles: ['admin', 'operator'] }
            },
            {
                path: 'gate',
                name: 'GateManage',
                component: () => import('@/views/GateManage.vue'),
                meta: { title: '闸口无感通行', roles: ['admin', 'operator'] }
            },
            {
                path: 'equipment',
                name: 'EquipmentManage',
                component: () => import('@/views/EquipmentManage.vue'),
                meta: { title: '设备管控', roles: ['admin', 'operator'] }
            },
            {
                path: 'aiRecognition',
                name: 'AiRecognition',
                component: () => import('@/views/AiRecognition.vue'),
                meta: { title: 'AI智能识别', roles: ['admin', 'operator'] }
            },
            {
                path: 'digitalTwin',
                name: 'DigitalTwin',
                component: () => import('@/views/DigitalTwin.vue'),
                meta: { title: '数字孪生港口时空视图', roles: ['admin', 'operator'] }
            },
            {
                path: 'command',
                name: 'CommandCenter',
                component: () => import('@/views/CommandCenter.vue'),
                meta: { title: '实时协同指挥', roles: ['admin', 'operator'] }
            },
            {
                path: 'userManage',
                name: 'UserManage',
                component: () => import('@/views/UserManage.vue'),
                meta: { title: '用户管理', roles: ['admin'] }
            },
            {
                path: 'operationLog',
                name: 'OperationLog',
                component: () => import('@/views/OperationLog.vue'),
                meta: { title: '审计日志', roles: ['admin', 'operator'] }
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
    const userRole = localStorage.getItem('userRole') || ''

    // 登录页直接放行
    if (to.path === '/login') {
        next()
        return
    }

    // 未登录跳转登录页
    if (!token) {
        next('/login')
        return
    }

    // 角色权限校验
    const allowedRoles = to.meta?.roles as string[] | undefined
    if (allowedRoles && allowedRoles.length > 0) {
        if (!allowedRoles.includes(userRole)) {
            ElMessage.warning(`当前账号（${userRole}）无权限访问该模块`)
            next('/dashboard')
            return
        }
    }

    next()
})

export default router
