<template>
    <div class="login-box">
        <h2>港口调度系统登录</h2>
        <div class="item">
            <label>用户名</label>
            <input v-model="username" placeholder="请输入用户名" />
        </div>
        <div class="item">
            <label>密码</label>
            <input v-model="password" type="password" placeholder="请输入密码" />
        </div>
        <button @click="doLogin">登录</button>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { loginApi } from '../api/login'

interface LoginData {
    token: string
    username: string
    role: string
}
interface LoginResult {
    code: number
    data: LoginData
    msg?: string
}

const router = useRouter()
const username = ref('')
const password = ref('')

// 彻底移除onMounted页面自动跳转逻辑，只能点击按钮登录跳转
const doLogin = async () => {
    if (!username.value.trim()) {
        ElMessage.warning('请输入用户名')
        return
    }
    if (!password.value.trim()) {
        ElMessage.warning('请输入密码')
        return
    }

    try {
        const res = await loginApi({
            username: username.value,
            password: password.value
        }) as LoginResult

        if (res.code === 200) {
            localStorage.setItem('token', res.data.token)
            localStorage.setItem('username', res.data.username)
            localStorage.setItem('userRole', res.data.role)
            ElMessage.success('登录成功')
            // 仅登录请求成功后手动跳转首页
            await router.push('/dashboard')
        } else {
            ElMessage.error(res.msg || '用户名或密码错误')
        }
    } catch (err) {
        ElMessage.error('请求失败，请检查后端服务是否正常启动')
        console.error('登录接口异常：', err)
    }
}
</script>

<style scoped>
.login-box {
    width: 360px;
    margin: 150px auto;
    padding: 30px;
    border: 1px solid #eee;
    border-radius: 8px;
}
.item {
    margin: 16px 0;
}
label {
    display: block;
    margin-bottom: 6px;
}
input {
    width: 100%;
    box-sizing: border-box;
    padding: 8px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
}
button {
    width: 100%;
    padding: 10px;
    background: #409eff;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
}
button:active {
    background: #337ecc;
}
</style>