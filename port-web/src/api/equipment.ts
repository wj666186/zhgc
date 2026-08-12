import request from '../utils/request'

export interface QuayCraneItem {
  id: number
  craneNo: string
  berthNo: string
  model: string
  status: number
  operator: string
  currentVessel: string
  trolleyPosition: number
  gantryPosition: number
  liftHeight: number
  spreaderStatus: number
  todayBoxCount: number
  totalBoxCount: number
  oee: number
  faultDesc: string
  lastHeartbeat: string
  createTime: string
  updateTime: string
}

export interface RtgItem {
  id: number
  rtgNo: string
  yardArea: string
  model: string
  status: number
  operator: string
  currentContainerNo: string
  currentRow: number
  currentCol: number
  liftHeight: number
  spreaderStatus: number
  todayBoxCount: number
  totalBoxCount: number
  oee: number
  faultDesc: string
  lastHeartbeat: string
  createTime: string
  updateTime: string
}

interface PageRes<T> {
  records: T[]
  total: number
  size: number
  current: number
}

// 岸桥
export const getCraneList = (pageNum: number, pageSize: number, craneNo?: string, status?: number) =>
  request.get<PageRes<QuayCraneItem>>('/api/equipment/crane/list', { params: { pageNum, pageSize, craneNo, status } })

export const getAllCrane = () => request.get<QuayCraneItem[]>('/api/equipment/crane/all')

export const addCrane = (data: Partial<QuayCraneItem>) => request.post('/api/equipment/crane/add', data)

export const updateCrane = (data: Partial<QuayCraneItem>) => request.put('/api/equipment/crane/update', data)

export const deleteCrane = (id: number) => request.delete(`/api/equipment/crane/${id}`)

export const startCrane = (data: { id: number; currentVessel: string }) =>
  request.post('/api/equipment/crane/start', data)

export const finishCrane = (id: number) => request.put(`/api/equipment/crane/finish/${id}`)

export const faultCrane = (data: { id: number; faultDesc: string }) =>
  request.post('/api/equipment/crane/fault', data)

export const heartbeatCrane = (id: number) => request.post(`/api/equipment/crane/heartbeat/${id}`)

// 龙门吊
export const getRtgList = (pageNum: number, pageSize: number, rtgNo?: string, status?: number) =>
  request.get<PageRes<RtgItem>>('/api/equipment/rtg/list', { params: { pageNum, pageSize, rtgNo, status } })

export const getAllRtg = () => request.get<RtgItem[]>('/api/equipment/rtg/all')

export const addRtg = (data: Partial<RtgItem>) => request.post('/api/equipment/rtg/add', data)

export const updateRtg = (data: Partial<RtgItem>) => request.put('/api/equipment/rtg/update', data)

export const deleteRtg = (id: number) => request.delete(`/api/equipment/rtg/${id}`)

export const startRtg = (data: { id: number; containerNo: string }) =>
  request.post('/api/equipment/rtg/start', data)

export const finishRtg = (id: number) => request.put(`/api/equipment/rtg/finish/${id}`)

export const faultRtg = (data: { id: number; faultDesc: string }) =>
  request.post('/api/equipment/rtg/fault', data)

export const heartbeatRtg = (id: number) => request.post(`/api/equipment/rtg/heartbeat/${id}`)
