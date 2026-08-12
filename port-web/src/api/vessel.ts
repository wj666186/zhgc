import request from '../utils/request'

export interface VesselPlanItem {
  id: number
  vesselName: string
  imoNo: string
  shippingCompany: string
  routeLine: string
  berthWindowStart: string
  berthWindowEnd: string
  actualBerthTime: string
  actualDepartureTime: string
  totalContainer: number
  finishedContainer: number
  berthNo: string
  status: number
  operator: string
  remark: string
  createTime: string
  updateTime: string
}

interface PageRes<T> {
  records: T[]
  total: number
  size: number
  current: number
}

export const getVesselList = (pageNum: number, pageSize: number, vesselName?: string, status?: number) =>
  request.get<PageRes<VesselPlanItem>>('/api/vessel/list', { params: { pageNum, pageSize, vesselName, status } })

export const getAllVessel = () => request.get<VesselPlanItem[]>('/api/vessel/all')

export const addVessel = (data: Partial<VesselPlanItem>) => request.post('/api/vessel/add', data)

export const updateVessel = (data: Partial<VesselPlanItem>) => request.put('/api/vessel/update', data)

export const deleteVessel = (id: number) => request.delete(`/api/vessel/${id}`)

export const berthVessel = (id: number) => request.put(`/api/vessel/berth/${id}`)

export const finishVessel = (id: number) => request.put(`/api/vessel/finish/${id}`)

export const departureVessel = (id: number) => request.put(`/api/vessel/departure/${id}`)

export const cancelVessel = (id: number) => request.put(`/api/vessel/cancel/${id}`)
