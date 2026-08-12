import request from '../utils/request'

export interface DashboardStats {
  containerTotal: number
  containerNormal: number
  containerWorking: number
  containerDamage: number
  truckTotal: number
  truckIdle: number
  truckWorking: number
  vesselTotal: number
  vesselWorking: number
  craneTotal: number
  craneWorking: number
  rtgTotal: number
  aiTotal: number
}

export const getDashboardStats = () => request.get<DashboardStats>('/api/dashboard/stats')

export const getContainerStatus = () => request.get<any[]>('/api/dashboard/container/status')

export const getTruckStatus = () => request.get<any[]>('/api/dashboard/truck/status')

export const getEquipmentOee = () => request.get<any[]>('/api/dashboard/equipment/oee')

export const getThroughputTrend = () => request.get<any[]>('/api/dashboard/throughput/trend')

export const getGateEfficiency = () => request.get<any[]>('/api/dashboard/gate/efficiency')

export const getVesselTop = () => request.get<any[]>('/api/dashboard/vessel/top')
