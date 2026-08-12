import request from '../utils/request'

export interface TruckItem {
  id: number
  plateNo: string
  driverName: string
  driverPhone: string
  truckType: number
  status: number
  currentContainerNo: string
  startLocation: string
  targetLocation: string
  longitude: number
  latitude: number
  todayTaskCount: number
  totalMileage: number
  createTime: string
  updateTime: string
}

interface PageRes<T> {
  records: T[]
  total: number
  size: number
  current: number
}

export const getTruckList = (pageNum: number, pageSize: number, plateNo?: string, status?: number) => {
  return request.get<PageRes<TruckItem>>('/api/truck/list', { params: { pageNum, pageSize, plateNo, status } })
}

export const getAllTruck = () => request.get<TruckItem[]>('/api/truck/all')

export const getIdleTruck = () => request.get<TruckItem[]>('/api/truck/idle')

export const getTruckStats = () => request.get<Record<string, number>>('/api/truck/stats')

export const addTruck = (data: Partial<TruckItem>) => request.post('/api/truck/add', data)

export const updateTruck = (data: Partial<TruckItem>) => request.put('/api/truck/update', data)

export const deleteTruck = (id: number) => request.delete(`/api/truck/${id}`)

export const assignTruck = (data: { truckId: number; containerNo: string; targetLocation: string }) =>
  request.post('/api/truck/assign', data)

export const finishTruck = (id: number) => request.put(`/api/truck/finish/${id}`)

export const updateTruckGps = (data: { truckId: number; longitude: number; latitude: number }) =>
  request.post('/api/truck/gps', data)
