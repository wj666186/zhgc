import request from '../utils/request'

export interface OperationLogItem {
  id: number
  logNo: string
  username: string
  userRole: string
  module: string
  operation: string
  description: string
  requestMethod: string
  requestUrl: string
  requestParams: string
  ipAddress: string
  result: number
  errorMsg: string
  costMs: number
  createTime: string
}

interface PageRes<T> {
  records: T[]
  total: number
  size: number
  current: number
}

export const getLogList = (pageNum: number, pageSize: number, params?: Record<string, any>) =>
  request.get<PageRes<OperationLogItem>>('/api/log/list', { params: { pageNum, pageSize, ...params } })

export const getLogModules = () => request.get<string[]>('/api/log/modules')

export const deleteLog = (id: number) => request.delete(`/api/log/${id}`)
