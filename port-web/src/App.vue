<template>
    <router-view />
</template>

<script setup>
</script>

<style>
/* 全局重置 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html,
body,
#app {
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    margin: 0;
    padding: 0;
}

body {
    background: #f0f4f8;
}
</style>
