<template>
    <router-view />
</template>

<script setup>
</script>

<style>
/* 重置所有默认边距 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* 整个浏览器视口铺满背景图1.png */
html,
body,
#app {
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    margin: 0;
    padding: 0;
    /* 全局背景图，填满整个浏览器屏幕（包含左右两端空白） */
    background-image: url('@/assets/1.png');
    background-repeat: no-repeat;
    background-position: center center;
    background-size: cover;
}
</style>
