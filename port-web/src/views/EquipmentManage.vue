<template>
  <div class="equipment-page">
    <div class="page-header">
      <h2>设备管控</h2>
      <el-button type="primary" @click="openAdd">{{ activeTab === 'crane' ? '新增岸桥' : '新增龙门吊' }}</el-button>
    </div>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="岸桥" name="crane" />
      <el-tab-pane label="龙门吊" name="rtg" />
    </el-tabs>

    <div class="filter-bar">
      <el-input v-model="filterNo" :placeholder="activeTab === 'crane' ? '岸桥编号' : '龙门吊编号'" clearable style="width: 160px" @keyup.enter="loadData" />
      <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 120px">
        <el-option label="离线" :value="0" />
        <el-option label="空闲" :value="1" />
        <el-option label="作业中" :value="2" />
        <el-option label="故障" :value="3" />
        <el-option label="维护" :value="4" />
      </el-select>
      <el-button type="primary" @click="loadData">查询</el-button>
      <el-button @click="resetFilter">重置</el-button>
    </div>

    <div class="table-wrapper">
      <!-- 岸桥表格 -->
      <el-table v-if="activeTab === 'crane'" :data="craneData" border stripe height="100%" v-loading="loading" style="width: 100%">
        <el-table-column prop="craneNo" label="岸桥编号" width="100" />
        <el-table-column prop="berthNo" label="泊位" width="70" />
        <el-table-column prop="model" label="型号" min-width="140" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="操作员" width="80" />
        <el-table-column prop="currentVessel" label="当前船舶" min-width="140" />
        <el-table-column prop="trolleyPosition" label="小车位置" width="90" />
        <el-table-column prop="liftHeight" label="起升高度" width="90" />
        <el-table-column prop="todayBoxCount" label="今日箱量" width="80" />
        <el-table-column label="OEE" width="120">
          <template #default="{ row }">
            <el-progress :percentage="Math.round(row.oee)" :stroke-width="10" :color="row.oee >= 85 ? '#67C23A' : row.oee >= 70 ? '#E6A23C' : '#F56C6C'" />
          </template>
        </el-table-column>
        <el-table-column prop="faultDesc" label="故障描述" min-width="150" show-overflow-tooltip />
        <el-table-column prop="lastHeartbeat" label="最后心跳" width="160" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 1" size="small" type="primary" link @click="openStart(row)">启动</el-button>
            <el-button v-if="row.status === 2" size="small" type="success" link @click="handleFinish(row)">完成</el-button>
            <el-button size="small" type="warning" link @click="openFault(row)">故障</el-button>
            <el-button size="small" type="info" link @click="handleHeartbeat(row)">心跳</el-button>
            <el-button size="small" type="primary" link @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 龙门吊表格 -->
      <el-table v-else :data="rtgData" border stripe height="100%" v-loading="loading" style="width: 100%">
        <el-table-column prop="rtgNo" label="龙门吊编号" width="110" />
        <el-table-column prop="yardArea" label="堆场" width="70" />
        <el-table-column prop="model" label="型号" min-width="140" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="操作员" width="80" />
        <el-table-column prop="currentContainerNo" label="当前箱号" min-width="140" />
        <el-table-column prop="currentRow" label="当前排" width="70" />
        <el-table-column prop="currentCol" label="当前列" width="70" />
        <el-table-column prop="liftHeight" label="起升高度" width="90" />
        <el-table-column prop="todayBoxCount" label="今日箱量" width="80" />
        <el-table-column label="OEE" width="120">
          <template #default="{ row }">
            <el-progress :percentage="Math.round(row.oee)" :stroke-width="10" :color="row.oee >= 85 ? '#67C23A' : row.oee >= 70 ? '#E6A23C' : '#F56C6C'" />
          </template>
        </el-table-column>
        <el-table-column prop="faultDesc" label="故障描述" min-width="150" show-overflow-tooltip />
        <el-table-column prop="lastHeartbeat" label="最后心跳" width="160" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 1" size="small" type="primary" link @click="openStart(row)">启动</el-button>
            <el-button v-if="row.status === 2" size="small" type="success" link @click="handleFinish(row)">完成</el-button>
            <el-button size="small" type="warning" link @click="openFault(row)">故障</el-button>
            <el-button size="small" type="info" link @click="handleHeartbeat(row)">心跳</el-button>
            <el-button size="small" type="primary" link @click="openEdit(row)">编辑</el-button>
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

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="showDialog" :title="editId ? '编辑' : '新增'" width="550px">
      <el-form :model="formData" label-width="110px">
        <el-form-item :label="activeTab === 'crane' ? '岸桥编号' : '龙门吊编号'">
          <el-input v-model="formData.equipNo" />
        </el-form-item>
        <el-form-item :label="activeTab === 'crane' ? '泊位' : '堆场'">
          <el-input v-model="formData.location" />
        </el-form-item>
        <el-form-item label="型号">
          <el-input v-model="formData.model" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="formData.status" style="width: 100%">
            <el-option label="离线" :value="0" />
            <el-option label="空闲" :value="1" />
            <el-option label="作业中" :value="2" />
            <el-option label="故障" :value="3" />
            <el-option label="维护" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作员">
          <el-input v-model="formData.operator" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 启动对话框 -->
    <el-dialog v-model="showStartDialog" title="启动作业" width="400px">
      <el-form :model="startForm" label-width="100px">
        <el-form-item :label="activeTab === 'crane' ? '当前船舶' : '集装箱号'">
          <el-input v-model="startForm.target" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showStartDialog = false">取消</el-button>
        <el-button type="primary" @click="handleStart">确认启动</el-button>
      </template>
    </el-dialog>

    <!-- 故障对话框 -->
    <el-dialog v-model="showFaultDialog" title="故障上报" width="400px">
      <el-form :model="faultForm" label-width="100px">
        <el-form-item label="故障描述">
          <el-input v-model="faultForm.faultDesc" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFaultDialog = false">取消</el-button>
        <el-button type="warning" @click="handleFault">上报故障</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getCraneList, addCrane, updateCrane, deleteCrane, startCrane, finishCrane, faultCrane, heartbeatCrane,
  getRtgList, addRtg, updateRtg, deleteRtg, startRtg, finishRtg, faultRtg, heartbeatRtg
} from '@/api/equipment'
import type { QuayCraneItem, RtgItem } from '@/api/equipment'

const activeTab = ref('crane')
const loading = ref(false)
const craneData = ref<QuayCraneItem[]>([])
const rtgData = ref<RtgItem[]>([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(20)

const filterNo = ref('')
const filterStatus = ref<number | undefined>(undefined)

const showDialog = ref(false)
const editId = ref<number | null>(null)
const formData = ref<any>({})

const showStartDialog = ref(false)
const startForm = ref({ id: 0, target: '' })

const showFaultDialog = ref(false)
const faultForm = ref({ id: 0, faultDesc: '' })

const statusText = (s: number) => ['离线', '空闲', '作业中', '故障', '维护'][s] || '未知'
const statusTagType = (s: number) => ['info', 'success', 'primary', 'danger', 'warning'][s] || 'info'

const handleTabChange = () => {
  pageNum.value = 1
  filterNo.value = ''
  filterStatus.value = undefined
  loadData()
}

const loadData = async () => {
  loading.value = true
  try {
    if (activeTab.value === 'crane') {
      const res: any = await getCraneList(pageNum.value, pageSize.value, filterNo.value || undefined, filterStatus.value)
      const data = res?.data || res
      craneData.value = data?.records || data?.list || []
      total.value = data?.total || 0
    } else {
      const res: any = await getRtgList(pageNum.value, pageSize.value, filterNo.value || undefined, filterStatus.value)
      const data = res?.data || res
      rtgData.value = data?.records || data?.list || []
      total.value = data?.total || 0
    }
  } catch (e) {
    craneData.value = []
    rtgData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterNo.value = ''
  filterStatus.value = undefined
  pageNum.value = 1
  loadData()
}

const openAdd = () => {
  editId.value = null
  formData.value = { status: 1, equipNo: '', location: '' }
  showDialog.value = true
}

const openEdit = (row: any) => {
  editId.value = row.id
  formData.value = {
    ...row,
    equipNo: row.craneNo || row.rtgNo || '',
    location: row.berthNo || row.yardArea || ''
  }
  showDialog.value = true
}

const handleSave = async () => {
  try {
    const submitData = { ...formData.value }
    if (activeTab.value === 'crane') {
      submitData.craneNo = submitData.equipNo
      submitData.berthNo = submitData.location
      delete submitData.equipNo
      delete submitData.location
      if (editId.value) { await updateCrane(submitData); ElMessage.success('编辑成功') }
      else { await addCrane(submitData); ElMessage.success('新增成功') }
    } else {
      submitData.rtgNo = submitData.equipNo
      submitData.yardArea = submitData.location
      delete submitData.equipNo
      delete submitData.location
      if (editId.value) { await updateRtg(submitData); ElMessage.success('编辑成功') }
      else { await addRtg(submitData); ElMessage.success('新增成功') }
    }
    showDialog.value = false
    loadData()
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  }
}

const handleDelete = async (row: any) => {
  try {
    const name = activeTab.value === 'crane' ? row.craneNo : row.rtgNo
    await ElMessageBox.confirm(`确认删除 ${name}？`, '提示', { type: 'warning' })
    if (activeTab.value === 'crane') { await deleteCrane(row.id) }
    else { await deleteRtg(row.id) }
    ElMessage.success('删除成功')
    loadData()
  } catch (e) { /* cancel */ }
}

const openStart = (row: any) => {
  startForm.value = { id: row.id, target: '' }
  showStartDialog.value = true
}

const handleStart = async () => {
  if (!startForm.value.target) { ElMessage.warning('请输入目标'); return }
  try {
    if (activeTab.value === 'crane') {
      await startCrane({ id: startForm.value.id, currentVessel: startForm.value.target })
    } else {
      await startRtg({ id: startForm.value.id, containerNo: startForm.value.target })
    }
    ElMessage.success('启动成功')
    showStartDialog.value = false
    loadData()
  } catch (e: any) { ElMessage.error(e?.message || '操作失败') }
}

const handleFinish = async (row: any) => {
  try {
    if (activeTab.value === 'crane') { await finishCrane(row.id) }
    else { await finishRtg(row.id) }
    ElMessage.success('作业完成')
    loadData()
  } catch (e: any) { ElMessage.error(e?.message || '操作失败') }
}

const openFault = (row: any) => {
  faultForm.value = { id: row.id, faultDesc: '' }
  showFaultDialog.value = true
}

const handleFault = async () => {
  if (!faultForm.value.faultDesc) { ElMessage.warning('请输入故障描述'); return }
  try {
    if (activeTab.value === 'crane') { await faultCrane(faultForm.value) }
    else { await faultRtg(faultForm.value) }
    ElMessage.success('故障已上报')
    showFaultDialog.value = false
    loadData()
  } catch (e: any) { ElMessage.error(e?.message || '操作失败') }
}

const handleHeartbeat = async (row: any) => {
  try {
    if (activeTab.value === 'crane') { await heartbeatCrane(row.id) }
    else { await heartbeatRtg(row.id) }
    ElMessage.success('心跳上报成功')
    loadData()
  } catch (e: any) { ElMessage.error(e?.message || '操作失败') }
}

onMounted(() => loadData())
</script>

<style scoped>
.equipment-page {
  display: flex; flex-direction: column; height: 100vh; padding: 16px 20px; box-sizing: border-box; overflow: hidden;
}
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-shrink: 0; }
.page-header h2 { margin: 0; color: #11616B; }
.filter-bar { display: flex; gap: 10px; margin-bottom: 12px; align-items: center; flex-shrink: 0; }
.table-wrapper { flex: 1; min-height: 0; background: #fff; border-radius: 8px; overflow: hidden; }
.pagination-bar { display: flex; justify-content: flex-end; padding-top: 12px; flex-shrink: 0; }
</style>
