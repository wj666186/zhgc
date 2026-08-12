<template>
  <div class="log-page">
    <div class="page-header">
      <h2>审计日志</h2>
    </div>

    <div class="filter-bar">
      <el-select v-model="filterModule" placeholder="模块" clearable style="width: 160px">
        <el-option v-for="m in modules" :key="m" :label="m" :value="m" />
      </el-select>
      <el-input v-model="filterUsername" placeholder="用户名" clearable style="width: 140px" @keyup.enter="loadData" />
      <el-select v-model="filterResult" placeholder="结果" clearable style="width: 120px">
        <el-option label="成功" :value="1" />
        <el-option label="失败" :value="0" />
      </el-select>
      <el-button type="primary" @click="loadData">查询</el-button>
      <el-button @click="resetFilter">重置</el-button>
    </div>

    <div class="table-wrapper">
      <el-table :data="tableData" border stripe height="100%" v-loading="loading" style="width: 100%">
        <el-table-column prop="logNo" label="日志编号" width="180" />
        <el-table-column prop="username" label="用户名" width="100" />
        <el-table-column prop="userRole" label="角色" width="80" />
        <el-table-column prop="module" label="模块" width="100" />
        <el-table-column prop="operation" label="操作" width="80" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="requestMethod" label="方法" width="70" />
        <el-table-column prop="requestUrl" label="URL" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ipAddress" label="IP地址" width="130" />
        <el-table-column label="结果" width="70">
          <template #default="{ row }">
            <el-tag :type="row.result === 1 ? 'success' : 'danger'" size="small">{{ row.result === 1 ? '成功' : '失败' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="errorMsg" label="错误信息" width="150" show-overflow-tooltip />
        <el-table-column prop="costMs" label="耗时(ms)" width="80" />
        <el-table-column prop="createTime" label="操作时间" width="160" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="pageNum"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 30, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getLogList, getLogModules, deleteLog } from '@/api/log'
import type { OperationLogItem } from '@/api/log'

const loading = ref(false)
const tableData = ref<OperationLogItem[]>([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(20)
const modules = ref<string[]>([])

const filterModule = ref('')
const filterUsername = ref('')
const filterResult = ref<number | undefined>(undefined)

const loadData = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {}
    if (filterModule.value) params.module = filterModule.value
    if (filterUsername.value) params.username = filterUsername.value
    if (filterResult.value !== undefined) params.result = filterResult.value
    const res: any = await getLogList(pageNum.value, pageSize.value, params)
    const data = res?.data || res
    tableData.value = data?.records || data?.list || []
    total.value = data?.total || 0
  } catch (e) {
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const loadModules = async () => {
  try {
    const res: any = await getLogModules()
    modules.value = res?.data || res || []
  } catch (e) {
    modules.value = []
  }
}

const resetFilter = () => {
  filterModule.value = ''
  filterUsername.value = ''
  filterResult.value = undefined
  pageNum.value = 1
  loadData()
}

const handleDelete = async (row: OperationLogItem) => {
  try {
    await ElMessageBox.confirm(`确认删除日志 ${row.logNo}？`, '提示', { type: 'warning' })
    await deleteLog(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) { /* cancel */ }
}

onMounted(() => {
  loadData()
  loadModules()
})
</script>

<style scoped>
.log-page {
  display: flex; flex-direction: column; height: 100%; padding: 16px 20px; box-sizing: border-box;
}
.page-header h2 { margin: 0 0 12px; color: #11616B; }
.filter-bar { display: flex; gap: 10px; margin-bottom: 12px; align-items: center; }
.table-wrapper { flex: 1; min-height: 0; background: #fff; border-radius: 8px; overflow: hidden; }
.pagination-bar { display: flex; justify-content: flex-end; padding-top: 12px; }
</style>
