import request from '../utils/request'

export interface GateRecordItem {
  id: number
  passNo: string
  gateNo: string
  direction: number
  plateNo: string
  containerNo: string
  appointmentNo: string
  etcResult: number
  rfidResult: number
  ocrContainerNo: string
  customsStatus: number
  verifyStatus: number
  enterTime: string
  exitTime: string
  stayMinutes: number
  operator: string
  remark: string
  createTime: string
}

interface PageRes<T> {
  records: T[]
  total: number
  size: number
  current: number
}

export const getGateList = (pageNum: number, pageSize: number, params?: Record<string, any>) =>
  request.get<PageRes<GateRecordItem>>('/api/gate/list', { params: { pageNum, pageSize, ...params } })

export const getGateStats = () => request.get<Record<string, number>>('/api/gate/stats')

export const verifyGate = (data: { plateNo: string; containerNo: string; appointmentNo: string }) =>
  request.post('/api/gate/verify', data)

export const exitGate = (id: number) => request.put(`/api/gate/exit/${id}`)

export const getGateByPassNo = (passNo: string) => request.get<GateRecordItem>(`/api/gate/pass/${passNo}`)

export const deleteGate = (id: number) => request.delete(`/api/gate/${id}`)
