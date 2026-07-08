<template>
    <div class="container-wrap">
        <h1 align="center">集装箱信息管理</h1>
        <table border="1" width="100%" cellpadding="6">
            <thead>
            <tr>
                <th>箱号</th>
                <th>货物类型</th>
                <th>目的港口</th>
                <th>重量</th>
                <th>状态</th>
                <th>堆场仓位</th>
                <th>操作</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="row in tableData" :key="row.id">
                <td>{{ row.containerNo }}</td>
                <td>{{ row.cargoType }}</td>
                <td>{{ row.destPort }}</td>
                <td>{{ row.weight }}</td>
                <td>{{ row.status === 0 ? '未入库' : row.status === 1 ? '已分配仓位' : '已损坏锁定' }}</td>
                <td>{{ row.yardSlotId || '暂无' }}</td>
                <td>
                    <button @click="handleAllocate(row.containerNo)">分配堆场</button>
                    <button @click="handleDamage(row.containerNo)">标记损坏</button>
                </td>
            </tr>
            </tbody>
        </table>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getContainerList, autoAllocateYard, markDamageContainer } from '../api/container'

const tableData = ref<any[]>([])

const loadList = async () => {
    const res = await getContainerList({ pageNum: 1, pageSize: 10 })
    if (res.code === 200) {
        tableData.value = res.data.records
    }
}

const handleAllocate = async (no: string) => {
    await autoAllocateYard(no)
    loadList()
}

const handleDamage = async (no: string) => {
    await markDamageContainer(no)
    loadList()
}

onMounted(() => {
    loadList()
})
</script>