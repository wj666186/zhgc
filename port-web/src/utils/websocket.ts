import { useContainerStore } from '../stores/container'

let ws: WebSocket | null = null
// 定义类型：允许null
let customMsgCallback: ((msg: string) => void) | null = null
const store = useContainerStore()

// 入参设置可选回调
export function initWebSocket(callback?: (msg: string) => void) {
    if (callback) {
        customMsgCallback = callback
    }

    // 防止重复创建连接
    if (ws && ws.readyState !== WebSocket.CLOSED) return

    ws = new WebSocket('ws://localhost:8080/ws/container')

    ws.onmessage = (event) => {
        // 先判断不为null再执行回调
        if (customMsgCallback) {
            customMsgCallback(event.data)
        }

        if (event.data === 'container_refresh') {
            setTimeout(() => {
                // void 忽略Promise返回值，消除警告
                void store.refreshAllData()
            }, 350)
        }
    }

    ws.onclose = () => {
        // 传入时做类型兜底：null转为undefined，匹配入参可选类型
        setTimeout(() => initWebSocket(customMsgCallback ?? undefined), 3000)
    }

    ws.onerror = () => {
        setTimeout(() => initWebSocket(customMsgCallback ?? undefined), 3000)
    }
}

