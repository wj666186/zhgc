<template>
    <!-- 外层盒子占满路由页面区域 -->
    <div class="dashboard-wrap">
        <img class="port-bg" src="@/assets/glt.png" alt="智慧港口首页看板" />
    </div>
</template>

<script setup lang="ts">
// 无业务逻辑可留空
</script>

<style scoped>
.dashboard-wrap {
    width: 100%;
    /* 自适应除去顶部标签栏剩余高度 */
    height: calc(100vh - 55px);
}
.port-bg {
    width: 100%;
    height: 100%;
    /* 图片不变形、铺满容器 */
    object-fit: cover;
    display: block;
}
</style>