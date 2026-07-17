<template>
  <!-- 顶部导航 -->
    <div class="nav-wrap">
        <router-link to="dashboard">首页看板</router-link>
        <router-link to="container">集装箱管理</router-link>
        <router-link to="yard">堆场调度</router-link>
        <router-link to="aiRecognition">AI智能识别</router-link>
        <router-link v-if="isAdmin" to="userManage">用户管理</router-link>
        <div class="logout-btn" @click="logout">退出登录</div>
    </div>

    <router-view :key="route.fullPath" />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
// 关键：导入路由实例
const route = useRoute()

const role = ref(localStorage.getItem('userRole'))
const isAdmin = ref(role.value === 'admin')

onMounted(() => {
    role.value = localStorage.getItem('userRole')
    isAdmin.value = role.value === 'admin'
})

const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('userRole')
    router.push('/login')
}
</script>

<style scoped>
.nav-wrap {
    display:flex;
    gap: 24px;
    padding: 16px;
    font-size: 18px;
    align-items: center;
}
.logout-btn {
    margin-left: auto;
    cursor: pointer;
    padding: 6px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
}
</style>
