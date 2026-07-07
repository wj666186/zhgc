import axios from 'axios'

const service = axios.create({
    baseURL: 'http://localhost:8080',
    timeout: 12000
})

service.interceptors.request.use(config => {
    return config
})

service.interceptors.response.use(
    res => res.data,
    err => {
        console.error('接口请求异常', err)
        return Promise.reject(err)
    }
)

export default service