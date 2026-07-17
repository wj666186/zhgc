<template>
    <div style="padding: 24px; min-height: calc(100vh - 60px); box-sizing: border-box;">
        <div style="text-align: center; margin-bottom: 20px; position: relative;">
            <h2 style="font-size: 32px; font-weight: bold; color: #193770; margin: 0;">用户信息管理</h2>
            <el-button
                type="primary"
                icon="Plus"
                @click="openAddDialog"
                style="position: absolute; right: 0; top: 5px; background: #407bff; border: none;"
            >
                新增用户
            </el-button>
        </div>

        <span style="display: block; text-align: right; color: #666; font-size: 13px; margin-bottom: 12px;">
      共 {{ tableData.length }} 条用户数据
    </span>

        <!-- 重点修改：header-cell-style 改为绑定返回样式对象的函数 -->
        <el-table
            :data="tableData"
            border
            stripe
            style="width: 100%;"
            element-loading="loading"
            :header-cell-style="tableHeaderStyle"
        >
            <el-table-column label="ID" prop="id" width="80" align="center" />
            <el-table-column label="用户名" prop="username" align="center" />
            <el-table-column label="用户角色" align="center">
                <template #default="scope">
                    <el-tag
                        :type="scope.row.role === 'admin' ? 'primary' : 'info'"
                        size="small"
                        effect="light"
                    >
                        {{ scope.row.role === 'admin' ? '系统管理员' : '普通操作员' }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column label="创建时间" prop="createTime" align="center" min-width="180" />
            <el-table-column label="操作" width="180" align="center">
                <template #default="scope">
                    <el-button
                        size="small"
                        type="primary"
                        plain
                        @click="openEditDialog(scope.row)"
                        style="margin-right: 8px;"
                    >
                        编辑
                    </el-button>

                    <el-popconfirm
                        v-if="loginUserRole === 'admin' && scope.row.username !== 'admin'"
                        title="确定删除该用户？删除后数据无法恢复！"
                        confirm-button-text="确认删除"
                        cancel-button-text="取消"
                        icon="WarningFilled"
                        icon-color="#E64340"
                        @confirm="confirmDelete(scope.row.id)"
                    >
                        <template #reference>
                            <el-button size="small" type="danger" plain @click="handleDeleteClick(scope.row)">
                                删除
                            </el-button>
                        </template>
                    </el-popconfirm>
                </template>
            </el-table-column>
        </el-table>

        <el-dialog v-model="dialogVisible" title="用户信息编辑" width="420px" draggable>
            <el-form :model="form" label-width="90px">
                <el-form-item label="用户名" required>
                    <el-input v-model="form.username" placeholder="请输入用户名" />
                </el-form-item>
                <el-form-item label="登录密码" v-if="!form.id" required>
                    <el-input v-model="form.password" show-password placeholder="新增用户必须填写密码" />
                </el-form-item>
                <el-form-item label="账号角色">
                    <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%;">
                        <el-option label="系统管理员" value="admin" />
                        <el-option label="普通操作员" value="user" />
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="dialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="submitForm">确认提交</el-button>
                </div>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getUserList, addUser, updateUser, deleteUser } from '../api/user'
import { ElMessage } from 'element-plus'

const tableData = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = ref({
    id: null as number | null,
    username: '',
    password: '',
    role: 'user'
})
const loginUserRole = ref(localStorage.getItem('userRole') || '')

// 表头样式函数，返回标准样式对象，彻底解决属性类型报错
const tableHeaderStyle = () => {
    return {
        backgroundColor: '#2662d9',
        color: '#fff',
        fontWeight: 'bold',
        textAlign: 'center'
    }
}

const loadUserList = async () => {
    loading.value = true
    try {
        const res = await getUserList()
        tableData.value = res.data
    } catch (err){
    ElMessage.error('列表加载失败')
}finally {
    loading.value = false
}
}


onMounted(() => {
    loadUserList()
})

const openAddDialog = () => {
    form.value = { id: null, username: '', password: '', role: 'user' }
    dialogVisible.value = true
}

const openEditDialog = (row: any) => {
    form.value = { ...row, password: '' }
    dialogVisible.value = true
}

const submitForm = async () => {
    if (!form.value.username.trim()) {
        ElMessage.warning('用户名不能为空')
        return
    }
    if (!form.value.id && !form.value.password?.trim()) {
        ElMessage.warning('新增用户必须填写登录密码')
        return
    }

    try {
        if (form.value.id) {
            await updateUser(form.value)
            ElMessage.success('用户编辑成功')
        } else {
            await addUser(form.value)
            ElMessage.success('用户新增成功')
        }
        dialogVisible.value = false
        loadUserList()
    } catch (err: any) {
        ElMessage.error(err.msg || '操作请求失败')
    }
}

const handleDeleteClick = (row: any) => {
    if (row.username === 'admin') {
        ElMessage.warning('系统默认管理员admin禁止删除！')
        return
    }
}

const confirmDelete = async (delId: number) => {
    try {
        await deleteUser(delId)
        ElMessage.success('用户删除成功')
        loadUserList()
    } catch (err: any) {
        ElMessage.error(err.msg || '删除失败')
    }
}
</script>

<style scoped>
.dialog-footer {
    text-align: right;
}
</style>
