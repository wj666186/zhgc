<template>
    <div class="container-wrap">
        <div style="margin-bottom:10px;">
            <button @click="openAdd">新增集装箱</button>
        </div>
        <h1 style="text-align: center">集装箱信息管理</h1>
        <table style="border: 1px solid #ccc; width: 100%; border-collapse: collapse;">
            <thead>
            <tr>
                <th style="border: 1px solid #ccc; padding: 6px 8px;">箱号</th>
                <th style="border: 1px solid #ccc; padding: 6px 8px;">货物类型</th>
                <th style="border: 1px solid #ccc; padding: 6px 8px;">目的港口</th>
                <th style="border: 1px solid #ccc; padding: 6px 8px;">重量</th>
                <th style="border: 1px solid #ccc; padding: 6px 8px;">状态</th>
                <th style="border: 1px solid #ccc; padding: 6px 8px;">堆场仓位</th>
                <th style="border: 1px solid #ccc; padding: 6px 8px;">操作</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="item in records" :key="item.id">
                <td style="border: 1px solid #ccc; padding: 6px 8px;">{{ item.containerNo }}</td>
                <td style="border: 1px solid #ccc; padding: 6px 8px;">{{ item.cargoType }}</td>
                <td style="border: 1px solid #ccc; padding: 6px 8px;">{{ item.destPort }}</td>
                <td style="border: 1px solid #ccc; padding: 6px 8px;">{{ item.weight }}</td>
                <td style="border: 1px solid #ccc; padding: 6px 8px;">{{ item.status }}</td>
                <td style="border: 1px solid #ccc; padding: 6px 8px;">{{ item.yardSlotId }}</td>
                <td style="border: 1px solid #ccc; padding: 6px 8px;">
                    <button @click="openEdit(item)">编辑</button>
                    <button style="margin-left: 6px;" @click="handleDelete(item.id)">删除</button>
                </td>
            </tr>
            </tbody>
        </table>

        <!-- 编辑弹窗 -->
        <div v-if="editVisible" class="edit-dialog">
            <div class="dialog-box">
                <h3>编辑集装箱</h3>
                <div>
                    <label>箱号：</label>
                    <input v-model="editForm.containerNo" />
                </div>
                <div>
                    <label>货物类型：</label>
                    <input v-model="editForm.cargoType" />
                </div>
                <div>
                    <label>目的港口：</label>
                    <input v-model="editForm.destPort" />
                </div>
                <div>
                    <label>重量：</label>
                    <input v-model.number="editForm.weight" />
                </div>
                <div style="margin-top:10px">
                    <button @click="submitEdit">确定保存</button>
                    <button style="margin-left:8px" @click="editVisible = false">取消</button>
                </div>
            </div>
        </div>

        <!-- 新增弹窗 -->
        <div v-if="addVisible" class="edit-dialog">
            <div class="dialog-box">
                <h3>新增集装箱</h3>
                <div>
                    <label>箱号：</label>
                    <input v-model="addForm.containerNo" />
                </div>
                <div>
                    <label>货物类型：</label>
                    <input v-model="addForm.cargoType" />
                </div>
                <div>
                    <label>目的港口：</label>
                    <input v-model="addForm.destPort" />
                </div>
                <div>
                    <label>重量：</label>
                    <input v-model.number="addForm.weight" />
                </div>
                <div style="margin-top:10px">
                    <button @click="submitAdd">确认新增</button>
                    <button style="margin-left:8px" @click="addVisible = false">取消</button>
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
.container-wrap {
    padding: 20px;
}
.edit-dialog {
    position: fixed;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
}
.dialog-box {
    background: #fff;
    padding: 20px;
    border-radius: 4px;
}
.dialog-box div {
    margin: 8px 0;
}
</style>