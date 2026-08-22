<template>
    <div class="login-page">
        <!-- 左侧品牌区 -->
        <div class="brand-panel">
            <div class="brand-content">
                <div class="brand-logo">
                    <el-icon :size="48"><Ship /></el-icon>
                </div>
                <h1 class="brand-title">港口集装箱调度<br/>与物流协作系统</h1>
                <p class="brand-desc">基于 Spring Boot + Vue 3 + Three.js<br/>智慧港口全链路数字化管理平台</p>
                <div class="brand-features">
                    <div class="feature-item">
                        <el-icon :size="20"><DataAnalysis /></el-icon>
                        <span>实时数据看板</span>
                    </div>
                    <div class="feature-item">
                        <el-icon :size="20"><Monitor /></el-icon>
                        <span>数字孪生可视化</span>
                    </div>
                    <div class="feature-item">
                        <el-icon :size="20"><Cpu /></el-icon>
                        <span>AI 智能识别</span>
                    </div>
                    <div class="feature-item">
                        <el-icon :size="20"><ChatDotRound /></el-icon>
                        <span>协同指挥调度</span>
                    </div>
                </div>
            </div>
            <div class="brand-decoration">
                <div class="deco-circle deco-1"></div>
                <div class="deco-circle deco-2"></div>
                <div class="deco-circle deco-3"></div>
            </div>
        </div>

        <!-- 右侧登录表单 -->
        <div class="login-panel">
            <div class="login-card">
                <div class="login-header">
                    <h2>欢迎登录</h2>
                    <p>请输入您的账号信息</p>
                </div>

                <el-form ref="formRef" :model="form" :rules="rules" class="login-form" @keyup.enter="doLogin">
                    <el-form-item prop="username">
                        <el-input
                            v-model="form.username"
                            placeholder="请输入用户名"
                            size="large"
                            :prefix-icon="User"
                            clearable
                        />
                    </el-form-item>
                    <el-form-item prop="password">
                        <el-input
                            v-model="form.password"
                            type="password"
                            placeholder="请输入密码"
                            size="large"
                            :prefix-icon="Lock"
                            show-password
                            @keyup.enter="doLogin"
                        />
                    </el-form-item>

                    <el-button
                        type="primary"
                        size="large"
                        class="login-btn"
                        :loading="loading"
                        @click="doLogin"
                    >
                        {{ loading ? '登录中...' : '登 录' }}
                    </el-button>
                </el-form>

                <div class="login-tips">
                    <el-alert
                        title="测试账号"
                        type="info"
                        :closable="false"
                        show-icon
                    >
                        <template #default>
                            <div class="tip-accounts">
                                <span>管理员：admin / 123456</span>
                                <span>调度员：operator / 123456</span>
                            </div>
                        </template>
                    </el-alert>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, Ship, DataAnalysis, Monitor, Cpu, ChatDotRound } from '@element-plus/icons-vue'
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
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
    username: '',
    password: ''
})

const rules: FormRules = {
    username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
    password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const doLogin = async () => {
    if (!formRef.value) return
    await formRef.value.validate(async (valid) => {
        if (!valid) return
        loading.value = true
        try {
            const res = await loginApi({
                username: form.username,
                password: form.password
            }) as LoginResult

            if (res.code === 200) {
                localStorage.setItem('token', res.data.token)
                localStorage.setItem('username', res.data.username)
                localStorage.setItem('userRole', res.data.role)
                ElMessage.success('登录成功，欢迎回来！')
                await router.push('/dashboard')
            } else {
                ElMessage.error(res.msg || '用户名或密码错误')
            }
        } catch (err) {
            ElMessage.error('请求失败，请检查后端服务是否正常启动')
            console.error('登录接口异常：', err)
        } finally {
            loading.value = false
        }
    })
}
</script>

<style scoped>
.login-page {
    width: 100vw;
    height: 100vh;
    display: flex;
    overflow: hidden;
}

/* 左侧品牌区 */
.brand-panel {
    flex: 1.2;
    background: linear-gradient(135deg, #0d4a52 0%, #11616B 40%, #1a8a97 100%);
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.brand-content {
    position: relative;
    z-index: 2;
    color: #fff;
    padding: 40px;
    max-width: 480px;
}

.brand-logo {
    width: 80px;
    height: 80px;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 28px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.brand-title {
    font-size: 32px;
    font-weight: 700;
    line-height: 1.4;
    margin-bottom: 16px;
    letter-spacing: 1px;
}

.brand-desc {
    font-size: 15px;
    color: rgba(255, 255, 255, 0.75);
    line-height: 1.8;
    margin-bottom: 40px;
}

.brand-features {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.feature-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    color: rgba(255, 255, 255, 0.85);
    background: rgba(255, 255, 255, 0.08);
    padding: 12px 16px;
    border-radius: 10px;
    backdrop-filter: blur(5px);
    transition: all 0.2s;
}
.feature-item:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateX(4px);
}

/* 装饰圆 */
.brand-decoration {
    position: absolute;
    inset: 0;
    overflow: hidden;
    z-index: 1;
}
.deco-circle {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.06);
}
.deco-1 {
    width: 400px;
    height: 400px;
    top: -150px;
    right: -100px;
}
.deco-2 {
    width: 250px;
    height: 250px;
    bottom: -80px;
    left: -60px;
}
.deco-3 {
    width: 150px;
    height: 150px;
    top: 40%;
    right: 20%;
    background: rgba(123, 189, 182, 0.15);
}

/* 右侧登录区 */
.login-panel {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f0f4f8;
    padding: 40px;
}

.login-card {
    width: 100%;
    max-width: 400px;
    background: #fff;
    border-radius: 20px;
    padding: 40px 36px;
    box-shadow: 0 20px 60px rgba(17, 97, 107, 0.12);
}

.login-header {
    text-align: center;
    margin-bottom: 32px;
}
.login-header h2 {
    font-size: 26px;
    font-weight: 700;
    color: #11616B;
    margin-bottom: 8px;
}
.login-header p {
    font-size: 14px;
    color: #909399;
}

.login-form {
    margin-bottom: 20px;
}

.login-btn {
    width: 100%;
    height: 44px;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: 4px;
    margin-top: 8px;
}

.login-tips {
    margin-top: 16px;
}
.tip-accounts {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 12px;
    color: #606266;
}

/* 响应式 */
@media (max-width: 900px) {
    .brand-panel {
        display: none;
    }
    .login-panel {
        flex: 1;
    }
}
</style>
