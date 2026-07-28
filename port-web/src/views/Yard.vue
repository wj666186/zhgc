<template>
    <!-- 增加自定义样式类，修改菜单底色、文字颜色 -->
    <el-menu
        mode="horizontal"
        router
        class="top-nav-menu"
        style="margin-bottom: 20px;"
    >
        <el-menu-item index="/dashboard">首页看板</el-menu-item>
        <el-menu-item index="/container">集装箱管理</el-menu-item>
        <el-menu-item index="/yard">堆场调度</el-menu-item>
        <el-menu-item index="/aiRecognition">AI智能识别</el-menu-item>
        <el-menu-item index="/digitalTwin">数字孪生时空视图</el-menu-item>
    </el-menu>
</template>

<script setup lang="ts">
// 无需额外逻辑代码
</script>

<style scoped>
/* 顶层导航菜单全局样式 */
:deep(.top-nav-menu) {
    /* 半透明白色，透出下方背景图 */
    background-color: rgba(255, 255, 255, 0.25);
    border-bottom: none;
}

/* 菜单项默认文字颜色 */
:deep(.top-nav-menu .el-menu-item) {
    color: #11616B;
    font-size: 16px;
}

/* 鼠标悬浮菜单项样式 */
:deep(.top-nav-menu .el-menu-item:hover) {
    background-color: rgba(123, 189, 182, 0.4);
    color: #08383f;
}

/* 当前路由激活选中样式（和侧边栏选中色调统一） */
:deep(.top-nav-menu .el-menu-item.is-active) {
    background-color: rgba(123, 189, 182, 0.55);
    color: #11616B;
    font-weight: 500;
}
</style>
