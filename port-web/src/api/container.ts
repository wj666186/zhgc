import request from '../utils/request'

// 状态类型
export type ContainerStatus = 0 | 1 | 2 | 3

// 集装箱实体类型 和后端字段一一对应
export interface ContainerItem {
    id: number
    containerNo: string
    cargoType: string
    destPort: string
    weight: number
    status: ContainerStatus
    yardSlotId: number | null
    areaNo: number | null
    loadStatus: 0 | 1
    createTime: string
    updateTime: string
}

// 堆场仓位实体类型
export interface YardSlotItem {
    id: number
    areaCode: string
    rowNo: number
    colNo: number
    maxLayer: number
    usedLayer: number
    lockContainerId: number | null
}

// 分页返回结构
interface PageRes<T> {
    records: T[]
    total: number
    size: number
    current: number
}

// 1. 分页查询集装箱列表
export const getContainerList = (pageNum: number, pageSize: number) => {
    return request.get<PageRes<ContainerItem>>('/api/container/list', {
        params: { pageNum, pageSize }
    })
}

// 2. 新增集装箱
export const addContainer = (data: Omit<ContainerItem, 'id' | 'createTime' | 'updateTime'>) => {
    return request.post('/api/container/add', data)
}

// 3. 编辑修改集装箱
export const updateContainer = (data: Partial<ContainerItem>) => {
    return request.put('/api/container/update', data)
}

// 4. 删除集装箱
export const delContainer = (id: number) => {
    return request.delete(`/api/container/${id}`)
}

// 5. 根据箱号分配堆场仓位
export const allocateYardByNo = (containerNo: string) => {
    return request.post('/yard/allocate', null, {
        params: { containerNo }
    })
}

// 6. 数字孪生视图+全局仓库：拉取全部集装箱（无分页）
export const getAllContainer = () => {
    return request.get<ContainerItem[]>('/api/container/twin')
}

// 7. 获取所有堆场仓位数据
export const getAllYardSlot = () => {
    return request.get<YardSlotItem[]>('/api/yard/list')
}
