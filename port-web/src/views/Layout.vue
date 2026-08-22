<template>
    <el-container class="layout-container">
        <!-- 左侧侧边栏 -->
        <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
            <div class="sidebar-logo">
                <div class="logo-icon">
                    <el-icon :size="24"><Ship /></el-icon>
                </div>
                <span v-show="!isCollapse" class="logo-text">港口调度系统</span>
            </div>

            <el-menu
                :default-active="activeMenu"
                :collapse="isCollapse"
                :collapse-transition="false"
                router
                class="sidebar-menu"
                background-color="transparent"
                text-color="rgba(255,255,255,0.75)"
                active-text-color="#ffffff"
            >
                <el-menu-item
                    v-for="item in visibleMenus"
                    :key="item.path"
                    :index="item.path"
                >
                    <el-icon><component :is="item.icon" /></el-icon>
                    <template #title>{{ item.title }}</template>
                </el-menu-item>
            </el-menu>

            <div class="sidebar-footer">
                <div class="user-info" @click="showUserMenu = !showUserMenu">
                    <el-avatar :size="32" class="user-avatar">
                        {{ username.charAt(0).toUpperCase() }}
                    </el-avatar>
                    <div v-show="!isCollapse" class="user-detail">
                        <div class="user-name">{{ username }}</div>
                        <div class="user-role">{{ roleMap[userRole] || userRole }}</div>
                    </div>
                </div>
            </div>
        </el-aside>

        <!-- 右侧主区域 -->
        <el-container class="main-container">
            <!-- 顶部栏 -->
            <el-header class="header-bar">
                <div class="header-left">
                    <el-icon class="collapse-btn" :size="20" @click="isCollapse = !isCollapse">
                        <Fold v-if="!isCollapse" />
                        <Expand v-else />
                    </el-icon>
                    <el-breadcrumb separator="/" class="breadcrumb">
                        <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
                        <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
                    </el-breadcrumb>
                </div>
                <div class="header-right">
                    <el-tooltip content="刷新数据" placement="bottom">
                        <el-icon class="header-icon" :size="18" @click="refreshPage"><Refresh /></el-icon>
                    </el-tooltip>
                    <el-dropdown trigger="click" @command="handleCommand">
                        <div class="header-user">
                            <el-avatar :size="28" class="header-avatar">
                                {{ username.charAt(0).toUpperCase() }}
                            </el-avatar>
                            <span class="header-username">{{ username }}</span>
                            <el-icon><ArrowDown /></el-icon>
                        </div>
                        <template #dropdown>
                            <el-dropdown-menu>
                                <el-dropdown-item disabled>
                                    <el-icon><User /></el-icon>
                                    角色：{{ roleMap[userRole] || userRole }}
                                </el-dropdown-item>
                                <el-dropdown-item divided command="logout">
                                    <el-icon><SwitchButton /></el-icon>
                                    退出登录
                                </el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                    </el-dropdown>
                </div>
            </el-header>

            <!-- 内容区 -->
            <el-main class="content-area">
                <router-view v-slot="{ Component }">
                    <transition name="fade" mode="out-in">
                        <component :is="Component" />
                    </transition>
                </router-view>
            </el-main>
        </el-container>
    </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
    Ship, DataAnalysis, Box, Grid, Van, Tickets, Tools, Cpu,
    Monitor, ChatDotRound, User, Document, Fold, Expand,
    Refresh, ArrowDown, SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const isCollapse = ref(false)
const showUserMenu = ref(false)

const username = computed(() => localStorage.getItem('username') || '用户')
const userRole = computed(() => localStorage.getItem('userRole') || '')

// 菜单配置
const menuConfig = [
    { path: '/dashboard', title: '首页看板', icon: DataAnalysis, roles: ['admin', 'operator'] },
    { path: '/vessel', title: '船舶计划', icon: Ship, roles: ['admin', 'operator'] },
    { path: '/container', title: '集装箱管理', icon: Box, roles: ['admin', 'operator'] },
    { path: '/yard', title: '堆场调度', icon: Grid, roles: ['admin', 'operator'] },
    { path: '/truck', title: '集卡调度', icon: Van, roles: ['admin', 'operator'] },
    { path: '/gate', title: '闸口通行', icon: Tickets, roles: ['admin', 'operator'] },
    { path: '/equipment', title: '设备管控', icon: Tools, roles: ['admin', 'operator'] },
    { path: '/aiRecognition', title: 'AI智能识别', icon: Cpu, roles: ['admin', 'operator'] },
    { path: '/digitalTwin', title: '数字孪生视图', icon: Monitor, roles: ['admin', 'operator'] },
    { path: '/command', title: '协同指挥', icon: ChatDotRound, roles: ['admin', 'operator'] },
    { path: '/userManage', title: '用户管理', icon: User, roles: ['admin'] },
    { path: '/operationLog', title: '审计日志', icon: Document, roles: ['admin', 'operator'] },
]

const roleMap: Record<string, string> = {
    admin: '管理员',
    operator: '调度员',
}

const visibleMenus = computed(() => {
    return menuConfig.filter(item => item.roles.includes(userRole.value))
})

const activeMenu = computed(() => route.path)

const currentPageTitle = computed(() => {
    const item = menuConfig.find(m => m.path === route.path)
    return item?.title || '首页看板'
})

const refreshPage = () => {
    window.location.reload()
}

const handleCommand = (cmd: string) => {
    if (cmd === 'logout') {
        ElMessageBox.confirm('确定要退出登录吗？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }).then(() => {
            localStorage.removeItem('token')
            localStorage.removeItem('username')
            localStorage.removeItem('userRole')
            ElMessage.success('已退出登录')
            router.push('/login')
        }).catch(() => {})
    }
}
</script>

<style scoped>
.layout-container {
    height: 100vh;
    width: 100vw;
}

/* 侧边栏 */
.sidebar {
    background: linear-gradient(180deg, #0d4a52 0%, #11616B 50%, #0d4a52 100%);
    display: flex;
    flex-direction: column;
    transition: width 0.3s ease;
    overflow: hidden;
    position: relative;
}

.sidebar::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 100%;
    background: radial-gradient(ellipse at top, rgba(123, 189, 182, 0.15) 0%, transparent 60%);
    pointer-events: none;
}

.sidebar-logo {
    height: 60px;
    display: flex;
    align-items: center;
    padding: 0 16px;
    gap: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    flex-shrink: 0;
    position: relative;
    z-index: 1;
}

.logo-icon {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #7BBDB6, #1a8a97);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    flex-shrink: 0;
}

.logo-text {
    color: #fff;
    font-size: 16px;
    font-weight: 700;
    white-space: nowrap;
    letter-spacing: 1px;
}

/* 菜单 */
.sidebar-menu {
    flex: 1;
    border-right: none !important;
    padding: 12px 8px;
    position: relative;
    z-index: 1;
    overflow-y: auto;
    overflow-x: hidden;
}

.sidebar-menu:not(.el-menu--collapse) {
    width: 100%;
}

.sidebar-menu .el-menu-item {
    height: 46px;
    line-height: 46px;
    border-radius: 8px;
    margin-bottom: 4px;
    font-size: 14px;
    transition: all 0.2s;
}

.sidebar-menu .el-menu-item:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #fff !important;
}

.sidebar-menu .el-menu-item.is-active {
    background: linear-gradient(90deg, rgba(123, 189, 182, 0.3), rgba(123, 189, 182, 0.1)) !important;
    color: #fff !important;
    font-weight: 600;
    box-shadow: inset 3px 0 0 #7BBDB6;
}

/* 底部用户区 */
.sidebar-footer {
    padding: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    flex-shrink: 0;
    position: relative;
    z-index: 1;
}

.user-info {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px;
    border-radius: 10px;
    cursor: pointer;
    transition: background 0.2s;
}
.user-info:hover {
    background: rgba(255, 255, 255, 0.08);
}

.user-avatar {
    background: linear-gradient(135deg, #7BBDB6, #1a8a97);
    color: #fff;
    font-weight: 600;
    flex-shrink: 0;
}

.user-detail {
    flex: 1;
    min-width: 0;
}
.user-name {
    color: #fff;
    font-size: 14px;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.user-role {
    color: rgba(255, 255, 255, 0.6);
    font-size: 12px;
    margin-top: 2px;
}

/* 主区域 */
.main-container {
    background: #f0f4f8;
    overflow: hidden;
}

/* 顶部栏 */
.header-bar {
    height: 60px !important;
    background: #fff;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px !important;
    flex-shrink: 0;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 16px;
}

.collapse-btn {
    cursor: pointer;
    color: #606266;
    transition: color 0.2s;
    padding: 6px;
    border-radius: 6px;
}
.collapse-btn:hover {
    color: #11616B;
    background: #EBF4F8;
}

.breadcrumb {
    font-size: 14px;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 16px;
}

.header-icon {
    cursor: pointer;
    color: #606266;
    padding: 6px;
    border-radius: 6px;
    transition: all 0.2s;
}
.header-icon:hover {
    color: #11616B;
    background: #EBF4F8;
}

.header-user {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    padding: 4px 10px;
    border-radius: 8px;
    transition: background 0.2s;
}
.header-user:hover {
    background: #f5f7fa;
}

.header-avatar {
    background: linear-gradient(135deg, #11616B, #1a8a97);
    color: #fff;
    font-weight: 600;
}

.header-username {
    font-size: 14px;
    color: #303133;
    font-weight: 500;
}

/* 内容区 */
.content-area {
    padding: 0 !important;
    overflow: hidden;
    background: #f0f4f8;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from {
    opacity: 0;
    transform: translateY(8px);
}
.fade-leave-to {
    opacity: 0;
    transform: translateY(-8px);
}
</style>
