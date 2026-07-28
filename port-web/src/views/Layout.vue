<template>
    <div class="layout-box">
        <!-- 左侧固定侧边栏 -->
        <aside class="left-sidebar">
            <div class="sidebar-title">港口集装箱调度系统</div>
            <div class="menu-list">
                <!-- 路由路径补全 / 保证 router-link-active 正常高亮 -->
                <router-link to="/dashboard" class="menu-item">首页看板</router-link>
                <router-link to="/container" class="menu-item">集装箱管理</router-link>
                <router-link to="/yard" class="menu-item">堆场调度</router-link>
                <router-link to="/aiRecognition" class="menu-item">AI智能识别</router-link>
                <!-- 新增数字孪生菜单 -->
                <router-link to="/digitalTwin" class="menu-item">数字孪生时空视图</router-link>
                <router-link v-if="isAdmin" to="/userManage" class="menu-item">用户管理</router-link>
            </div>
            <div class="logout-btn" @click="logout">退出登录</div>
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
    width: 230px;
    flex-shrink: 0;
    height: 100%;
    /* 半透明深色，透出全局1.png背景图 */
    background-color: rgba(17, 97, 107, 0.85);
    display: flex;
    flex-direction: column;
    padding: 40px 0 30px;
    box-sizing: border-box;
}

.sidebar-title {
    color: #EBF4F8;
    font-size: 22px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 45px;
    letter-spacing: 1px;
}

.menu-list {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 0 18px;
}

.menu-item {
    display: block;
    padding: 14px 22px;
    border-radius: 8px;
    color: #EBF4F8;
    text-decoration: none;
    font-size: 17px;
    transition: all 0.24s ease;
}
.menu-item:hover {
    background-color: #7BBDB6;
    color: #11616B;
}
/* 路由激活高亮 */
.router-link-active {
    background-color: #7BBDB6;
    color: #11616B;
    font-weight: 500;
}

.logout-btn {
    margin: 0 18px;
    margin-top: 20px;
    padding: 12px;
    text-align: center;
    border: 1px solid #EBF4F8;
    border-radius: 8px;
    color: #EBF4F8;
    cursor: pointer;
    transition: 0.24s;
}
.logout-btn:hover {
    background-color: #DC8B70;
    border-color: #DC8B70;
}

/* 右侧内容区透明，继承App全局1.png背景 */
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
