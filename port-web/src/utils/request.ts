import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
    baseURL: 'http://localhost:8080',
    timeout: 10000
})

// 请求拦截自动带上token
service.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = token
    }
    return config
})

// 响应拦截直接剥离外层data
service.interceptors.response.use(res => {
    return res.data
}, err => {
    ElMessage.error('网络请求异常')
    return Promise.reject(err)
})

export default service