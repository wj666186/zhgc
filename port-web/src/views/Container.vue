<template>
    <div class="container-wrap">
        <div class="content-card">
            <div class="btn-top">
                <button class="btn-add" @click="openAdd">新增集装箱</button>
            </div>
            <h1 class="page-title">集装箱信息管理</h1>
            <table class="container-table">
                <thead>
                <tr>
                    <th style="width: 15%;">箱号</th>
                    <th style="width: 14%;">货物类型</th>
                    <th style="width: 15%;">目的港口</th>
                    <th style="width: 10%;">重量</th>
                    <th style="width: 12%;">状态</th>
                    <th style="width: 14%;">所属仓位</th>
                    <th style="width: 20%;">操作</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="item in containerList" :key="item.id">
                    <td>{{ item.containerNo }}</td>
                    <td>{{ item.cargoType }}</td>
                    <td>{{ item.destPort }}</td>
                    <td>{{ item.weight }}</td>
                    <!-- 状态文字+颜色标识 -->
                    <td :class="statusClass[item.status]">{{ statusText[item.status] }}</td>
                    <td>{{ getSlotDisplay(item) }}</td>
                    <td class="btn-group">
                        <button class="btn-edit" @click="openEdit(item)" :disabled="item.status === 3">编辑</button>
                        <button class="btn-allocate" @click="handleAllocate(item)" :disabled="[2,3].includes(item.status)">分配堆场</button>
                        <button class="btn-del" @click="handleDelete(Number(item.id))">删除</button>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>

        <!-- 编辑弹窗 -->
        <div v-if="editVisible" class="edit-dialog">
            <div class="dialog-box">
                <h3>编辑集装箱信息</h3>
                <div class="form-item">
                    <label>箱号：</label>
                    <input v-model="editForm.containerNo" />
                </div>
                <div class="form-item">
                    <label>货物类型：</label>
                    <input v-model="editForm.cargoType" />
                </div>
                <div class="form-item">
                    <label>目的港口：</label>
                    <input v-model="editForm.destPort" />
                </div>
                <div class="form-item">
                    <label>重量：</label>
                    <input v-model.number="editForm.weight" type="number" step="0.01"/>
                </div>
                <div class="dialog-buttons">
                    <button class="btn-save" @click="submitEdit">确定保存</button>
                    <button class="btn-cancel" @click="editVisible = false">取消</button>
                </div>
            </div>
        </div>

        <!-- 新增弹窗 -->
        <div v-if="addVisible" class="edit-dialog">
            <div class="dialog-box">
                <h3>新增集装箱</h3>
                <div class="form-item">
                    <label>箱号：</label>
                    <input v-model="addForm.containerNo" placeholder="请输入集装箱箱号"/>
                </div>
                <div class="form-item">
                    <label>货物类型：</label>
                    <input v-model="addForm.cargoType" placeholder="例如：电子产品"/>
                </div>
                <div class="form-item">
                    <label>目的港口：</label>
                    <input v-model="addForm.destPort" placeholder="例如：上海港"/>
                </div>
                <div class="form-item">
                    <label>重量：</label>
                    <input v-model.number="addForm.weight" type="number" step="0.01" placeholder="单位：吨"/>
                </div>
                <div class="dialog-buttons">
                    <button class="btn-save" @click="submitAdd">确认新增</button>
                    <button class="btn-cancel" @click="addVisible = false">取消</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted, watch } from 'vue'
import { useContainerStore } from '../stores/container'
import type { ContainerStatus, ContainerItem } from '../api/container'
import { getContainerList, updateContainer, delContainer, addContainer, allocateYardByNo } from '../api/container'

// Pinia仓库
const containerStore = useContainerStore()
const containerList = computed<ContainerItem[]>(() => containerStore.containerList)
const slotList = computed(() => containerStore.slotList)

// 状态文字映射（和后端、数字孪生视图完全统一）
const statusText: Record<ContainerStatus, string> = {
    0: '待分配',
    1: '已分配堆场',
    2: '破损锁定',
    3: '已装船'
}

// 状态文字颜色样式
const statusClass: Record<ContainerStatus, string> = {
    0: 'text-green',
    1: 'text-blue',
    2: 'text-orange',
    3: 'text-skyblue'
}

// 仓位展示文案处理
const getSlotDisplay = (item: ContainerItem) => {
    // 已装船箱子
    if (item.loadStatus === 1) return '🚢 存放于轮船'
    if (!item.yardSlotId) return '未分配'
    const slot = slotList.value.find(s => s.id === item.yardSlotId)
    return slot ? `分区${slot.areaCode} ${slot.rowNo}排${slot.colNo}列` : '仓位异常'
}

// 弹窗开关
const editVisible = ref<boolean>(false)
const addVisible = ref<boolean>(false)

// 编辑表单
const editForm = ref({
    id: null as number | null,
    containerNo: '',
    cargoType: '',
    destPort: '',
    weight: 0
})

// 新增表单：默认状态0待分配、1号仓位、堆场内
const addForm = ref<Omit<ContainerItem, 'id' | 'createTime' | 'updateTime'>>({
    containerNo: '',
    cargoType: '',
    destPort: '',
    weight: 0,
    status: 0,
    yardSlotId: null,
    areaNo: 1,
    loadStatus: 0
})

// WebSocket变量 + 重连定时器
let socket: WebSocket | null = null
let reconnectTimer: number | null = null
const WS_URL = 'ws://localhost:8080/ws/container'

// 初始化WebSocket 支持断开自动重连
const initWebSocket = () => {
    socket = new WebSocket(WS_URL)

    socket.onmessage = (event) => {
        if (event.data === 'container_refresh') {
            containerStore.refreshAllData()
        }
    }

    // 连接关闭 3秒后自动重连
    socket.onclose = () => {
        socket = null
        if (!reconnectTimer) {
            reconnectTimer = window.setTimeout(() => {
                initWebSocket()
                reconnectTimer = null
            }, 3000)
        }
    }

    socket.onerror = () => {
        socket?.close()
    }
}

// 打开编辑弹窗
const openEdit = (row: ContainerItem) => {
    editForm.value.id = Number(row.id)
    editForm.value.containerNo = row.containerNo
    editForm.value.cargoType = row.cargoType
    editForm.value.destPort = row.destPort
    editForm.value.weight = Number(row.weight)
    editVisible.value = true
}

// 提交编辑
const submitEdit = async () => {
    try {
        await updateContainer(editForm.value)
        editVisible.value = false
        alert('编辑成功')
    } catch (err: any) {
        alert('编辑失败：' + (err.message || '服务异常'))
    }
}

// 删除集装箱
const handleDelete = async (id: number) => {
    if (!confirm('确定要删除该集装箱数据？删除后无法恢复')) return
    try {
        await delContainer(id)
        alert('删除成功')
    } catch (err: any) {
        alert('删除失败：' + (err.message || '服务异常'))
    }
}

// 分配堆场按钮点击事件
const handleAllocate = async (row: ContainerItem) => {
    try {
        await allocateYardByNo(row.containerNo)
        alert('堆场分配完成')
    } catch (err: any) {
        alert('分配失败：' + (err.message || '暂无空闲仓位/箱子破损禁止分配'))
    }
}

// 打开新增弹窗
const openAdd = () => {
    addForm.value = {
        containerNo: '',
        cargoType: '',
        destPort: '',
        weight: 0,
        status: 0,
        yardSlotId: null,
        areaNo: 1,
        loadStatus: 0
    }
    addVisible.value = true
}

// 提交新增
const submitAdd = async () => {
    if (!addForm.value.containerNo.trim()) {
        alert('请填写箱号')
        return
    }
    try {
        await addContainer(addForm.value)
        addVisible.value = false
        alert('新增集装箱成功')
    } catch (err: any) {
        alert('新增失败：' + (err.message || '服务异常'))
    }
}

onMounted(() => {
    initWebSocket()
    // 初始化加载列表
    containerStore.refreshAllData()
})

onUnmounted(() => {
    // 清除重连定时器、关闭ws连接
    if (reconnectTimer) clearTimeout(reconnectTimer)
    if (socket) socket.close()
})
</script>

<style scoped>
.container-wrap {
    width: 100%;
    height: 100%;
    padding: 24px;
    box-sizing: border-box;
    background: url('@/assets/1.png') no-repeat center center;
    background-size: cover;
    overflow-x: hidden;
}

.content-card {
    width: 100%;
    background: rgba(255, 255, 255, 0.88);
    backdrop-filter: blur(8px);
    border-radius: 12px;
    padding: 28px;
    box-sizing: border-box;
    box-shadow: 0 4px 20px rgba(17, 97, 107, 0.18);
}

.btn-top {
    margin-bottom: 16px;
    text-align: right;
}

.page-title {
    text-align: center;
    margin: 0 0 24px;
    color: #11616B;
    font-weight: 600;
    letter-spacing: 2px;
    font-size: 30px;
}

.container-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    table-layout: auto;
}

.container-table th {
    background-color: #11616B;
    color: #EBF4F8;
    padding: 12px 6px;
    border: 1px solid #dce8ec;
    text-align: center;
}

.container-table td {
    padding: 12px 6px;
    border: 1px solid #dce8ec;
    background-color: #ffffff;
    color: #222;
    text-align: center;
}

.container-table tbody tr:hover td {
    background-color: #7BBDB6;
    color: #08383f;
}

/* 状态文字颜色 */
:deep(.text-green) {
    color: #009933;
    font-weight: 500;
}
:deep(.text-blue) {
    color: #11616B;
    font-weight: 500;
}
:deep(.text-orange) {
    color: #e67722;
    font-weight: 500;
}
:deep(.text-skyblue) {
    color: #0077bb;
    font-weight: 500;
}

.btn-add {
    background-color: #11616B;
    color: #EBF4F8;
    border: none;
    padding: 8px 18px;
    border-radius: 6px;
    cursor: pointer;
    transition: 0.2s;
    font-size: 15px;
}
.btn-add:hover {
    background-color: #7BBDB6;
    color: #11616B;
}

.btn-edit {
    background-color: #7BBDB6;
    color: #093a41;
    border: none;
    padding: 5px 10px;
    border-radius: 4px;
    cursor: pointer;
}
.btn-allocate {
    background-color: #369099;
    color: #fff;
    border: none;
    padding: 5px 10px;
    border-radius: 4px;
    cursor: pointer;
}
.btn-del {
    background-color: #DC8B70;
    color: #fff;
    border: none;
    padding: 5px 10px;
    border-radius: 4px;
    cursor: pointer;
    margin-left: 6px;
}

button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-group {
    display: flex;
    gap: 6px;
    justify-content: center;
    flex-wrap: wrap;
}

.edit-dialog {
    position: fixed;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background: rgba(17, 97, 107, 0.55);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 999;
}

.dialog-box {
    background: #EBF4F8;
    padding: 26px 32px;
    border-radius: 10px;
    min-width: 420px;
    box-shadow: 0 8px 30px rgba(17, 97, 107, 0.25);
}
.dialog-box h3 {
    color: #11616B;
    text-align: center;
    margin-top: 0;
}

.form-item {
    margin: 14px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.form-item label {
    width: 80px;
    color: #11616B;
    font-weight: 500;
}
.form-item input {
    flex: 1;
    padding: 8px 10px;
    border: 1px solid #b8d8dd;
    border-radius: 5px;
    outline: none;
    background: #fff;
}
.form-item input:focus {
    border-color: #11616B;
}

.dialog-buttons {
    margin-top: 20px;
    display: flex;
    gap: 12px;
    justify-content: center;
}
.btn-save {
    background: #11616B;
    color: #EBF4F8;
    border: none;
    padding: 8px 22px;
    border-radius: 6px;
    cursor: pointer;
}
.btn-save:hover {
    background: #7BBDB6;
    color: #11616B;
}
.btn-cancel {
    background: #FED9CD;
    color: #663c30;
    border: none;
    padding: 8px 22px;
    border-radius: 6px;
    cursor: pointer;
}
</style>
