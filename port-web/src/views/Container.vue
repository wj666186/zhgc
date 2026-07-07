<template>
    <div style="padding: 20px;">
        <h2>集装箱信息管理</h2>
        <el-table :data="tableData" border style="width: 100%; margin-top: 16px;">
            <el-table-column label="箱号" prop="containerNo" />
            <el-table-column label="货物类型" prop="cargoType" />
            <el-table-column label="目的港口" prop="destPort" />
            <el-table-column label="重量" prop="weight" />
            <el-table-column label="状态" prop="status" />
            <el-table-column label="堆场仓位" prop="yardSlotCode" />
            <el-table-column label="操作">
                <template #default="scope">
                    <el-button type="primary" size="small" @click="allocate(scope.row.containerNo)">分配堆场</el-button>
                    <el-button type="danger" size="small" @click="lockDamage(scope.row.containerNo)">标记损坏</el-button>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
// 务必确认顶部导入了这三个接口
import { getContainerList, autoAllocateYard, markDamageContainer } from '../api/container'

// 正确写法，ref初始值直接写[]
const tableData = ref<any[]>([])

// 加载列表
const loadList = async () => {
    // 删掉多余的 params:
    const res = await getContainerList({ pageNum: 1, pageSize: 30 })
    tableData.value = res.res || []
}

// 分配堆场
const allocate = async (no: string) => {
    await autoAllocateYard(no)
    await loadList()
}

// 标记损坏
const lockDamage = async (no: string) => {
    await markDamageContainer(no)
    await loadList()
}

onMounted(loadList)
</script>