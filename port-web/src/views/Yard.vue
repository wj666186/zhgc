<template>
    <el-menu mode="horizontal" router style="margin-bottom: 20px;">
        <el-menu-item index="/dashboard">首页看板</el-menu-item>
        <el-menu-item index="/container">集装箱管理</el-menu-item>
        <el-menu-item index="/yard">堆场调度</el-menu-item>
    </el-menu>
    <router-view />
</template>

<script setup lang="ts">
// 无需额外代码
</script>