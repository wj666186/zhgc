import request from '../utils/request'

export interface CommandItem {
  id: number
  target: string
  commandType: string
  content: string
  operator: string
  createTime: string
}

export const sendCommand = (data: { target: string; commandType: string; content: string; operator: string }) =>
  request.post('/api/command/send', data)

export const broadcastCommand = (data: { content: string }) =>
  request.post('/api/command/broadcast', data)

export const sendAlert = (data: { level: string; content: string }) =>
  request.post('/api/command/alert', data)

export const getOnlineCount = () => request.get<number>('/api/command/online/count')

export const getCommandHistory = () => request.get<CommandItem[]>('/api/command/history')
