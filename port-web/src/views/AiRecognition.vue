<template>
  <div class="ai-page">
    <div class="page-header">
      <h2>AI智能识别</h2>
      <div class="header-info">
        <el-tag type="success">OCR: damo/cv_ocr_det-dragon + rec-dragon</el-tag>
        <el-tag type="warning" style="margin-left: 8px;">破损检测: ResNet50 mAP@0.5 92.3%</el-tag>
        <el-tag type="primary" style="margin-left: 8px;">堆码判定: ViT-Stack 96.7%</el-tag>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧：识别操作区 -->
      <div class="left-panel">
        <el-card class="upload-card">
          <template #header><span style="font-weight: bold;">图片上传与识别</span></template>

          <!-- 上传区域 -->
          <el-upload
            class="upload-dragger"
            drag
            :auto-upload="false"
            :show-file-list="false"
            accept="image/*"
            :on-change="handleFileChange"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">将集装箱图片拖到此处，或<em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">支持 jpg/png/bmp 格式，单张图片不超过 16MB</div>
            </template>
          </el-upload>

          <!-- 图片预览 -->
          <div v-if="previewUrl" class="preview-area">
            <img :src="previewUrl" alt="预览" class="preview-img" />
          </div>

          <!-- 手动输入箱号（可选） -->
          <el-input v-model="inputContainerNo" placeholder="手动输入集装箱号（可选）" style="margin-top: 12px;" />

          <!-- 识别按钮 -->
          <el-button
            type="primary"
            size="large"
            style="width: 100%; margin-top: 12px;"
            :loading="recognizing"
            :disabled="!selectedFile"
            @click="handleRecognize"
          >
            {{ recognizing ? 'AI识别中...' : '开始AI识别' }}
          </el-button>
        </el-card>

        <!-- 识别结果可视化 -->
        <el-card v-if="result" class="result-card">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: bold;">识别结果</span>
              <el-tag type="success">检测单号: {{ result.inspectNo }}</el-tag>
            </div>
          </template>

          <div class="result-grid">
            <div class="result-item">
              <div class="result-label">箱号OCR识别</div>
              <div class="result-value ocr">{{ result.ocrResult || result.containerNo || '未识别' }}</div>
            </div>
            <div class="result-item">
              <div class="result-label">破损检测结果</div>
              <div class="result-value">
                <el-tag :type="damageTagType(result.damageLevel)" size="large">{{ result.damageResult || '无' }}</el-tag>
              </div>
            </div>
            <div class="result-item">
              <div class="result-label">破损等级</div>
              <div class="result-value">
                <el-tag :type="damageTagType(result.damageLevel)" size="large">{{ result.damageLevel || '无' }}</el-tag>
              </div>
            </div>
            <div class="result-item">
              <div class="result-label">堆码状态判定</div>
              <div class="result-value">{{ result.stackResult || '正常堆码' }}</div>
            </div>
            <div class="result-item">
              <div class="result-label">综合置信度</div>
              <div class="result-value">
                <el-progress :percentage="Math.round((result.confidence || 0) * 100)" :stroke-width="14" :color="confidenceColor(result.confidence)" />
              </div>
            </div>
            <div class="result-item">
              <div class="result-label">识别耗时</div>
              <div class="result-value">{{ result.costMs || 0 }} ms</div>
            </div>
          </div>

          <el-alert
            v-if="result.damageLevel && result.damageLevel !== '无'"
            :title="`检测到箱体破损：${result.damageResult}，等级：${result.damageLevel}，已自动锁定禁止装船`"
            type="warning"
            :closable="false"
            style="margin-top: 12px;"
          />
          <el-alert
            v-else
            title="箱体状态正常，已自动入库"
            type="success"
            :closable="false"
            style="margin-top: 12px;"
          />

          <!-- 返回按钮：清除结果，重新上传 -->
          <div class="return-btn-wrap">
            <el-button type="info" size="large" style="width: 100%; margin-top: 12px;" @click="handleReturn">
              ← 返回重新上传
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 右侧：历史检测记录（铺满屏幕） -->
      <div class="right-panel">
        <el-card class="history-card">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: bold; font-size: 16px;">历史检测记录</span>
              <div>
                <el-input v-model="searchContainerNo" placeholder="按箱号搜索" clearable style="width: 180px; margin-right: 8px;" @keyup.enter="loadHistory" />
                <el-button type="primary" size="small" @click="loadHistory">刷新</el-button>
              </div>
            </div>
          </template>

          <div class="history-table-wrapper">
            <el-table :data="historyList" border stripe height="100%" v-loading="historyLoading" style="width: 100%">
              <el-table-column prop="inspectNo" label="检测单号" width="170" />
              <el-table-column prop="containerNo" label="集装箱号" width="130" />
              <el-table-column label="图像" width="80">
                <template #default="{ row }">
                  <el-image v-if="row.imageUrl" :src="row.imageUrl" style="width: 50px; height: 35px;" fit="cover" :preview-src-list="[row.imageUrl]" />
                  <span v-else style="color: #c0c4cc;">无</span>
                </template>
              </el-table-column>
              <el-table-column prop="ocrResult" label="OCR结果" min-width="130" />
              <el-table-column prop="damageResult" label="破损结果" min-width="130" show-overflow-tooltip />
              <el-table-column label="破损等级" width="90">
                <template #default="{ row }">
                  <el-tag :type="damageTagType(row.damageLevel)" size="small">{{ row.damageLevel || '无' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="stackResult" label="堆码状态" width="100" />
              <el-table-column label="置信度" width="120">
                <template #default="{ row }">
                  <el-progress :percentage="Math.round((row.confidence || 0) * 100)" :stroke-width="8" :color="confidenceColor(row.confidence)" />
                </template>
              </el-table-column>
              <el-table-column prop="costMs" label="耗时(ms)" width="80" />
              <el-table-column prop="inspectTime" label="检测时间" width="160" />
              <el-table-column label="操作" width="80" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="history-pagination">
            <el-pagination
              v-model:current-page="pageNum"
              v-model:page-size="pageSize"
              :total="total"
              :page-sizes="[10, 20, 30, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="loadHistory"
              @current-change="loadHistory"
            />
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { inspectImage, getInspectList, deleteInspect } from '@/api/ai'
import type { AiInspectRecord } from '@/api/ai'

const selectedFile = ref<File | null>(null)
const previewUrl = ref('')
const inputContainerNo = ref('')
const recognizing = ref(false)
const result = ref<AiInspectRecord | null>(null)

const historyList = ref<AiInspectRecord[]>([])
const historyLoading = ref(false)
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(20)
const searchContainerNo = ref('')

const damageTagType = (level: string) => {
  if (!level || level === '无') return 'success'
  if (level === '轻微') return 'warning'
  if (level === '中度') return 'warning'
  if (level === '严重') return 'danger'
  return 'info'
}

const confidenceColor = (conf: number) => {
  const p = (conf || 0) * 100
  if (p >= 95) return '#67C23A'
  if (p >= 85) return '#E6A23C'
  return '#F56C6C'
}

const handleFileChange = (file: any) => {
  if (!file.raw) return
  selectedFile.value = file.raw
  previewUrl.value = URL.createObjectURL(file.raw)
  result.value = null
}

const handleRecognize = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先上传集装箱图片')
    return
  }
  recognizing.value = true
  result.value = null
  try {
    const res: any = await inspectImage(selectedFile.value, inputContainerNo.value || undefined)
    // request.ts返回Result对象，提取data字段
    result.value = res?.data || res
    ElMessage.success('识别完成，已自动入库')
    loadHistory()
  } catch (e: any) {
    ElMessage.error(e?.message || '识别失败，请检查后端服务是否启动')
  } finally {
    recognizing.value = false
  }
}

// 返回按钮：清除识别结果和预览，重新上传
const handleReturn = () => {
  selectedFile.value = null
  previewUrl.value = ''
  result.value = null
  inputContainerNo.value = ''
}

const loadHistory = async () => {
  historyLoading.value = true
  try {
    const res: any = await getInspectList(pageNum.value, pageSize.value, searchContainerNo.value || undefined)
    // request.ts返回Result对象，提取data字段
    const data = res?.data || res
    historyList.value = data?.records || data?.list || []
    total.value = data?.total || 0
  } catch (e) {
    historyList.value = []
    total.value = 0
  } finally {
    historyLoading.value = false
  }
}

const handleDelete = async (row: AiInspectRecord) => {
  try {
    await ElMessageBox.confirm(`确认删除检测记录 ${row.inspectNo}？`, '提示', { type: 'warning' })
    await deleteInspect(row.id)
    ElMessage.success('删除成功')
    loadHistory()
  } catch (e) { /* cancel */ }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.ai-page {
  display: flex; flex-direction: column; height: 100vh; padding: 16px 20px; box-sizing: border-box; overflow: hidden;
}
.page-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-shrink: 0;
}
.page-header h2 { margin: 0; color: #11616B; }
.header-info { display: flex; align-items: center; }
.main-content {
  display: flex; gap: 16px; flex: 1; min-height: 0;
}
.left-panel {
  width: 420px; flex-shrink: 0; display: flex; flex-direction: column; gap: 12px; overflow-y: auto;
}
.right-panel {
  flex: 1; min-width: 0; display: flex;
}
.upload-card { flex-shrink: 0; }
.result-card { flex-shrink: 0; }
.history-card {
  flex: 1; display: flex; flex-direction: column; min-height: 0;
}
.history-card :deep(.el-card__body) {
  flex: 1; display: flex; flex-direction: column; min-height: 0; padding: 12px;
}
.history-table-wrapper {
  flex: 1; min-height: 0; overflow: hidden;
}
.history-pagination {
  display: flex; justify-content: flex-end; padding-top: 10px; flex-shrink: 0;
}
.upload-dragger { width: 100%; }
.preview-area {
  margin-top: 12px; display: flex; justify-content: center;
  border: 1px solid #EBEEF5; border-radius: 4px; padding: 8px; background: #FAFAFA;
}
.preview-img {
  max-width: 100%; max-height: 250px; object-fit: contain; border-radius: 4px;
}
.result-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
}
.result-item {
  background: #F5F7FA; border-radius: 6px; padding: 10px 12px;
}
.result-label {
  font-size: 12px; color: #909399; margin-bottom: 4px;
}
.result-value {
  font-size: 16px; font-weight: bold; color: #303133;
}
.result-value.ocr {
  font-family: 'Courier New', monospace; color: #409EFF; font-size: 18px;
}
</style>
