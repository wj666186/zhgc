import request from '../utils/request'

interface LoginRes {
    code: number
    msg: string
    data: {
        token: string
        username: string
    }
}

export function loginApi(data: { username: string; password: string }): Promise<LoginRes> {
    return request({
        url: 'http://localhost:8080/api/login',
        method: 'post',
        data
    })
}