<template>
  <div class="gate-page">
    <div class="page-header">
      <h2>闸口无感通行管理</h2>
      <el-button type="primary" @click="showVerifyDialog = true">进港核验</el-button>
    </div>

    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ stats.todayTotal || 0 }}</div>
        <div class="stat-label">今日通行</div>
      </div>
      <div class="stat-card pass">
        <div class="stat-value">{{ stats.todayPass || 0 }}</div>
        <div class="stat-label">放行</div>
      </div>
      <div class="stat-card fail">
        <div class="stat-value">{{ stats.todayFail || 0 }}</div>
        <div class="stat-label">拦截</div>
      </div>
      <div class="stat-card inport">
        <div class="stat-value">{{ stats.inPort || 0 }}</div>
        <div class="stat-label">在场</div>
      </div>
    </div>

    <div class="filter-bar">
      <el-input v-model="filterPlateNo" placeholder="车牌号" clearable style="width: 160px" @keyup.enter="loadData" />
      <el-input v-model="filterContainerNo" placeholder="集装箱号" clearable style="width: 180px" @keyup.enter="loadData" />
      <el-select v-model="filterDirection" placeholder="方向" clearable style="width: 120px">
        <el-option label="进港" :value="1" />
        <el-option label="出港" :value="2" />
      </el-select>
      <el-select v-model="filterVerifyStatus" placeholder="核验状态" clearable style="width: 120px">
        <el-option label="待核验" :value="0" />
        <el-option label="通过" :value="1" />
        <el-option label="拦截" :value="2" />
      </el-select>
      <el-button type="primary" @click="loadData">查询</el-button>
      <el-button @click="resetFilter">重置</el-button>
    </div>

    <div class="table-wrapper">
      <el-table :data="tableData" border stripe height="100%" v-loading="loading" style="width: 100%">
        <el-table-column prop="passNo" label="通行单号" min-width="180" />
        <el-table-column prop="gateNo" label="闸口" width="70" />
        <el-table-column label="方向" width="70">
          <template #default="{ row }">
            <el-tag :type="row.direction === 1 ? 'primary' : 'success'" size="small">{{ row.direction === 1 ? '进港' : '出港' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="plateNo" label="车牌号" width="110" />
        <el-table-column prop="containerNo" label="集装箱号" min-width="140" />
        <el-table-column label="ETC" width="60">
          <template #default="{ row }">
            <el-tag :type="row.etcResult === 1 ? 'success' : 'danger'" size="small">{{ row.etcResult === 1 ? '通过' : '异常' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="RFID" width="60">
          <template #default="{ row }">
            <el-tag :type="row.rfidResult === 1 ? 'success' : 'danger'" size="small">{{ row.rfidResult === 1 ? '通过' : '异常' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="海关" width="60">
          <template #default="{ row }">
            <el-tag :type="row.customsStatus === 1 ? 'success' : 'warning'" size="small">{{ row.customsStatus === 1 ? '放行' : '未放' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="核验" width="70">
          <template #default="{ row }">
            <el-tag :type="row.verifyStatus === 1 ? 'success' : row.verifyStatus === 2 ? 'danger' : 'warning'" size="small">
              {{ ['待核验', '通过', '拦截'][row.verifyStatus] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enterTime" label="进港时间" width="160" />
        <el-table-column prop="exitTime" label="出港时间" width="160" />
        <el-table-column prop="stayMinutes" label="停留(分)" width="80" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="success" link @click="handleExit(row)" :disabled="row.direction === 2 || row.exitTime">出港</el-button>
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
        :page-sizes="[10, 20, 30, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>

    <!-- 进港核验对话框 -->
    <el-dialog v-model="showVerifyDialog" title="进港核验（ETC+RFID+OCR三合一）" width="450px">
      <el-form :model="verifyForm" label-width="100px">
        <el-form-item label="车牌号">
          <el-input v-model="verifyForm.plateNo" placeholder="请输入车牌号" />
        </el-form-item>
        <el-form-item label="集装箱号">
          <el-input v-model="verifyForm.containerNo" placeholder="请输入集装箱号" />
        </el-form-item>
        <el-form-item label="预约单号">
          <el-input v-model="verifyForm.appointmentNo" placeholder="请输入预约单号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showVerifyDialog = false">取消</el-button>
        <el-button type="primary" @click="handleVerify">开始核验</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getGateList, getGateStats, verifyGate, exitGate, deleteGate } from '@/api/gate'
import type { GateRecordItem } from '@/api/gate'

const loading = ref(false)
const tableData = ref<GateRecordItem[]>([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(20)
const stats = ref<Record<string, number>>({})

const filterPlateNo = ref('')
const filterContainerNo = ref('')
const filterDirection = ref<number | undefined>(undefined)
const filterVerifyStatus = ref<number | undefined>(undefined)

const showVerifyDialog = ref(false)
const verifyForm = ref({ plateNo: '', containerNo: '', appointmentNo: '' })

const loadData = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {}
    if (filterPlateNo.value) params.plateNo = filterPlateNo.value
    if (filterContainerNo.value) params.containerNo = filterContainerNo.value
    if (filterDirection.value !== undefined) params.direction = filterDirection.value
    if (filterVerifyStatus.value !== undefined) params.verifyStatus = filterVerifyStatus.value
    const res: any = await getGateList(pageNum.value, pageSize.value, params)
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
    const res: any = await getGateStats()
    stats.value = res?.data || res || {}
  } catch (e) {
    stats.value = {}
  }
}

const resetFilter = () => {
  filterPlateNo.value = ''
  filterContainerNo.value = ''
  filterDirection.value = undefined
  filterVerifyStatus.value = undefined
  pageNum.value = 1
  loadData()
}

const handleVerify = async () => {
  if (!verifyForm.value.plateNo) {
    ElMessage.warning('请输入车牌号')
    return
  }
  try {
    const res: any = await verifyGate(verifyForm.value)
    if (res && res.verifyStatus === 1) {
      ElMessage.success('核验通过，已放行')
    } else if (res && res.verifyStatus === 2) {
      ElMessage.warning('核验未通过，已拦截')
    } else {
      ElMessage.success('核验完成')
    }
    showVerifyDialog.value = false
    verifyForm.value = { plateNo: '', containerNo: '', appointmentNo: '' }
    loadData()
    loadStats()
  } catch (e: any) {
    ElMessage.error(e?.message || '核验失败')
  }
}

const handleExit = async (row: GateRecordItem) => {
  try {
    await exitGate(row.id)
    ElMessage.success('出港登记成功')
    loadData()
    loadStats()
  } catch (e: any) {
    ElMessage.error(e?.message || '操作失败')
  }
}

const handleDelete = async (row: GateRecordItem) => {
  try {
    await ElMessageBox.confirm(`确认删除通行记录 ${row.passNo}？`, '提示', { type: 'warning' })
    await deleteGate(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) { /* cancel */ }
}

onMounted(() => {
  loadData()
  loadStats()
})
</script>

<style scoped>
.gate-page {
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
.page-header h2 { margin: 0; color: #11616B; }
.stats-row { display: flex; gap: 16px; margin-bottom: 12px; flex-shrink: 0; }
.stat-card {
  flex: 1; background: #fff; border-radius: 8px; padding: 16px; text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stat-card .stat-value { font-size: 28px; font-weight: bold; color: #11616B; }
.stat-card.pass .stat-value { color: #67C23A; }
.stat-card.fail .stat-value { color: #F56C6C; }
.stat-card.inport .stat-value { color: #E6A23C; }
.stat-card .stat-label { font-size: 14px; color: #909399; margin-top: 4px; }
.filter-bar { display: flex; gap: 10px; margin-bottom: 12px; align-items: center; flex-wrap: wrap; flex-shrink: 0; }
.table-wrapper { flex: 1; min-height: 0; background: #fff; border-radius: 8px; overflow: hidden; }
.pagination-bar { display: flex; justify-content: flex-end; padding-top: 12px; flex-shrink: 0; }
</style>
