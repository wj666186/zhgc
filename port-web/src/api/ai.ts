import request from '../utils/request'

export interface AiInspectRecord {
  id: number
  inspectNo: string
  containerNo: string
  inspectType: string
  ocrResult: string
  damageResult: string
  damageLevel: string
  stackResult: string
  confidence: number
  imageUrl: string
  imageName: string
  inspectTime: string
  inspector: string
  status: number
  remark: string
  costMs: number
  createTime: string
}

interface PageRes<T> {
  records: T[]
  total: number
  size: number
  current: number
}

// 本地上传图片识别（multipart/form-data）
export const inspectImage = (file: File, containerNo?: string) => {
  const formData = new FormData()
  formData.append('file', file)
  if (containerNo) formData.append('containerNo', containerNo)
  return request.post<AiInspectRecord>('/api/ai/inspect', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 历史检测记录列表
export const getInspectList = (pageNum: number, pageSize: number, containerNo?: string) => {
  return request.get<PageRes<AiInspectRecord>>('/api/ai/list', {
    params: { pageNum, pageSize, containerNo }
  })
}

// 历史记录（不分页）
export const getInspectHistory = (limit?: number) => {
  return request.get<AiInspectRecord[]>('/api/ai/history', { params: { limit } })
}

// 删除记录
export const deleteInspect = (id: number) => {
  return request.delete(`/api/ai/${id}`)
}
