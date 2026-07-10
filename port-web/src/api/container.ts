import request from '../utils/request'

// 分页查询列表
export function getContainerList(params: any) {
    return request({
        url: '/api/container/list',
        method: 'get',
        params
    })
}

// 编辑更新
export function updateContainer(data: any) {
    return request({
        url: '/api/container/update',
        method: 'put',
        data
    })
}

// 根据ID删除
export function delContainer(id: number) {
    return request({
        url: `/api/container/${id}`,
        method: 'delete'
    })
}

// 新增集装箱
export function addContainer(data: any) {
    return request({
        url: '/api/container/add',
        method: 'post',
        data
    })
}
// 标记损坏锁定
export function markDamageContainer(containerNo: string) {
    return request({
        url: '/api/container/damage',
        method: 'put',
        data: { containerNo }
    })
}