<template>
    <div class="dashboard-wrap">
        <div class="bg-box"></div>
    </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.dashboard-wrap {
    width: 100%;
    max-width: 100%;
    height: 100%;
    padding: 0;
    box-sizing: border-box;
    background-color: transparent;
    overflow-x: hidden;
}
.bg-box {
    width: 100%;
    height: 100%;
    min-height: 100vh;
    background: url('@/assets/glt.png') no-repeat center center;
    background-size: cover;
}
</style>
