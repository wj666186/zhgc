<template>
    <main class="ai-page">
        <section class="ai-header">
            <div>
                <h1>AI智能识别</h1>
                <p>集装箱外观破损检测</p>
            </div>
            <el-tag type="success" effect="plain">演示级</el-tag>
        </section>

        <section class="ai-workbench">
            <!-- 左侧预览面板 -->
            <div class="preview-panel">
                <div class="container-visual">
                    <div class="container-roof"></div>
                    <div class="container-body">
                        <span v-for="line in 8" :key="line"></span>
                    </div>
                    <div class="damage-mark"></div>
                </div>
                <div class="preview-info">
                    <span class="left">箱号：{{ form.containerNo }}</span>
                    <span class="right">{{ form.imageName }}</span>
                </div>
            </div>

            <!-- 右侧操作面板 -->
            <div class="operate-panel">
                <!-- 箱号下拉选择（动态从接口加载） -->
                <div class="form-item">
                    <label>箱号</label>
                    <el-select v-model="form.containerNo" placeholder="请选择箱号">
                        <el-option
                            v-for="boxNo in containerOptions"
                            :key="boxNo"
                            :label="boxNo"
                            :value="boxNo"
                        ></el-option>
                    </el-select>
                </div>

                <!-- 识别图像 三个按钮 调用封装好的changeImage方法 -->
                <div class="form-item">
                    <label>识别图像</label>
                    <div class="btn-group">
                        <el-button
                            :type="imgType === 'front' ? 'primary' : ''"
                            @click="changeImage('front')"
                        >正面</el-button>
                        <el-button
                            :type="imgType === 'side' ? 'primary' : ''"
                            @click="changeImage('side')"
                        >侧面</el-button>
                        <el-button
                            :type="imgType === 'top' ? 'primary' : ''"
                            @click="changeImage('top')"
                        >顶部</el-button>
                    </div>
                </div>

                <!-- AI识别大按钮 -->
                <el-button type="primary" class="ai-btn" @click="handleRecognize">AI识别</el-button>

                <!-- 接口与状态信息 -->
                <div class="info-row">
                    <label>接口</label>
                    <span>/api/ai/recognize</span>
                </div>
                <div class="info-row">
                    <label>状态</label>
                    <span>{{ statusText }}</span>
                </div>

                <!-- 识别结果卡片 -->
                <div class="result-card" v-if="result.inspectNo">
                    <h3>识别检测结果</h3>
                    <el-descriptions border column="1">
                        <el-descriptions-item label="检测单号">{{ result.inspectNo }}</el-descriptions-item>
                        <el-descriptions-item label="集装箱号">{{ result.containerNo }}</el-descriptions-item>
                        <el-descriptions-item label="破损描述">{{ result.damageResult }}</el-descriptions-item>
                        <el-descriptions-item label="破损等级">{{ result.damageLevel }}</el-descriptions-item>
                        <el-descriptions-item label="置信度">{{ result.confidence }}</el-descriptions-item>
                        <el-descriptions-item label="耗时(ms)">{{ result.costMs }}</el-descriptions-item>
                    </el-descriptions>
                </div>
            </div>
        </section>
    </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { recognizeContainer } from '../api/ai'
import { getContainerList } from '../api/container'

// 下拉箱号数据源
const containerOptions = ref<string[]>([])

// 表单绑定数据
const form = ref({
    containerNo: '',
    imageName: ''
})

// 识别返回结果
const result = ref({
    inspectNo: '',
    containerNo: '',
    damageResult: '',
    damageLevel: '',
    confidence: 0,
    costMs: 0
})

// 识别状态计算属性
const statusText = computed(() => {
    return result.value.inspectNo ? '识别完成' : '待识别'
})

// 页面挂载拉取集装箱列表，填充下拉框
onMounted(async () => {
    // 必须加()执行函数，分页接口传入空对象作为默认参数
    const res = await getContainerList({})
    if (res.code !== 200) {
        return
    }
    // 提取所有箱号
    containerOptions.value = res.data.records.map(item => item.containerNo)
    // 默认选中第一条
    if (containerOptions.value.length > 0) {
        form.value.containerNo = containerOptions.value[0]
    }
})

// AI识别请求
const handleRecognize = async () => {
    const res = await recognizeContainer(form.value)
    if (res.code === 200) {
        result.value = res.data
    }
}

// 切换图片视角，消除未使用变量警告
const imgType = ref('front')
const changeImage = (type: string) => {
    imgType.value = type
    const map: Record<string, string> = {
        front: 'front-camera-01.jpg',
        side: 'side-camera-01.jpg',
        top: 'top-camera-01.jpg'
    }
    form.value.imageName = map[type]
}
</script>

<style scoped>
.ai-page {
    padding: 20px;
}
.ai-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}
.ai-workbench {
    display: flex;
    gap: 30px;
}
.preview-panel {
    flex: 1;
    border: 1px solid #e4e7ed;
    padding: 20px;
    border-radius: 6px;
}
.container-visual {
    width: 100%;
    height: 320px;
    border: 2px solid #366;
    margin: 0 auto 20px;
    position: relative;
    background-color: #366;
}
.container-roof {
    height: 50px;
    width: 90%;
    margin-left: -5%;
    position: relative;
    top: -10px;
    left: 5%;
    background: #285959;
    transform: skewX(-15deg);
}
.container-body {
    height: calc(100% - 50px);
    display: flex;
    flex-direction: column;
    justify-content: space-around;
}
.container-body span {
    display: block;
    width: 100%;
    height: 1px;
    background: #224444;
}
.damage-mark {
    position: absolute;
    top: 120px;
    left: 55%;
    width: 70px;
    height: 70px;
    border: 2px solid #f56c6c;
    background: rgba(245, 108, 108, 0.2);
}
.preview-info {
    margin-top: 12px;
    display: flex;
    justify-content: space-between;
}
.operate-panel {
    width: 340px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}
.form-item {
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.form-item label {
    font-size: 14px;
    color: #606266;
}
.btn-group {
    display: flex;
    gap: 8px;
}
.ai-btn {
    width: 100%;
    height: 44px;
    font-size: 16px;
}
.info-row {
    display: flex;
    justify-content: space-between;
    font-size: 14px;
}
.info-row label {
    color: #606266;
}
.result-card {
    margin-top: 10px;
    padding: 16px;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
}
.result-card h3 {
    margin-bottom: 12px;
}
</style>