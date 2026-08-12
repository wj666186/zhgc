<template>
  <div class="command-page">
    <div class="page-header">
      <h2>实时协同指挥</h2>
      <div class="ws-status">
        <el-tag :type="wsConnected ? 'success' : 'danger'" size="large">
          {{ wsConnected ? 'WebSocket已连接' : 'WebSocket未连接' }}
        </el-tag>
        <span style="margin-left: 12px; color: #606266;">在线设备: {{ onlineCount }}</span>
      </div>
    </div>

    <div class="content-row">
      <!-- 左侧：指令下发 -->
      <div class="left-panel">
        <el-card class="panel-card">
          <template #header><span style="font-weight: bold;">指令下发</span></template>
          <el-form :model="commandForm" label-width="80px">
            <el-form-item label="目标">
              <el-input v-model="commandForm.target" placeholder="如 QC01 / RTG06 / 新A10001" />
            </el-form-item>
            <el-form-item label="指令类型">
              <el-select v-model="commandForm.commandType" style="width: 100%">
                <el-option label="岸桥抓取" value="crane_lift" />
                <el-option label="岸桥放置" value="crane_place" />
                <el-option label="龙门吊移动" value="rtg_move" />
                <el-option label="集卡调度" value="truck_dispatch" />
                <el-option label="停机指令" value="stop" />
                <el-option label="告警通知" value="alert" />
                <el-option label="通用指令" value="general" />
              </el-select>
            </el-form-item>
            <el-form-item label="内容">
              <el-input v-model="commandForm.content" type="textarea" :rows="3" placeholder="请输入指令内容" />
            </el-form-item>
            <el-form-item label="操作员">
              <el-input v-model="commandForm.operator" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSend">下发指令</el-button>
              <el-button type="success" @click="handleBroadcast">全局广播</el-button>
              <el-button type="warning" @click="handleAlert">告警通知</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card class="panel-card" style="margin-top: 12px;">
          <template #header><span style="font-weight: bold;">快捷广播</span></template>
          <div class="quick-btns">
            <el-button v-for="msg in quickMessages" :key="msg" size="small" @click="quickBroadcast(msg)">{{ msg }}</el-button>
          </div>
        </el-card>
      </div>

      <!-- 右侧：指令历史 -->
      <div class="right-panel">
        <el-card class="panel-card history-card">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: bold;">指令历史</span>
              <el-button size="small" @click="loadHistory">刷新</el-button>
            </div>
          </template>
          <div class="history-list">
            <div v-for="item in historyList" :key="item.id" class="history-item" :class="'type-' + (item.type || 'command')">
              <div class="history-header">
                <el-tag v-if="item.type === 'broadcast'" size="small" type="success">全局广播</el-tag>
                <el-tag v-else-if="item.type === 'alert'" size="small" type="warning">告警通知</el-tag>
                <template v-else>
                  <el-tag size="small" type="primary">{{ item.target || '未指定' }}</el-tag>
                  <el-tag size="small" style="margin-left: 6px;">{{ commandTypeText(item.commandType) }}</el-tag>
                </template>
                <span class="history-time">{{ item.createTime }}</span>
              </div>
              <div class="history-content">{{ item.content }}</div>
              <div class="history-operator">
                <span>操作员: {{ item.operator || 'system' }}</span>
                <span v-if="item.level" style="margin-left: 12px;">级别: {{ item.level }}</span>
              </div>
            </div>
            <el-empty v-if="historyList.length === 0" description="暂无指令记录" />
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { sendCommand, broadcastCommand, sendAlert, getOnlineCount, getCommandHistory } from '@/api/command'
import type { CommandItem } from '@/api/command'

const wsConnected = ref(false)
const onlineCount = ref(0)
const historyList = ref<CommandItem[]>([])

const commandForm = ref({
  target: '',
  commandType: 'general',
  content: '',
  operator: localStorage.getItem('username') || 'admin'
})

const quickMessages = ['12点交接班', '注意大风天气', '泊位B1有船靠泊', '闸口G2拥堵', '全场停止作业']

const commandTypeText = (type: string) => {
  const map: Record<string, string> = {
    crane_lift: '岸桥抓取', crane_place: '岸桥放置', rtg_move: '龙门吊移动',
    truck_dispatch: '集卡调度', stop: '停机指令', alert: '告警通知', general: '通用指令'
  }
  return map[type] || type || '通用指令'
}

let ws: WebSocket | null = null

const connectWs = () => {
  try {
    const token = localStorage.getItem('token') || ''
    ws = new WebSocket(`ws://localhost:8080/ws/container?token=${token}`)
    ws.onopen = () => { wsConnected.value = true; ElMessage.success('WebSocket连接成功') }
    ws.onclose = () => { wsConnected.value = false }
    ws.onerror = () => { wsConnected.value = false }
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        ElMessage.info(`收到指令: ${data.content || data.type}`)
      } catch (e) { /* ignore */ }
    }
  } catch (e) {
    wsConnected.value = false
  }
}

const loadOnlineCount = async () => {
  try {
    const res: any = await getOnlineCount()
    const data = res?.data || res
    onlineCount.value = typeof data === 'number' ? data : (data?.count || 0)
  } catch (e) {
    onlineCount.value = 0
  }
}

const loadHistory = async () => {
  try {
    const res: any = await getCommandHistory()
    const data = res?.data || res
    historyList.value = Array.isArray(data) ? data : (data?.list || data?.records || [])
  } catch (e) {
    historyList.value = []
  }
}

const handleSend = async () => {
  if (!commandForm.value.target || !commandForm.value.content) {
    ElMessage.warning('请填写目标和内容')
    return
  }
  try {
    await sendCommand(commandForm.value)
    ElMessage.success('指令下发成功')
    commandForm.value.content = ''
    loadHistory()
  } catch (e: any) {
    ElMessage.error(e?.message || '下发失败')
  }
}

const handleBroadcast = async () => {
  if (!commandForm.value.content) { ElMessage.warning('请输入广播内容'); return }
  try {
    await broadcastCommand({ content: commandForm.value.content })
    ElMessage.success('广播成功')
    commandForm.value.content = ''
    loadHistory()
  } catch (e: any) {
    ElMessage.error(e?.message || '广播失败')
  }
}

const handleAlert = async () => {
  if (!commandForm.value.content) { ElMessage.warning('请输入告警内容'); return }
  try {
    await sendAlert({ level: 'warning', content: commandForm.value.content })
    ElMessage.warning('告警已发送')
    commandForm.value.content = ''
    loadHistory()
  } catch (e: any) {
    ElMessage.error(e?.message || '发送失败')
  }
}

const quickBroadcast = async (msg: string) => {
  try {
    await broadcastCommand({ content: msg })
    ElMessage.success('广播成功')
    loadHistory()
  } catch (e: any) {
    ElMessage.error(e?.message || '广播失败')
  }
}

onMounted(() => {
  connectWs()
  loadOnlineCount()
  loadHistory()
})

onUnmounted(() => {
  if (ws) ws.close()
})
</script>

<style scoped>
.command-page {
  display: flex; flex-direction: column; height: 100vh; padding: 16px 20px; box-sizing: border-box; overflow: hidden;
}
.page-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-shrink: 0;
}
.page-header h2 { margin: 0; color: #11616B; font-size: 20px; font-weight: 600; }
.ws-status { display: flex; align-items: center; }
.content-row {
  display: flex; gap: 16px; flex: 1; min-height: 0;
}
.left-panel { width: 380px; flex-shrink: 0; display: flex; flex-direction: column; gap: 12px; }
.right-panel { flex: 1; min-width: 0; display: flex; }
.panel-card { flex-shrink: 0; border-radius: 8px; }
.panel-card :deep(.el-card__header) { padding: 12px 16px; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); }
.history-card { flex: 1; display: flex; flex-direction: column; min-height: 0; border-radius: 8px; }
.history-card :deep(.el-card__body) { flex: 1; overflow-y: auto; padding: 12px; }
.history-list { display: flex; flex-direction: column; gap: 10px; }
.history-item {
  border: 1px solid #EBEEF5; border-radius: 8px; padding: 12px 14px; background: #fff;
  transition: all 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.history-item:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); transform: translateY(-1px); }
.history-item.type-broadcast { border-left: 4px solid #67C23A; background: #f0f9eb; }
.history-item.type-alert { border-left: 4px solid #E6A23C; background: #fdf6ec; }
.history-item.type-command { border-left: 4px solid #409EFF; }
.history-header { display: flex; align-items: center; margin-bottom: 8px; }
.history-time { margin-left: auto; font-size: 12px; color: #909399; }
.history-content { font-size: 14px; color: #303133; margin-bottom: 6px; line-height: 1.5; }
.history-operator { font-size: 12px; color: #909399; display: flex; }
.quick-btns { display: flex; flex-wrap: wrap; gap: 8px; }
.quick-btns .el-button { border-radius: 16px; }
</style>
