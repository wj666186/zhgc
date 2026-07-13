<template>
    <!-- 最外层绑定背景图 -->
    <div class="container-wrap">
        <!-- 功能卡片容器，半透明悬浮面板 -->
        <div class="content-card">
            <div class="btn-top">
                <button class="btn-add" @click="openAdd">新增集装箱</button>
            </div>
            <h1 class="page-title">集装箱信息管理</h1>
            <table class="container-table">
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
                <tr v-for="item in records" :key="item.id">
                    <td>{{ item.containerNo }}</td>
                    <td>{{ item.cargoType }}</td>
                    <td>{{ item.destPort }}</td>
                    <td>{{ item.weight }}</td>
                    <td>{{ item.status === 0 ? '待入堆' : item.status === 1 ? '运输中' : '已离港' }}</td>
                    <td>{{ item.yardSlotId || '未分配' }}</td>
                    <td class="btn-group">
                        <button class="btn-edit" @click="openEdit(item)">编辑</button>
                        <button class="btn-del" @click="handleDelete(item.id)">删除</button>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>

        <!-- 编辑弹窗 -->
        <div v-if="editVisible" class="edit-dialog">
            <div class="dialog-box">
                <h3>编辑集装箱</h3>
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
                    <input v-model.number="editForm.weight" />
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
                    <input v-model="addForm.containerNo" />
                </div>
                <div class="form-item">
                    <label>货物类型：</label>
                    <input v-model="addForm.cargoType" />
                </div>
                <div class="form-item">
                    <label>目的港口：</label>
                    <input v-model="addForm.destPort" />
                </div>
                <div class="form-item">
                    <label>重量：</label>
                    <input v-model.number="addForm.weight" />
                </div>
                <div class="dialog-buttons">
                    <button class="btn-save" @click="submitAdd">确认新增</button>
                    <button class="btn-cancel" @click="addVisible = false">取消</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getContainerList, updateContainer, delContainer, addContainer } from '@/api/container'

// 表格数据
const records = ref([])

// 编辑弹窗控制
const editVisible = ref(false)
const editForm = ref({
    id: 0,
    containerNo: '',
    cargoType: '',
    destPort: '',
    weight: 0
})

// 新增弹窗控制
const addVisible = ref(false)
const addForm = ref({
    containerNo: '',
    cargoType: '',
    destPort: '',
    weight: 0
})

// 加载列表
const loadList = async () => {
    const res = await getContainerList({})
    if (res.code === 200) {
        records.value = res.data.records
    }
}
onMounted(loadList)

// 打开编辑
const openEdit = (row) => {
    editForm.value = { ...row }
    editVisible.value = true
}

// 提交编辑
const submitEdit = async () => {
    await updateContainer(editForm.value)
    editVisible.value = false
    loadList()
}

// 删除
const handleDelete = async (id) => {
    if (confirm('确定删除该条数据？')) {
        await delContainer(id)
        loadList()
    }
}

// 打开新增弹窗
const openAdd = () => {
    addForm.value = {
        containerNo: '',
        cargoType: '',
        destPort: '',
        weight: 0
    }
    addVisible.value = true
}

// 提交新增
const submitAdd = async () => {
    await addContainer(addForm.value)
    addVisible.value = false
    loadList()
}
</script>

<style scoped>
/* 页面背景 */
.container-wrap {
    width: 100%;
    min-height: calc(100vh - 55px);
    padding: 24px;
    box-sizing: border-box;
    background: url('@/assets/port-bg.png') no-repeat center center;
    background-size: cover;
}

/* 主内容磨砂卡片 */
.content-card {
    width: 100%;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(8px);
    border-radius: 12px;
    padding: 28px;
    box-sizing: border-box;
    box-shadow: 0 4px 20px rgba(0, 30, 60, 0.15);
}

.btn-top {
    margin-bottom: 16px;
}

.page-title {
    text-align: center;
    margin: 0 0 24px;
    color: #0f4c81;
    font-weight: 600;
    letter-spacing: 2px;
}

/* 表格样式美化 */
.container-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

.container-table th {
    background-color: #165dff;
    color: #fff;
    padding: 12px 10px;
    border: 1px solid #e6edf7;
}

.container-table td {
    padding: 12px 10px;
    border: 1px solid #e6edf7;
    background-color: #ffffff;
}

.container-table tbody tr:hover td {
    background-color: #f0f7ff;
}

/* 按钮通用样式 */
.btn-add {
    background-color: #165dff;
    color: white;
    border: none;
    padding: 8px 18px;
    border-radius: 6px;
    cursor: pointer;
    transition: 0.2s;
}
.btn-add:hover {
    background-color: #0e4bdd;
}

.btn-edit {
    background-color: #4096ff;
    color: #fff;
    border: none;
    padding: 5px 10px;
    border-radius: 4px;
    cursor: pointer;
}
.btn-del {
    background-color: #f53f3f;
    color: #fff;
    border: none;
    padding: 5px 10px;
    border-radius: 4px;
    cursor: pointer;
    margin-left: 6px;
}

.btn-group {
    display: flex;
    gap: 8px;
    justify-content: center;
}

/* 弹窗遮罩 */
.edit-dialog {
    position: fixed;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.55);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 999;
}

.dialog-box {
    background: #fff;
    padding: 26px 32px;
    border-radius: 10px;
    min-width: 420px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.2);
}

.form-item {
    margin: 14px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.form-item label {
    width: 80px;
}
.form-item input {
    flex: 1;
    padding: 8px 10px;
    border: 1px solid #dcdcdc;
    border-radius: 5px;
    outline: none;
}
.form-item input:focus {
    border-color: #165dff;
}

.dialog-buttons {
    margin-top: 20px;
    display: flex;
    gap: 12px;
    justify-content: center;
}
.btn-save {
    background: #165dff;
    color: #fff;
    border: none;
    padding: 8px 22px;
    border-radius: 6px;
    cursor: pointer;
}
.btn-cancel {
    background: #f2f3f5;
    border: none;
    padding: 8px 22px;
    border-radius: 6px;
    cursor: pointer;
}
</style>