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
        try {
            const containerRes: any = await getAllContainer()
            const slotRes: any = await getAllYardSlot()
            // request.ts已剥离Result外层，直接返回data本身（数组）
            containerList.value = Array.isArray(containerRes) ? containerRes : (containerRes?.data || containerRes?.records || [])
            slotList.value = Array.isArray(slotRes) ? slotRes : (slotRes?.data || slotRes?.records || [])
        } catch (e) {
            containerList.value = []
            slotList.value = []
        }
    }

    return {
        containerList,
        slotList,
        refreshAllData
    }
})
