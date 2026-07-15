import request from '../utils/request'

// 通用后端返回格式
interface BaseResp<T = any> {
    code: number
    data: T
    msg: string
}

// 分页结构
interface PageResult<T> {
    records: T[]
    total: number
    current: number
    size: number
}

// 集装箱实体
export interface ContainerItem {
    id?: number
    containerNo: string
    goodsType: string
    targetPort: string
    weight: number
    status: string
    storeSlot?: string
    isDamage?: number
}

// 分页查询列表
export function getContainerList(params: any): Promise<BaseResp<PageResult<ContainerItem>>> {
    return request({
        url: '/api/container/list',
        method: 'get',
        params
    })
}

// 编辑更新
export function updateContainer(data: ContainerItem): Promise<BaseResp> {
    return request({
        url: '/api/container/update',
        method: 'put',
        data
    })
}

// 根据ID删除
export function delContainer(id: number): Promise<BaseResp> {
    return request({
        url: `/api/container/${id}`,
        method: 'delete'
    })
}

// 新增集装箱
export function addContainer(data: Omit<ContainerItem, 'id'>): Promise<BaseResp> {
    return request({
        url: '/api/container/add',
        method: 'post',
        data
    })
}

// 标记损坏锁定
export function markDamageContainer(containerNo: string): Promise<BaseResp> {
    return request({
        url: '/api/container/damage',
        method: 'put',
        data: { containerNo }
    })
}