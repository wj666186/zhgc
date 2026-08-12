<template>
    <div class="layout-box">
        <!-- 左侧固定侧边栏 -->
        <aside class="left-sidebar">
            <div class="sidebar-title">
                <el-icon :size="24" style="margin-right: 8px;"><Odometer /></el-icon>
                港口集装箱调度系统
            </div>
            <div class="menu-list">
                <router-link to="/dashboard" class="menu-item">
                    <el-icon><DataAnalysis /></el-icon><span>首页看板</span>
                </router-link>
                <router-link to="/vessel" class="menu-item">
                    <el-icon><Ship /></el-icon><span>船舶计划</span>
                </router-link>
                <router-link to="/container" class="menu-item">
                    <el-icon><Box /></el-icon><span>集装箱管理</span>
                </router-link>
                <router-link to="/yard" class="menu-item">
                    <el-icon><Grid /></el-icon><span>堆场调度</span>
                </router-link>
                <router-link to="/truck" class="menu-item">
                    <el-icon><Van /></el-icon><span>集卡调度</span>
                </router-link>
                <router-link to="/gate" class="menu-item">
                    <el-icon><Tickets /></el-icon><span>闸口通行</span>
                </router-link>
                <router-link to="/equipment" class="menu-item">
                    <el-icon><Tools /></el-icon><span>设备管控</span>
                </router-link>
                <router-link to="/aiRecognition" class="menu-item">
                    <el-icon><Cpu /></el-icon><span>AI智能识别</span>
                </router-link>
                <router-link to="/digitalTwin" class="menu-item">
                    <el-icon><Monitor /></el-icon><span>数字孪生视图</span>
                </router-link>
                <router-link to="/command" class="menu-item">
                    <el-icon><ChatDotRound /></el-icon><span>协同指挥</span>
                </router-link>
                <router-link v-if="isAdmin" to="/userManage" class="menu-item">
                    <el-icon><User /></el-icon><span>用户管理</span>
                </router-link>
                <router-link to="/operationLog" class="menu-item">
                    <el-icon><Document /></el-icon><span>审计日志</span>
                </router-link>
            </div>
            <div class="logout-btn" @click="logout">
                <el-icon><SwitchButton /></el-icon><span>退出登录</span>
            </div>
        </aside>

        <!-- 右侧自适应内容区 -->
        <main class="page-content">
            <router-view :key="route.fullPath" />
        </main>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
    Odometer, DataAnalysis, Ship, Box, Grid, Van, Tickets,
    Tools, Cpu, Monitor, ChatDotRound, User, Document, SwitchButton
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 用户角色
const userRole = ref(localStorage.getItem('userRole') || '')
const isAdmin = ref(userRole.value === 'admin')

// 监听路由变化，切换页面时重新读取角色（防止登录切换账号不刷新菜单）
watch(() => route.fullPath, () => {
    userRole.value = localStorage.getItem('userRole') || ''
    isAdmin.value = userRole.value === 'admin'
})

onMounted(() => {
    userRole.value = localStorage.getItem('userRole') || ''
    isAdmin.value = userRole.value === 'admin'
})

const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('userRole')
    router.push('/login')
}
</script>

<style scoped>
/* 全局铺满视口，无外边距 */
.layout-box {
    display: flex;
    width: 100%;
    height: 100vh;
    margin: 0;
    padding: 0;
    overflow: hidden;
}

/* 侧边栏永久固定230px，绝不压缩、绝不拉伸 */
.left-sidebar {
    width: 220px;
    flex-shrink: 0;
    height: 100%;
    background: linear-gradient(180deg, rgba(17, 97, 107, 0.95) 0%, rgba(13, 71, 79, 0.95) 100%);
    display: flex;
    flex-direction: column;
    padding: 30px 0 24px;
    box-sizing: border-box;
    box-shadow: 2px 0 12px rgba(0,0,0,0.15);
}

.sidebar-title {
    color: #EBF4F8;
    font-size: 18px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 30px;
    letter-spacing: 1px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 12px;
}

.menu-list {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 0 12px;
    overflow-y: auto;
}

.menu-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    border-radius: 8px;
    color: #c8d6dc;
    text-decoration: none;
    font-size: 15px;
    transition: all 0.24s ease;
}
.menu-item:hover {
    background-color: rgba(123, 189, 182, 0.2);
    color: #fff;
}
/* 路由激活高亮 */
.router-link-active {
    background: linear-gradient(90deg, #7BBDB6 0%, #5fa8a0 100%);
    color: #fff;
    font-weight: 500;
    box-shadow: 0 2px 8px rgba(123, 189, 182, 0.4);
}

.logout-btn {
    margin: 12px 12px 0;
    padding: 12px;
    text-align: center;
    border: 1px solid rgba(235, 244, 248, 0.3);
    border-radius: 8px;
    color: #c8d6dc;
    cursor: pointer;
    transition: 0.24s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 15px;
}
.logout-btn:hover {
    background-color: #DC8B70;
    border-color: #DC8B70;
    color: #fff;
}

/* 右侧内容区透明，继承App全局背景 */
.page-content {
    flex: 1;
    min-width: 0;
    height: 100vh;
    overflow-y: auto;
    overflow-x: hidden;
    background-color: transparent;
    box-sizing: border-box;
}
</style>
