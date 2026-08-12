<template>
    <div class="user-manage-wrap">
        <div class="page-header">
            <h2>用户信息管理</h2>
            <el-button
                type="primary"
                icon="Plus"
                @click="openAddDialog"
                class="btn-add-user"
            >
                新增用户
            </el-button>
        </div>

        <div class="page-count">
            共 {{ tableData?.length || 0 }} 条用户数据
        </div>

        <el-table
            :data="tableData"
            border
            stripe
            class="user-table"
            v-loading="loading"
            :header-cell-style="tableHeaderStyle"
        >
            <!-- 改用最小像素宽度，禁止百分比，解决文字竖排错乱 -->
            <el-table-column label="ID" prop="id" min-width="70" align="center" />
            <el-table-column label="用户名" prop="username" min-width="100" align="center" />
            <el-table-column label="用户角色" min-width="130" align="center">
                <template #default="scope">
                    <el-tag
                        :type="scope.row.role === 'admin' ? 'primary' : 'info'"
                        size="small"
                        effect="light"
                        :color="scope.row.role === 'admin' ? '#11616B' : '#7BBDB6'"
                        :text-color="scope.row.role === 'admin' ? '#ffffff' : '#08383f'"
                    >
                        {{ scope.row.role === 'admin' ? '系统管理员' : '普通操作员' }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column label="创建时间" prop="createTime" min-width="180" align="center" />
            <el-table-column label="操作" min-width="170" align="center">
                <template #default="scope">
                    <el-button
                        size="small"
                        plain
                        @click="openEditDialog(scope.row)"
                        class="btn-edit-user"
                    >
                        编辑
                    </el-button>

                    <el-popconfirm
                        v-if="loginUserRole === 'admin' && scope.row.username !== 'admin'"
                        title="确定删除该用户？删除后数据无法恢复！"
                        confirm-button-text="确认删除"
                        cancel-button-text="取消"
                        icon="WarningFilled"
                        icon-color="#DC8B70"
                        @confirm="confirmDelete(scope.row.id)"
                    >
                        <template #reference>
                            <el-button
                                size="small"
                                plain
                                @click="handleDeleteClick(scope.row)"
                                class="btn-del-user"
                            >
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
                <el-form-item label="确认密码" v-if="!form.id" required>
                    <el-input
                        v-model="form.confirmPassword"
                        show-password
                        placeholder="请再次输入登录密码"
                    />
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
                    <el-button @click="dialogVisible = false" class="btn-cancel-dialog">取消</el-button>
                    <el-button type="primary" @click="submitForm" class="btn-confirm-dialog">确认提交</el-button>
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
    confirmPassword: '',
    role: 'user'
})
const loginUserRole = ref(localStorage.getItem('userRole') || '')

// 表头莫兰迪深色样式
const tableHeaderStyle = () => {
    return {
        backgroundColor: '#11616B',
        color: '#EBF4F8',
        fontWeight: 'bold',
        textAlign: 'center'
    }
}

const loadUserList = async () => {
    loading.value = true
    try {
        const res: any = await getUserList()
        // 确保tableData始终是数组，避免undefined.length报错
        tableData.value = Array.isArray(res) ? res : (res?.data || res?.records || [])
    } catch (err) {
        tableData.value = []
        ElMessage.error('列表加载失败')
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    loadUserList()
})

const openAddDialog = () => {
    form.value = { id: null, username: '', password: '', confirmPassword: '', role: 'user' }
    dialogVisible.value = true
}


const openEditDialog = (row: any) => {
    form.value = { ...row, password: '', confirmPassword: '' }
    dialogVisible.value = true
}


const submitForm = async () => {
    if (!form.value.username.trim()) {
        ElMessage.warning('用户名不能为空')
        return
    }
    // 新增用户校验密码规则
    if (!form.value.id) {
        if (!form.value.password?.trim()) {
            ElMessage.warning('新增用户必须填写登录密码')
            return
        }
        // 校验两次密码是否一致
        if (form.value.password !== form.value.confirmPassword) {
            ElMessage.warning('两次输入的密码不一致，请重新填写')
            return
        }
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
        form.value.confirmPassword = '' // 提交后清空确认密码
        await loadUserList()
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
        await loadUserList()
    } catch (err: any) {
        ElMessage.error(err.msg || '删除失败')
    }
}
</script>

<style scoped>
.user-manage-wrap {
    width: 100%;
    max-width: 100%;
    height: 100%;
    padding: 24px;
    box-sizing: border-box;
    background-color: transparent;
    overflow-x: hidden;
}


.page-header {
    text-align: center;
    margin-bottom: 20px;
    position: relative;
}

.page-header h2 {
    font-size: 32px;
    font-weight: bold;
    color: #11616B;
    margin: 0;
}

.btn-add-user {
    position: absolute;
    right: 0;
    top: 5px;
    background: #11616B;
    border: none;
    --el-color-primary: #11616B;
}

.page-count {
    display: block;
    text-align: right;
    color: #444;
    font-size: 13px;
    margin-bottom: 12px;
}

.user-table {
    width: 100%;
    background: #fff;
    table-layout: auto;
}

/* 编辑按钮配色 */
.btn-edit-user {
    margin-right: 8px;
    color: #11616B;
    border-color: #7BBDB6;
}
.btn-edit-user:hover {
    color: #fff;
    background-color: #7BBDB6;
    border-color: #7BBDB6;
}

/* 删除按钮配色 */
.btn-del-user {
    color: #DC8B70;
    border-color: #DC8B70;
}
.btn-del-user:hover {
    color: #fff;
    background-color: #DC8B70;
    border-color: #DC8B70;
}

.dialog-footer {
    text-align: right;
    gap: 10px;
    display: flex;
    justify-content: flex-end;
}

.btn-cancel-dialog {
    background: #FED9CD;
    color: #663c30;
    border: none;
}

.btn-confirm-dialog {
    background: #11616B;
    border: none;
    --el-color-primary: #11616B;
}
</style>
