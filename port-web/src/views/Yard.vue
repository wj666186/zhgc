<template>
    <el-menu mode="horizontal" router style="margin-bottom: 20px;">
        <el-menu-item index="/dashboard">首页看板</el-menu-item>
        <el-menu-item index="/container">集装箱管理</el-menu-item>
        <el-menu-item index="/yard">堆场调度</el-menu-item>
        <!-- 新增AI智能识别菜单 -->
        <el-menu-item index="/aiRecognition">AI智能识别</el-menu-item>
    </el-menu>
</template>

<script setup lang="ts">
// 无需额外代码
</script>