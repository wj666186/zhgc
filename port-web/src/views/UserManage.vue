<template>
    <div style="padding: 24px;">
        <el-button type="primary" @click="openAddDialog">新增用户</el-button>
        <el-table :data="tableData" border style="margin-top: 16px;">
            <el-table-column label="ID" prop="id" width="80" />
            <el-table-column label="用户名" prop="username" />
            <el-table-column label="用户角色">
                <template #default="scope">
                    {{ scope.row.role === 'admin' ? '系统管理员' : '普通操作员' }}
                </template>
            </el-table-column>
            <el-table-column label="创建时间" prop="createTime" />
            <el-table-column label="操作" width="100">
                <template #default="scope">
                    <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
                </template>
            </el-table-column>
        </el-table>

        <el-dialog v-model="dialogVisible" title="用户信息编辑">
            <el-form :model="form">
                <el-form-item label="用户名">
                    <el-input v-model="form.username"></el-input>
                </el-form-item>
                <el-form-item label="登录密码" v-if="!form.id">
                    <el-input v-model="form.password" show-password placeholder="新增用户必须填写密码"></el-input>
                </el-form-item>
                <el-form-item label="账号角色">
                    <el-select v-model="form.role">
                        <el-option label="管理员" value="admin" />
                        <el-option label="普通用户" value="user" />
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="submitForm">确认提交</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getUserList, addUser, updateUser } from '../api/user'
import { ElMessage } from 'element-plus'

const tableData = ref<any[]>([])
const dialogVisible = ref(false)
const form = ref({
    id: null as number | null,
    username: '',
    password: '',
    role: 'user'
})

// 加载用户列表
const loadUserList = async () => {
    const res = await getUserList()
    tableData.value = res.data
}

onMounted(() => {
    loadUserList()
})

// 打开新增弹窗
const openAddDialog = () => {
    form.value = { id: null, username: '', password: '', role: 'user' }
    dialogVisible.value = true
}

// 打开编辑弹窗
const openEditDialog = (row: any) => {
    form.value = { ...row, password: '' }
    dialogVisible.value = true
}

// 提交表单
const submitForm = async () => {
    try {
        if (form.value.id) {
            await updateUser(form.value)
        } else {
            if (!form.value.password) {
                ElMessage.warning('新增用户必须填写登录密码')
                return
            }
            await addUser(form.value)
        }
        dialogVisible.value = false
        loadUserList()
        ElMessage.success('操作完成')
    } catch (err: any) {
        ElMessage.error(err.msg || '操作失败')
    }
}
</script>