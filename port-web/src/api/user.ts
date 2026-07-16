import request from '../utils/request'
export function getUserList() {
    return request({ url: '/api/user/list', method: 'get' })
}
export function addUser(data: any) {
    return request({ url: '/api/user/add', method: 'post', data })
}
export function updateUser(data: any) {
    return request({ url: '/api/user/update', method: 'put', data })
}