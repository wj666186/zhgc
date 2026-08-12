<template>
  <div class="vessel-page">
    <div class="page-header">
      <h2>船舶计划管理</h2>
      <el-button type="primary" @click="openAdd">新增计划</el-button>
    </div>

    <div class="filter-bar">
      <el-input v-model="filterVesselName" placeholder="船名" clearable style="width: 200px" @keyup.enter="loadData" />
      <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 140px">
        <el-option label="待靠泊" :value="0" />
        <el-option label="作业中" :value="1" />
        <el-option label="完成待离港" :value="2" />
        <el-option label="已离港" :value="3" />
        <el-option label="已取消" :value="4" />
      </el-select>
      <el-button type="primary" @click="loadData">查询</el-button>
      <el-button @click="resetFilter">重置</el-button>
    </div>

    <div class="table-wrapper">
      <el-table :data="tableData" border stripe height="100%" v-loading="loading" style="width: 100%">
        <el-table-column prop="vesselName" label="船名" width="160" />
        <el-table-column prop="imoNo" label="IMO号" width="110" />
        <el-table-column prop="shippingCompany" label="船公司" min-width="140" />
        <el-table-column prop="routeLine" label="航线" min-width="150" />
        <el-table-column prop="berthNo" label="泊位" width="70" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="berthWindowStart" label="计划靠泊" width="160" />
        <el-table-column prop="actualBerthTime" label="实际靠泊" width="160" />
        <el-table-column prop="totalContainer" label="总箱量" width="80" />
        <el-table-column label="完成进度" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.totalContainer ? Math.round(row.finishedContainer / row.totalContainer * 100) : 0" :stroke-width="12" />
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="调度员" width="80" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 0" size="small" type="primary" link @click="handleBerth(row)">靠泊</el-button>
            <el-button v-if="row.status === 1" size="small" type="success" link @click="handleFinish(row)">完成</el-button>
            <el-button v-if="row.status === 2" size="small" type="info" link @click="handleDeparture(row)">离港</el-button>
            <el-button v-if="row.status === 0" size="small" type="warning" link @click="handleCancel(row)">取消</el-button>
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

    <el-dialog v-model="showDialog" :title="editId ? '编辑船舶计划' : '新增船舶计划'" width="600px">
      <el-form :model="formData" label-width="110px">
        <el-form-item label="船名">
          <el-input v-model="formData.vesselName" />
        </el-form-item>
        <el-form-item label="IMO号">
          <el-input v-model="formData.imoNo" />
        </el-form-item>
        <el-form-item label="船公司">
          <el-input v-model="formData.shippingCompany" />
        </el-form-item>
        <el-form-item label="航线">
          <el-input v-model="formData.routeLine" />
        </el-form-item>
        <el-form-item label="泊位">
          <el-input v-model="formData.berthNo" placeholder="如 B1" />
        </el-form-item>
        <el-form-item label="总箱量">
          <el-input-number v-model="formData.totalContainer" :min="0" />
        </el-form-item>
        <el-form-item label="计划靠泊">
          <el-date-picker v-model="formData.berthWindowStart" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="计划离港">
          <el-date-picker v-model="formData.berthWindowEnd" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="formData.status" style="width: 100%">
            <el-option label="待靠泊" :value="0" />
            <el-option label="作业中" :value="1" />
            <el-option label="完成待离港" :value="2" />
            <el-option label="已离港" :value="3" />
            <el-option label="已取消" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getVesselList, addVessel, updateVessel, deleteVessel,
  berthVessel, finishVessel, departureVessel, cancelVessel
} from '@/api/vessel'
import type { VesselPlanItem } from '@/api/vessel'

const loading = ref(false)
const tableData = ref<VesselPlanItem[]>([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(20)

const filterVesselName = ref('')
const filterStatus = ref<number | undefined>(undefined)

const showDialog = ref(false)
const editId = ref<number | null>(null)
const formData = ref<Partial<VesselPlanItem>>({
  vesselName: '', imoNo: '', shippingCompany: '', routeLine: '', berthNo: '',
  totalContainer: 0, finishedContainer: 0, status: 0, remark: ''
})

const statusText = (s: number) => ['待靠泊', '作业中', '完成待离港', '已离港', '已取消'][s] || '未知'
const statusTagType = (s: number) => ['warning', 'primary', 'success', 'info', 'danger'][s] || 'info'

const loadData = async () => {
  loading.value = true
  try {
    const res: any = await getVesselList(pageNum.value, pageSize.value, filterVesselName.value || undefined, filterStatus.value)
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

const resetFilter = () => {
  filterVesselName.value = ''
  filterStatus.value = undefined
  pageNum.value = 1
  loadData()
}

const openAdd = () => {
  editId.value = null
  formData.value = { vesselName: '', imoNo: '', shippingCompany: '', routeLine: '', berthNo: '', totalContainer: 0, finishedContainer: 0, status: 0, remark: '' }
  showDialog.value = true
}

const openEdit = (row: VesselPlanItem) => {
  editId.value = row.id
  formData.value = { ...row }
  showDialog.value = true
}

const handleSave = async () => {
  if (!formData.value.vesselName) {
    ElMessage.warning('请输入船名')
    return
  }
  try {
    if (editId.value) {
      await updateVessel(formData.value)
      ElMessage.success('编辑成功')
    } else {
      await addVessel(formData.value)
      ElMessage.success('新增成功')
    }
    showDialog.value = false
    loadData()
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  }
}

const handleDelete = async (row: VesselPlanItem) => {
  try {
    await ElMessageBox.confirm(`确认删除船舶计划 ${row.vesselName}？`, '提示', { type: 'warning' })
    await deleteVessel(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) { /* cancel */ }
}

const handleBerth = async (row: VesselPlanItem) => {
  try { await berthVessel(row.id); ElMessage.success('靠泊确认成功'); loadData() } catch (e: any) { ElMessage.error(e?.message || '操作失败') }
}
const handleFinish = async (row: VesselPlanItem) => {
  try { await finishVessel(row.id); ElMessage.success('作业完成'); loadData() } catch (e: any) { ElMessage.error(e?.message || '操作失败') }
}
const handleDeparture = async (row: VesselPlanItem) => {
  try { await departureVessel(row.id); ElMessage.success('离港确认成功'); loadData() } catch (e: any) { ElMessage.error(e?.message || '操作失败') }
}
const handleCancel = async (row: VesselPlanItem) => {
  try {
    await ElMessageBox.confirm(`确认取消船舶计划 ${row.vesselName}？`, '提示', { type: 'warning' })
    await cancelVessel(row.id); ElMessage.success('已取消'); loadData()
  } catch (e) { /* cancel */ }
}

onMounted(() => loadData())
</script>

<style scoped>
.vessel-page {
  display: flex; flex-direction: column; height: 100vh; padding: 16px 20px; box-sizing: border-box; overflow: hidden;
}
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-shrink: 0; }
.page-header h2 { margin: 0; color: #11616B; }
.filter-bar { display: flex; gap: 10px; margin-bottom: 12px; align-items: center; flex-shrink: 0; }
.table-wrapper { flex: 1; min-height: 0; background: #fff; border-radius: 8px; overflow: hidden; }
.pagination-bar { display: flex; justify-content: flex-end; padding-top: 12px; flex-shrink: 0; }
</style>
