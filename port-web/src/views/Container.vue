<template>
    <div class="page-container">
        <!-- 页面头部 -->
        <div class="page-header">
            <h2 class="page-title">集装箱信息管理</h2>
            <div class="toolbar-right">
                <el-button type="primary" :icon="Plus" @click="openAdd">新增集装箱</el-button>
            </div>
        </div>

        <!-- 数据卡片 -->
        <el-card class="table-card" shadow="never">
            <el-table
                :data="pagedList"
                stripe
                border
                style="width: 100%"
                :header-cell-style="{ background: '#EBF4F8', color: '#11616B', fontWeight: 600 }"
            >
                <el-table-column prop="containerNo" label="箱号" width="160" align="center">
                    <template #default="{ row }">
                        <span class="container-no">{{ row.containerNo }}</span>
                    </template>
                </el-table-column>
                <el-table-column prop="cargoType" label="货物类型" align="center" />
                <el-table-column prop="destPort" label="目的港口" align="center" />
                <el-table-column prop="weight" label="重量(吨)" width="100" align="center" />
                <el-table-column label="状态" width="120" align="center">
                    <template #default="{ row }">
                        <el-tag :type="statusTagType[row.status]" effect="light" round>
                            {{ statusText[row.status] }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column label="所属仓位" align="center">
                    <template #default="{ row }">
                        {{ getSlotDisplay(row) }}
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="260" align="center" fixed="right">
                    <template #default="{ row }">
                        <el-button size="small" type="primary" link @click="openEdit(row)" :disabled="row.status === 3">
                            编辑
                        </el-button>
                        <el-button size="small" type="success" link @click="handleAllocate(row)" :disabled="[2,3].includes(row.status)">
                            分配堆场
                        </el-button>
                        <el-button size="small" type="danger" link @click="handleDelete(row)">
                            删除
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-wrap">
                <el-pagination
                    v-model:current-page="currentPage"
                    v-model:page-size="pageSize"
                    :page-sizes="[10, 20, 50]"
                    :total="containerList.length"
                    layout="total, sizes, prev, pager, next, jumper"
                    background
                />
            </div>
        </el-card>

        <!-- 新增/编辑弹窗 -->
        <el-dialog
            v-model="dialogVisible"
            :title="isEdit ? '编辑集装箱信息' : '新增集装箱'"
            width="480px"
            :close-on-click-modal="false"
        >
            <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
                <el-form-item label="箱号" prop="containerNo">
                    <el-input v-model="form.containerNo" placeholder="请输入集装箱箱号" />
                </el-form-item>
                <el-form-item label="货物类型" prop="cargoType">
                    <el-input v-model="form.cargoType" placeholder="例如：电子产品" />
                </el-form-item>
                <el-form-item label="目的港口" prop="destPort">
                    <el-input v-model="form.destPort" placeholder="例如：上海港" />
                </el-form-item>
                <el-form-item label="重量" prop="weight">
                    <el-input-number v-model="form.weight" :min="0" :precision="2" :step="0.5" placeholder="单位：吨" style="width: 100%" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" :loading="submitLoading" @click="submitForm">确定</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { useContainerStore } from '../stores/container'
import type { ContainerStatus, ContainerItem } from '../api/container'
import { updateContainer, delContainer, addContainer, allocateYardByNo } from '../api/container'

const containerStore = useContainerStore()
const containerList = computed<ContainerItem[]>(() => containerStore.containerList)
const slotList = computed(() => containerStore.slotList)

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const pagedList = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    return containerList.value.slice(start, start + pageSize.value)
})

// 状态映射
const statusText: Record<ContainerStatus, string> = {
    0: '待分配',
    1: '已分配堆场',
    2: '破损锁定',
    3: '已装船'
}
const statusTagType: Record<ContainerStatus, string> = {
    0: 'info',
    1: 'primary',
    2: 'warning',
    3: 'success'
}

const getSlotDisplay = (item: ContainerItem) => {
    if (item.loadStatus === 1) return '存放于轮船'
    if (!item.yardSlotId) return '未分配'
    const slot = slotList.value.find(s => s.id === item.yardSlotId)
    return slot ? `分区${slot.areaCode} ${slot.rowNo}排${slot.colNo}列` : '仓位异常'
}

// 弹窗
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
    id: null as number | null,
    containerNo: '',
    cargoType: '',
    destPort: '',
    weight: 0
})

const rules: FormRules = {
    containerNo: [{ required: true, message: '请输入箱号', trigger: 'blur' }],
    cargoType: [{ required: true, message: '请输入货物类型', trigger: 'blur' }],
    destPort: [{ required: true, message: '请输入目的港口', trigger: 'blur' }],
}

const openAdd = () => {
    isEdit.value = false
    form.id = null
    form.containerNo = ''
    form.cargoType = ''
    form.destPort = ''
    form.weight = 0
    dialogVisible.value = true
}

const openEdit = (row: ContainerItem) => {
    isEdit.value = true
    form.id = Number(row.id)
    form.containerNo = row.containerNo
    form.cargoType = row.cargoType
    form.destPort = row.destPort
    form.weight = Number(row.weight)
    dialogVisible.value = true
}

const submitForm = async () => {
    if (!formRef.value) return
    await formRef.value.validate(async (valid) => {
        if (!valid) return
        submitLoading.value = true
        try {
            if (isEdit.value) {
                await updateContainer(form)
                ElMessage.success('编辑成功')
            } else {
                const addData: Omit<ContainerItem, 'id' | 'createTime' | 'updateTime'> = {
                    containerNo: form.containerNo,
                    cargoType: form.cargoType,
                    destPort: form.destPort,
                    weight: form.weight,
                    status: 0,
                    yardSlotId: null,
                    areaNo: 1,
                    loadStatus: 0
                }
                await addContainer(addData)
                ElMessage.success('新增成功')
            }
            dialogVisible.value = false
            await containerStore.refreshAllData()
        } catch (err: any) {
            ElMessage.error('操作失败：' + (err.message || '服务异常'))
        } finally {
            submitLoading.value = false
        }
    })
}

const handleDelete = (row: ContainerItem) => {
    ElMessageBox.confirm(`确定要删除集装箱「${row.containerNo}」吗？删除后无法恢复`, '删除确认', {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
    }).then(async () => {
        try {
            await delContainer(Number(row.id))
            ElMessage.success('删除成功')
            await containerStore.refreshAllData()
        } catch (err: any) {
            ElMessage.error('删除失败：' + (err.message || '服务异常'))
        }
    }).catch(() => {})
}

const handleAllocate = async (row: ContainerItem) => {
    try {
        await allocateYardByNo(row.containerNo)
        ElMessage.success('堆场分配完成')
        await containerStore.refreshAllData()
    } catch (err: any) {
        ElMessage.error('分配失败：' + (err.message || '暂无空闲仓位/箱子破损禁止分配'))
    }
}

// WebSocket
let socket: WebSocket | null = null
let reconnectTimer: number | null = null
const WS_URL = 'ws://localhost:8080/ws/container'

const initWebSocket = () => {
    socket = new WebSocket(WS_URL)
    socket.onmessage = (event) => {
        if (event.data === 'container_refresh') {
            containerStore.refreshAllData()
        }
    }
    socket.onclose = () => {
        socket = null
        if (!reconnectTimer) {
            reconnectTimer = window.setTimeout(() => {
                initWebSocket()
                reconnectTimer = null
            }, 3000)
        }
    }
    socket.onerror = () => { socket?.close() }
}

onMounted(() => {
    initWebSocket()
    containerStore.refreshAllData()
})

onUnmounted(() => {
    if (reconnectTimer) clearTimeout(reconnectTimer)
    if (socket) socket.close()
})
</script>

<style scoped>
.page-container {
    width: 100%;
    height: 100%;
    padding: 20px 24px;
    box-sizing: border-box;
    overflow-y: auto;
    overflow-x: hidden;
}

.page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}

.page-title {
    font-size: 20px;
    font-weight: 700;
    color: #11616B;
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0;
}
.page-title::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 20px;
    background: linear-gradient(180deg, #11616B, #7BBDB6);
    border-radius: 2px;
}

.table-card {
    border-radius: 12px;
    border: none;
}

.container-no {
    font-family: 'Courier New', monospace;
    font-weight: 600;
    color: #11616B;
}

.pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
}
</style>
