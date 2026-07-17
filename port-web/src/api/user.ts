import request from '../utils/request'

// 获取用户列表
export function getUserList() {
    return request({ url: '/api/user/list', method: 'get' })
}

// 新增用户
export function addUser(data: any) {
    return request({ url: '/api/user/add', method: 'post', data })
}

// 编辑修改用户
export function updateUser(data: any) {
    return request({ url: '/api/user/update', method: 'put', data })
}

// 【新增】根据ID删除用户接口
export function deleteUser(userId: number) {
    return request({
        url: `/api/user/remove/${userId}`,
        method: 'delete'
    })
}

