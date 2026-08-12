<template>
  <div class="truck-page">
    <div class="page-header">
      <h2>集卡调度管理</h2>
      <el-button type="primary" @click="showAddDialog = true">新增集卡</el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total || 0 }}</div>
        <div class="stat-label">集卡总数</div>
      </div>
      <div class="stat-card idle">
        <div class="stat-value">{{ stats.idle || 0 }}</div>
        <div class="stat-label">空闲</div>
      </div>
      <div class="stat-card working">
        <div class="stat-value">{{ stats.working || 0 }}</div>
        <div class="stat-label">运输中</div>
      </div>
      <div class="stat-card repair">
        <div class="stat-value">{{ stats.repair || 0 }}</div>
        <div class="stat-label">维修中</div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input v-model="filterPlateNo" placeholder="车牌号" clearable style="width: 180px" @keyup.enter="loadData" />
      <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 140px">
        <el-option label="空闲" :value="0" />
        <el-option label="运输中" :value="1" />
        <el-option label="装卸中" :value="2" />
        <el-option label="维修中" :value="3" />
        <el-option label="离线" :value="4" />
      </el-select>
      <el-button type="primary" @click="loadData">查询</el-button>
      <el-button @click="resetFilter">重置</el-button>
    </div>

    <!-- 表格区域：铺满剩余屏幕 -->
    <div class="table-wrapper">
      <el-table :data="tableData" border stripe height="100%" v-loading="loading" style="width: 100%">
        <el-table-column prop="plateNo" label="车牌号" width="110" />
        <el-table-column prop="driverName" label="司机" width="90" />
        <el-table-column prop="driverPhone" label="联系电话" width="130" />
        <el-table-column label="类型" width="80">
          <template #default="{ row }">
            <el-tag :type="row.truckType === 1 ? 'primary' : 'success'" size="small">
              {{ row.truckType === 1 ? '内集卡' : '外集卡' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="currentContainerNo" label="当前箱号" width="140" />
        <el-table-column prop="startLocation" label="起点" min-width="120" />
        <el-table-column prop="targetLocation" label="目标位置" min-width="130" />
        <el-table-column prop="todayTaskCount" label="今日任务" width="90" />
        <el-table-column prop="totalMileage" label="总里程(km)" width="110" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="openAssign(row)" :disabled="row.status !== 0">派单</el-button>
            <el-button size="small" type="success" link @click="handleFinish(row)" :disabled="row.status === 0 || row.status === 3">完成</el-button>
            <el-button size="small" type="warning" link @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="pageNum"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 30, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="showAddDialog" :title="editId ? '编辑集卡' : '新增集卡'" width="500px">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="车牌号">
          <el-input v-model="formData.plateNo" />
        </el-form-item>
        <el-form-item label="司机姓名">
          <el-input v-model="formData.driverName" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="formData.driverPhone" />
        </el-form-item>
        <el-form-item label="集卡类型">
          <el-select v-model="formData.truckType" style="width: 100%">
            <el-option label="内集卡" :value="1" />
            <el-option label="外集卡" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="formData.status" style="width: 100%">
            <el-option label="空闲" :value="0" />
            <el-option label="运输中" :value="1" />
            <el-option label="装卸中" :value="2" />
            <el-option label="维修中" :value="3" />
            <el-option label="离线" :value="4" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 派单对话框 -->
    <el-dialog v-model="showAssignDialog" title="派单" width="450px">
      <el-form :model="assignForm" label-width="100px">
        <el-form-item label="集卡车牌">
          <el-input :model-value="assignForm.plateNo" disabled />
        </el-form-item>
        <el-form-item label="集装箱号">
          <el-input v-model="assignForm.containerNo" placeholder="请输入集装箱号" />
        </el-form-item>
        <el-form-item label="目标位置">
          <el-input v-model="assignForm.targetLocation" placeholder="如：1号泊位 / A区-01-01" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAssignDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAssign">确认派单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getTruckList, getTruckStats, addTruck, updateTruck, deleteTruck, assignTruck, finishTruck
} from '@/api/truck'
import type { TruckItem } from '@/api/truck'

const loading = ref(false)
const tableData = ref<TruckItem[]>([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(20)
const stats = ref<Record<string, number>>({})

const filterPlateNo = ref('')
const filterStatus = ref<number | undefined>(undefined)

const showAddDialog = ref(false)
const editId = ref<number | null>(null)
const formData = ref<Partial<TruckItem>>({ plateNo: '', driverName: '', driverPhone: '', truckType: 1, status: 0 })

const showAssignDialog = ref(false)
const assignForm = ref({ truckId: 0, plateNo: '', containerNo: '', targetLocation: '' })

const statusText = (s: number) => ['空闲', '运输中', '装卸中', '维修中', '离线'][s] || '未知'
const statusTagType = (s: number) => ['info', 'primary', 'warning', 'danger', 'info'][s] || 'info'

const loadData = async () => {
  loading.value = true
  try {
    const res: any = await getTruckList(pageNum.value, pageSize.value, filterPlateNo.value || undefined, filterStatus.value)
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

const loadStats = async () => {
  try {
    const res: any = await getTruckStats()
    stats.value = res?.data || res || {}
  } catch (e) {
    stats.value = {}
  }
}

const resetFilter = () => {
  filterPlateNo.value = ''
  filterStatus.value = undefined
  pageNum.value = 1
  loadData()
}

const openEdit = (row: TruckItem) => {
  editId.value = row.id
  formData.value = { ...row }
  showAddDialog.value = true
}

const handleSave = async () => {
  if (!formData.value.plateNo) {
    ElMessage.warning('请输入车牌号')
    return
  }
  try {
    if (editId.value) {
      await updateTruck(formData.value)
      ElMessage.success('编辑成功')
    } else {
      await addTruck(formData.value)
      ElMessage.success('新增成功')
    }
    showAddDialog.value = false
    loadData()
    loadStats()
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  }
}

const handleDelete = async (row: TruckItem) => {
  try {
    await ElMessageBox.confirm(`确认删除集卡 ${row.plateNo}？`, '提示', { type: 'warning' })
    await deleteTruck(row.id)
    ElMessage.success('删除成功')
    loadData()
    loadStats()
  } catch (e) { /* cancel */ }
}

const openAssign = (row: TruckItem) => {
  assignForm.value = { truckId: row.id, plateNo: row.plateNo, containerNo: '', targetLocation: '' }
  showAssignDialog.value = true
}

const handleAssign = async () => {
  if (!assignForm.value.containerNo || !assignForm.value.targetLocation) {
    ElMessage.warning('请填写集装箱号和目标位置')
    return
  }
  try {
    await assignTruck(assignForm.value)
    ElMessage.success('派单成功')
    showAssignDialog.value = false
    loadData()
    loadStats()
  } catch (e: any) {
    ElMessage.error(e?.message || '派单失败')
  }
}

const handleFinish = async (row: TruckItem) => {
  try {
    await finishTruck(row.id)
    ElMessage.success('任务已完成')
    loadData()
    loadStats()
  } catch (e: any) {
    ElMessage.error(e?.message || '操作失败')
  }
}

onMounted(() => {
  loadData()
  loadStats()
})
</script>

<style scoped>
.truck-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 16px 20px;
  box-sizing: border-box;
  overflow: hidden;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-shrink: 0;
}
.page-header h2 {
  margin: 0;
  color: #11616B;
}
.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  flex-shrink: 0;
}
.stat-card {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stat-card .stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #11616B;
}
.stat-card.idle .stat-value { color: #67C23A; }
.stat-card.working .stat-value { color: #409EFF; }
.stat-card.repair .stat-value { color: #F56C6C; }
.stat-card .stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}
.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
  align-items: center;
  flex-shrink: 0;
}
.table-wrapper {
  flex: 1;
  min-height: 0;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}
.pagination-bar {
  display: flex;
  justify-content: flex-end;
  padding-top: 12px;
  flex-shrink: 0;
}
</style>
