import { defineStore } from 'pinia'
import { ref } from 'vue'
// 导入类型 + 接口一一对应
import type { ContainerItem, YardSlotItem } from '../api/container'
import { getAllContainer, getAllYardSlot } from '../api/container'

export const useContainerStore = defineStore('container', () => {
    // 响应式数据声明
    const containerList = ref<ContainerItem[]>([])
    const slotList = ref<YardSlotItem[]>([])

    // 全局刷新：集装箱+仓位全部重载
    const refreshAllData = async (): Promise<void> => {
        const containerRes = await getAllContainer()
        const slotRes = await getAllYardSlot()
        containerList.value = containerRes.data
        slotList.value = slotRes.data
    }

    return {
        containerList,
        slotList,
        refreshAllData
    }
})
