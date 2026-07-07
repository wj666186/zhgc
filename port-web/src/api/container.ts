import request from '../utils/request'

// 分页查询集装箱
export function getContainerList(params: any) {
    return request({
        url: '/container/list',
        method: 'get',
        params
    })
}

// 自动分配堆场
export function autoAllocateYard(containerNo: string) {
    return request({
        url: '/yard/allocate',
        method: 'post',
        data: { containerNo }
    })
}

// 标记集装箱损坏锁定
export function markDamageContainer(containerNo: string) {
    return request({
        url: '/container/damage',
        method: 'put',
        data: { containerNo }
    })
}