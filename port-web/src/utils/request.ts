import axios, { type AxiosResponse } from 'axios'

// 创建axios实例
const request = axios.create({
    baseURL: 'http://localhost:8080',
    timeout: 10000
})

// 请求拦截器：自动携带token
request.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// 响应拦截器
request.interceptors.response.use(
    (res: AxiosResponse<any, any>) => res.data,
    (err) => {
        // 未登录强制跳转登录页
        if (err.response?.data?.code === 401) {
            localStorage.removeItem('token')
            location.href = '/login'
        }
        return Promise.reject(err)
    }
)

export default request