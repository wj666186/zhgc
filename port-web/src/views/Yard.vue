<template>
  <div class="yard-page">
    <div class="page-header">
      <h2>堆场集装箱坐标调度管理</h2>
      <div class="header-actions">
        <el-radio-group v-model="currentArea" @change="handleAreaChange">
          <el-radio-button :value="1">A区</el-radio-button>
          <el-radio-button :value="2">B区</el-radio-button>
          <el-radio-button :value="3">C区</el-radio-button>
        </el-radio-group>
        <el-button type="primary" style="margin-left: 12px;" @click="loadData">刷新</el-button>
      </div>
    </div>

    <div class="content-row">
      <!-- 左侧：仓位网格 -->
      <div class="left-panel">
        <el-card class="grid-card">
          <template #header>
            <span style="font-weight: bold;">{{ areaName }} 仓位分布图 (6排 × 8列)</span>
          </template>
          <div class="yard-grid">
            <div class="grid-row" v-for="row in 6" :key="row">
              <div class="grid-label">{{ row }}排</div>
              <div
                v-for="col in 8"
                :key="col"
                class="grid-cell"
                :class="getCellClass(row, col)"
                @click="handleCellClick(row, col)"
              >
                <span class="cell-coord">{{ row }}-{{ col }}</span>
                <span v-if="getContainerAt(row, col)" class="cell-box">
                  {{ getContainerAt(row, col)?.containerNo?.slice(-4) }}
                </span>
              </div>
            </div>
          </div>
          <div class="legend">
            <span class="legend-item"><span class="legend-color empty"></span>空闲</span>
            <span class="legend-item"><span class="legend-color normal"></span>正常</span>
            <span class="legend-item"><span class="legend-color working"></span>作业中</span>
            <span class="legend-item"><span class="legend-color damage"></span>破损</span>
          </div>
        </el-card>
      </div>

      <!-- 右侧：集装箱坐标列表（铺满屏幕） -->
      <div class="right-panel">
        <el-card class="list-card">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: bold; font-size: 16px;">{{ areaName }} 集装箱坐标列表</span>
              <el-input v-model="searchNo" placeholder="箱号搜索" clearable style="width: 180px;" @keyup.enter="loadData" />
            </div>
          </template>
          <div class="table-wrapper">
            <el-table :data="filteredList" border stripe height="100%" v-loading="loading" style="width: 100%">
              <el-table-column prop="containerNo" label="箱号" width="140" />
              <el-table-column prop="cargoType" label="货物类型" min-width="120" />
              <el-table-column prop="destPort" label="目的港" min-width="110" />
              <el-table-column prop="weight" label="重量(吨)" width="90" />
              <el-table-column label="状态" width="90">
                <template #default="{ row }">
                  <el-tag :type="statusTagType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="坐标(X,Z)" width="120">
                <template #default="{ row }">
                  ({{ row.x ?? row.xPos ?? 0 }}, {{ row.z ?? row.zPos ?? 0 }})
                </template>
              </el-table-column>
              <el-table-column prop="yardSlotId" label="仓位ID" width="80" />
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" type="primary" link @click="openMove(row)">移位</el-button>
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
        </el-card>
      </div>
    </div>

    <!-- 移位对话框 -->
    <el-dialog v-model="showMoveDialog" title="集装箱移位" width="400px">
      <el-form :model="moveForm" label-width="80px">
        <el-form-item label="箱号">
          <el-input :model-value="moveForm.containerNo" disabled />
        </el-form-item>
        <el-form-item label="目标排">
          <el-input-number v-model="moveForm.targetRow" :min="1" :max="6" />
        </el-form-item>
        <el-form-item label="目标列">
          <el-input-number v-model="moveForm.targetCol" :min="1" :max="8" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMoveDialog = false">取消</el-button>
        <el-button type="primary" @click="handleMove">确认移位</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

interface ContainerItem {
  id: number
  containerNo: string
  cargoType: string
  destPort: string
  weight: number
  status: number
  yardSlotId: number | null
  areaNo: number
  loadStatus: number
  x: number | null
  z: number | null
  xPos: number
  zPos: number
}

const currentArea = ref(1)
const loading = ref(false)
const allContainers = ref<ContainerItem[]>([])
const searchNo = ref('')
const pageNum = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showMoveDialog = ref(false)
const moveForm = ref({ id: 0, containerNo: '', targetRow: 1, targetCol: 1 })

const areaName = computed(() => ['A区', 'B区', 'C区'][currentArea.value - 1] || 'A区')

const areaContainers = computed(() => {
  return allContainers.value.filter(c => c.areaNo === currentArea.value)
})

const filteredList = computed(() => {
  let list = areaContainers.value
  if (searchNo.value) {
    list = list.filter(c => c.containerNo.includes(searchNo.value))
  }
  total.value = list.length
  const start = (pageNum.value - 1) * pageSize.value
  return list.slice(start, start + pageSize.value)
})

const statusText = (s: number) => ['正常', '作业中', '破损', '已装船'][s] || '未知'
const statusTagType = (s: number) => ['success', 'primary', 'danger', 'info'][s] || 'info'

const getContainerAt = (row: number, col: number): ContainerItem | undefined => {
  // 根据坐标映射：x范围对应列，z范围对应排
  // 简化：用areaNo + 坐标计算位置
  return areaContainers.value.find(c => {
    const x = c.x ?? c.xPos ?? 0
    const z = c.z ?? c.zPos ?? 0
    // 映射逻辑：每个箱子占一个格子
    const cRow = Math.abs(Math.round(z / 30)) + 1
    const cCol = Math.abs(Math.round(x / 25)) + 1
    return cRow === row && cCol === col
  })
}

const getCellClass = (row: number, col: number) => {
  const c = getContainerAt(row, col)
  if (!c) return 'empty'
  if (c.status === 2) return 'damage'
  if (c.status === 1) return 'working'
  return 'normal'
}

const handleCellClick = (row: number, col: number) => {
  const c = getContainerAt(row, col)
  if (c) {
    ElMessage.info(`仓位 ${row}-${col}: ${c.containerNo} (${statusText(c.status)})`)
  } else {
    ElMessage.info(`仓位 ${row}-${col}: 空闲`)
  }
}

const handleAreaChange = () => {
  pageNum.value = 1
  searchNo.value = ''
}

const loadData = async () => {
  loading.value = true
  try {
    const res: any = await request.get('/api/container/twin')
    const list = res?.data || []
    allContainers.value = list
  } catch (e) {
    allContainers.value = []
  } finally {
    loading.value = false
  }
}

const openMove = (row: ContainerItem) => {
  moveForm.value = { id: row.id, containerNo: row.containerNo, targetRow: 1, targetCol: 1 }
  showMoveDialog.value = true
}

const handleMove = async () => {
  try {
    // 计算新坐标：基于排和列
    const newX = (moveForm.value.targetCol - 4) * 25
    const newZ = (moveForm.value.targetRow - 3) * 30
    await request.post('/api/container/savePos', {
      id: moveForm.value.id,
      x: newX,
      z: newZ
    })
    ElMessage.success('移位成功')
    showMoveDialog.value = false
    loadData()
  } catch (e: any) {
    ElMessage.error(e?.message || '移位失败')
  }
}

const handleDelete = async (row: ContainerItem) => {
  try {
    await ElMessageBox.confirm(`确认删除集装箱 ${row.containerNo}？`, '提示', { type: 'warning' })
    await request.delete(`/api/container/${row.id}`)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) { /* cancel */ }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.yard-page {
  display: flex; flex-direction: column; height: 100vh; padding: 16px 20px; box-sizing: border-box; overflow: hidden;
}
.page-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-shrink: 0;
}
.page-header h2 { margin: 0; color: #11616B; }
.content-row {
  display: flex; gap: 16px; flex: 1; min-height: 0;
}
.left-panel { width: 480px; flex-shrink: 0; }
.right-panel { flex: 1; min-width: 0; display: flex; }
.grid-card { height: 100%; display: flex; flex-direction: column; }
.grid-card :deep(.el-card__body) { flex: 1; overflow-y: auto; }
.yard-grid { display: flex; flex-direction: column; gap: 4px; }
.grid-row { display: flex; align-items: center; gap: 4px; }
.grid-label { width: 40px; text-align: center; font-size: 12px; color: #606266; font-weight: bold; }
.grid-cell {
  flex: 1; aspect-ratio: 1.2; border: 1px solid #dcdfe6; border-radius: 4px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s; position: relative; min-height: 45px;
}
.grid-cell:hover { transform: scale(1.05); box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.grid-cell.empty { background: #f5f7fa; }
.grid-cell.normal { background: #e1f3d8; border-color: #67c23a; }
.grid-cell.working { background: #d9ecff; border-color: #409eff; }
.grid-cell.damage { background: #fde2e2; border-color: #f56c6c; }
.cell-coord { font-size: 10px; color: #909399; }
.cell-box { font-size: 11px; font-weight: bold; color: #303133; margin-top: 2px; }
.legend { display: flex; gap: 16px; margin-top: 12px; justify-content: center; }
.legend-item { display: flex; align-items: center; gap: 4px; font-size: 12px; color: #606266; }
.legend-color { width: 14px; height: 14px; border-radius: 3px; border: 1px solid #dcdfe6; }
.legend-color.empty { background: #f5f7fa; }
.legend-color.normal { background: #e1f3d8; }
.legend-color.working { background: #d9ecff; }
.legend-color.damage { background: #fde2e2; }
.list-card { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.list-card :deep(.el-card__body) { flex: 1; display: flex; flex-direction: column; min-height: 0; padding: 12px; }
.table-wrapper { flex: 1; min-height: 0; overflow: hidden; }
.pagination-bar { display: flex; justify-content: flex-end; padding-top: 10px; flex-shrink: 0; }
</style>
