<template>
    <div class="login-container">
        <!-- 背景动画：港口抽象线条 -->
        <div class="bg-animation">
            <div class="wave wave1"></div>
            <div class="wave wave2"></div>
            <div class="wave wave3"></div>
        </div>

        <!-- 登录卡片 -->
        <div class="login-card">
            <!-- Logo与标题 -->
            <div class="login-header">
                <div class="logo-container">
                    <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M3 12L7 8L11 12L15 8L19 12L21 10" stroke-width="2" stroke-linecap="round"/>
                        <path d="M3 18L7 14L11 18L15 14L19 18L21 16" stroke-width="2" stroke-linecap="round"/>
                        <rect x="2" y="20" width="20" height="2" rx="1"/>
                        <path d="M7 8V12" stroke-width="2"/>
                        <path d="M15 8V12" stroke-width="2"/>
                    </svg>
                    <span class="logo-text">PortFlow</span>
                    <span class="logo-badge">智慧港口</span>
                </div>
                <h1>集装箱调度系统</h1>
                <p class="subtitle">Container Dispatch & Logistics Collaboration</p>
            </div>

            <!-- 登录表单 -->
            <form class="login-form" @submit.prevent="handleLogin">
                <div class="form-group">
                    <label for="username">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                            <circle cx="12" cy="7" r="4"/>
                        </svg>
                        用户名 / 工号
                    </label>
                    <input
                            id="username"
                            v-model="loginForm.username"
                            type="text"
                            placeholder="请输入用户名或工号"
                            autocomplete="username"
                            required
                    />
                </div>

                <div class="form-group">
                    <label for="password">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="11" width="18" height="11" rx="2"/>
                            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                        </svg>
                        密码
                    </label>
                    <div class="password-wrapper">
                        <input
                                id="password"
                                v-model="loginForm.password"
                                :type="showPassword ? 'text' : 'password'"
                                placeholder="请输入密码"
                                autocomplete="current-password"
                                required
                        />
                        <button
                                type="button"
                                class="toggle-password"
                                @click="showPassword = !showPassword"
                        >
                            <svg v-if="showPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                                <circle cx="12" cy="12" r="3"/>
                            </svg>
                            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                                <line x1="1" y1="1" x2="23" y2="23"/>
                            </svg>
                        </button>
                    </div>
                </div>

                <!-- 角色选择与记住我 -->
                <div class="form-options">
                    <div class="role-selector">
                        <span class="role-label">登录角色</span>
                        <div class="role-buttons">
                            <button
                                    v-for="role in roles"
                                    :key="role.value"
                                    type="button"
                                    class="role-btn"
                                    :class="{ active: loginForm.role === role.value }"
                                    @click="loginForm.role = role.value"
                            >
                                {{ role.label }}
                            </button>
                        </div>
                    </div>
                    <label class="remember-me">
                        <input v-model="loginForm.remember" type="checkbox" />
                        <span>记住账号</span>
                    </label>
                </div>

                <!-- 登录按钮 -->
                <button type="submit" class="login-btn" :disabled="loading">
                    <span v-if="!loading">登 录</span>
                    <span v-else class="loading-spinner">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" stroke-dasharray="60" stroke-dashoffset="30">
                <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
              </circle>
            </svg>
          </span>
                </button>

                <!-- 系统状态 -->
                <div class="system-status">
                    <span class="status-dot"></span>
                    <span>系统运行中 · 调度中台 v3.3</span>
                </div>
            </form>

            <!-- 底部信息 -->
            <div class="login-footer">
                <span>© 2026 PortFlow · 智慧港口集装箱调度系统</span>
                <span class="divider">|</span>
                <span>ISO/PAS 20500 合规</span>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

// 路由实例
const router = useRouter()

// 登录表单数据
const loginForm = reactive({
    username: '',
    password: '',
    role: 'dispatcher', // dispatcher | operator | driver
    remember: false
})

// UI状态
const loading = ref(false)
const showPassword = ref(false)

// 角色选项
const roles = [
    { label: '调度员', value: 'dispatcher' },
    { label: '操作员', value: 'operator' },
    { label: '司机', value: 'driver' }
]

// 登录处理函数
const handleLogin = async () => {
    // 表单校验
    if (!loginForm.username.trim() || !loginForm.password.trim()) {
        ElMessage.warning('请输入用户名和密码')
        return
    }

    loading.value = true

    try {
        // 模拟API请求（实际项目中替换为真实接口）
        const mockLogin = () => {
            return new Promise<{ success: boolean; token: string; role: string }>((resolve) => {
                setTimeout(() => {
                    resolve({
                        success: true,
                        token: `mock-token-${Date.now()}`,
                        role: loginForm.role
                    })
                }, 1500)
            })
        }

        const result = await mockLogin()

        if (result.success) {
            // 存储登录信息
            localStorage.setItem('token', result.token)
            localStorage.setItem('userRole', result.role)
            if (loginForm.remember) {
                localStorage.setItem('rememberedUser', loginForm.username)
            }

            ElMessage.success(`登录成功！欢迎 ${loginForm.username}`)

            // 根据角色跳转不同页面
            const routeMap: Record<string, string> = {
                dispatcher: '/dashboard',
                operator: '/yard',
                driver: '/container'
            }

            setTimeout(() => {
                router.push(routeMap[loginForm.role] || '/dashboard')
            }, 500)
        }
    } catch (error) {
        ElMessage.error('登录失败，请检查网络连接')
    } finally {
        loading.value = false
    }
}

// 自动填充记住的用户名
onMounted(() => {
    const remembered = localStorage.getItem('rememberedUser')
    if (remembered) {
        loginForm.username = remembered
        loginForm.remember = true
    }
})
</script>

<style scoped>
/* ========== 整体容器 ========== */
.login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #0b1a2a 0%, #1a3a4a 40%, #2a5a6a 100%);
    position: relative;
    overflow: hidden;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* ========== 背景波浪动画 ========== */
.bg-animation {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    overflow: hidden;
}

.wave {
    position: absolute;
    bottom: -10%;
    left: -50%;
    width: 200%;
    height: 40%;
    background: rgba(64, 164, 223, 0.06);
    border-radius: 50% 50% 0 0;
    animation: waveMove 8s ease-in-out infinite;
}

.wave1 {
    bottom: -5%;
    background: rgba(64, 164, 223, 0.04);
    animation-duration: 10s;
    animation-delay: -2s;
}

.wave2 {
    bottom: -8%;
    background: rgba(64, 164, 223, 0.03);
    animation-duration: 14s;
    animation-delay: -4s;
    width: 250%;
}

.wave3 {
    bottom: -12%;
    background: rgba(0, 180, 216, 0.02);
    animation-duration: 18s;
    animation-delay: -6s;
    width: 300%;
}

@keyframes waveMove {
    0%, 100% { transform: translateX(0) scaleY(0.8); }
    25% { transform: translateX(5%) scaleY(1); }
    50% { transform: translateX(10%) scaleY(0.9); }
    75% { transform: translateX(5%) scaleY(1.1); }
}

/* ========== 登录卡片 ========== */
.login-card {
    position: relative;
    z-index: 2;
    width: 100%;
    max-width: 440px;
    padding: 40px 36px 32px;
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 32px;
    box-shadow:
            0 30px 80px rgba(0, 0, 0, 0.4),
            0 0 0 1px rgba(255, 255, 255, 0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.login-card:hover {
    transform: translateY(-2px);
    box-shadow:
            0 40px 100px rgba(0, 0, 0, 0.5),
            0 0 0 1px rgba(255, 255, 255, 0.12);
}

/* ========== 头部 ========== */
.login-header {
    margin-bottom: 32px;
}

.logo-container {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}

.logo-icon {
    width: 36px;
    height: 36px;
    color: #0a7e8c;
    flex-shrink: 0;
}

.logo-text {
    font-size: 22px;
    font-weight: 700;
    color: #0b1a2a;
    letter-spacing: -0.5px;
}

.logo-badge {
    font-size: 10px;
    font-weight: 600;
    padding: 2px 12px;
    background: linear-gradient(135deg, #0a7e8c, #0b5a6a);
    color: #fff;
    border-radius: 20px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.login-header h1 {
    font-size: 26px;
    font-weight: 700;
    color: #0b1a2a;
    margin: 0 0 4px;
    letter-spacing: -0.5px;
}

.subtitle {
    font-size: 13px;
    color: #5a7a8a;
    font-weight: 400;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

/* ========== 表单 ========== */
.login-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.form-group label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 500;
    color: #1a3a4a;
    letter-spacing: 0.3px;
}

.form-group label svg {
    color: #5a8a9a;
}

.form-group input {
    padding: 12px 16px;
    border: 1.5px solid #dce8ee;
    border-radius: 12px;
    font-size: 15px;
    font-family: inherit;
    color: #0b1a2a;
    background: #f8fafc;
    transition: all 0.2s ease;
    outline: none;
}

.form-group input:focus {
    border-color: #0a7e8c;
    background: #ffffff;
    box-shadow: 0 0 0 4px rgba(10, 126, 140, 0.12);
}

.form-group input::placeholder {
    color: #a0b8c8;
}

.password-wrapper {
    position: relative;
}

.password-wrapper input {
    width: 100%;
    padding-right: 48px;
}

.toggle-password {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: #8aacbc;
    cursor: pointer;
    padding: 4px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.2s;
}

.toggle-password:hover {
    color: #0a7e8c;
}

/* ========== 表单选项 ========== */
.form-options {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 4px 0;
}

.role-selector {
    display: flex;
    align-items: center;
    gap: 8px;
}

.role-label {
    font-size: 12px;
    font-weight: 500;
    color: #5a7a8a;
}

.role-buttons {
    display: flex;
    gap: 4px;
}

.role-btn {
    padding: 4px 14px;
    font-size: 12px;
    font-weight: 500;
    border: 1.5px solid #dce8ee;
    border-radius: 20px;
    background: transparent;
    color: #5a7a8a;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: inherit;
}

.role-btn:hover {
    border-color: #8aacbc;
    color: #1a3a4a;
}

.role-btn.active {
    background: #0a7e8c;
    border-color: #0a7e8c;
    color: #fff;
}

.remember-me {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #4a6a7a;
    cursor: pointer;
}

.remember-me input[type="checkbox"] {
    width: 16px;
    height: 16px;
    accent-color: #0a7e8c;
    border-radius: 4px;
    cursor: pointer;
}

/* ========== 登录按钮 ========== */
.login-btn {
    width: 100%;
    padding: 14px;
    font-size: 16px;
    font-weight: 600;
    font-family: inherit;
    color: #fff;
    background: linear-gradient(135deg, #0a7e8c, #0b5a6a);
    border: none;
    border-radius: 14px;
    cursor: pointer;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
    letter-spacing: 0.5px;
    margin-top: 4px;
}

.login-btn:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 8px 30px rgba(10, 126, 140, 0.35);
}

.login-btn:active:not(:disabled) {
    transform: scale(0.98);
}

.login-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.loading-spinner {
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.loading-spinner svg {
    color: #fff;
}

/* ========== 系统状态 ========== */
.system-status {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 12px;
    color: #6a8a9a;
    padding: 8px 0 4px;
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #00c853;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ========== 底部 ========== */
.login-footer {
    margin-top: 28px;
    padding-top: 20px;
    border-top: 1px solid #e8eef2;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 12px;
    font-size: 12px;
    color: #6a8a9a;
}

.divider {
    color: #c0d0d8;
}

/* ========== 响应式 ========== */
@media (max-width: 480px) {
    .login-card {
        padding: 28px 20px 24px;
        border-radius: 24px;
        margin: 12px;
    }

    .login-header h1 {
        font-size: 22px;
    }

    .logo-text {
        font-size: 18px;
    }

    .form-options {
        flex-direction: column;
        align-items: stretch;
    }

    .role-selector {
        flex-wrap: wrap;
    }
}
</style>