<template>
  <div class="dashboard-wrap">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon" style="background: #409EFF;">箱</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.containerTotal || 0 }}</div>
          <div class="stat-label">集装箱总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #67C23A;">卡</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.truckTotal || 0 }}</div>
          <div class="stat-label">集卡总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #E6A23C;">船</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.vesselWorking || 0 }}</div>
          <div class="stat-label">作业中船舶</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #F56C6C;">桥</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.craneWorking || 0 }}</div>
          <div class="stat-label">作业中岸桥</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #909399;">AI</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.aiTotal || 0 }}</div>
          <div class="stat-label">AI检测次数</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-title">集装箱状态分布</div>
        <div ref="containerChartRef" class="chart-container"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">集卡状态分布</div>
        <div ref="truckChartRef" class="chart-container"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">设备OEE TOP10</div>
        <div ref="oeeChartRef" class="chart-container"></div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-title">近7天吞吐量趋势</div>
        <div ref="throughputChartRef" class="chart-container"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">闸口通行效率</div>
        <div ref="gateChartRef" class="chart-container"></div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card full">
        <div class="chart-title">船舶在泊时间 TOP10</div>
        <div ref="vesselChartRef" class="chart-container"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  getDashboardStats, getContainerStatus, getTruckStatus,
  getEquipmentOee, getThroughputTrend, getGateEfficiency, getVesselTop
} from '@/api/dashboard'

const stats = ref<Record<string, number>>({})

const containerChartRef = ref<HTMLElement>()
const truckChartRef = ref<HTMLElement>()
const oeeChartRef = ref<HTMLElement>()
const throughputChartRef = ref<HTMLElement>()
const gateChartRef = ref<HTMLElement>()
const vesselChartRef = ref<HTMLElement>()

let containerChart: echarts.ECharts | null = null
let truckChart: echarts.ECharts | null = null
let oeeChart: echarts.ECharts | null = null
let throughputChart: echarts.ECharts | null = null
let gateChart: echarts.ECharts | null = null
let vesselChart: echarts.ECharts | null = null

const initCharts = () => {
  if (containerChartRef.value) containerChart = echarts.init(containerChartRef.value)
  if (truckChartRef.value) truckChart = echarts.init(truckChartRef.value)
  if (oeeChartRef.value) oeeChart = echarts.init(oeeChartRef.value)
  if (throughputChartRef.value) throughputChart = echarts.init(throughputChartRef.value)
  if (gateChartRef.value) gateChart = echarts.init(gateChartRef.value)
  if (vesselChartRef.value) vesselChart = echarts.init(vesselChartRef.value)
}

const loadStats = async () => {
  try {
    const res: any = await getDashboardStats()
    stats.value = res?.data || res || {}
  } catch (e) {
    stats.value = {}
  }
}

const loadContainerStatus = async () => {
  try {
    const res: any = await getContainerStatus()
    const data = res?.data || res
    const list = Array.isArray(data) ? data : []
    if (containerChart) {
      containerChart.setOption({
        tooltip: { trigger: 'item' },
        legend: { bottom: 0, type: 'scroll' },
        series: [{
          type: 'pie', radius: ['40%', '70%'], avoidLabelOverlap: false,
          label: { show: false }, emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
          data: list.length ? list : [
            { value: 0, name: '正常' }, { value: 0, name: '作业中' }, { value: 0, name: '破损' }, { value: 0, name: '已装船' }
          ]
        }]
      })
    }
  } catch (e) {
    if (containerChart) containerChart.setOption({ series: [{ data: [] }] })
  }
}

const loadTruckStatus = async () => {
  try {
    const res: any = await getTruckStatus()
    const data = res?.data || res
    const list = Array.isArray(data) ? data : []
    if (truckChart) {
      truckChart.setOption({
        tooltip: { trigger: 'item' },
        legend: { bottom: 0, type: 'scroll' },
        series: [{
          type: 'pie', radius: ['40%', '70%'],
          label: { show: false },
          data: list.length ? list : [
            { value: 0, name: '空闲' }, { value: 0, name: '运输中' }, { value: 0, name: '装卸中' }, { value: 0, name: '维修中' }
          ]
        }]
      })
    }
  } catch (e) {
    if (truckChart) truckChart.setOption({ series: [{ data: [] }] })
  }
}

const loadEquipmentOee = async () => {
  try {
    const res: any = await getEquipmentOee()
    const data = res?.data || res
    const list = Array.isArray(data) ? data : []
    const names = list.map((item: any) => item.name || item.equipmentNo || '').slice(0, 10)
    const values = list.map((item: any) => item.oee || item.value || 0).slice(0, 10)
    if (oeeChart) {
      oeeChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: names, axisLabel: { rotate: 30, fontSize: 10 } },
        yAxis: { type: 'value', max: 100 },
        series: [{ type: 'bar', data: values, itemStyle: { color: '#409EFF' } }]
      })
    }
  } catch (e) {
    if (oeeChart) oeeChart.setOption({ xAxis: { data: [] }, series: [{ data: [] }] })
  }
}

const loadThroughputTrend = async () => {
  try {
    const res: any = await getThroughputTrend()
    const data = res?.data || res
    const list = Array.isArray(data) ? data : []
    const dates = list.map((item: any) => item.date || item.day || '')
    const values = list.map((item: any) => item.count || item.value || 0)
    if (throughputChart) {
      throughputChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', boundaryGap: false, data: dates },
        yAxis: { type: 'value' },
        series: [{ type: 'line', data: values, smooth: true, areaStyle: {}, itemStyle: { color: '#67C23A' } }]
      })
    }
  } catch (e) {
    if (throughputChart) throughputChart.setOption({ xAxis: { data: [] }, series: [{ data: [] }] })
  }
}

const loadGateEfficiency = async () => {
  try {
    const res: any = await getGateEfficiency()
    const data = res?.data || res
    const list = Array.isArray(data) ? data : []
    const names = list.map((item: any) => item.gate || item.gateNo || item.name || '')
    const values = list.map((item: any) => {
      if (item.efficiency !== undefined) return item.efficiency
      if (item.pass !== undefined && item.plan) return Math.round(item.pass / item.plan * 100)
      return item.value || item.pass || 0
    })
    if (gateChart) {
      gateChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: names },
        yAxis: { type: 'value', max: 100 },
        series: [{ type: 'bar', data: values, itemStyle: { color: '#E6A23C' } }]
      })
    }
  } catch (e) {
    if (gateChart) gateChart.setOption({ xAxis: { data: [] }, series: [{ data: [] }] })
  }
}

const loadVesselTop = async () => {
  try {
    const res: any = await getVesselTop()
    const data = res?.data || res
    // 确保data是数组，避免data is not iterable错误
    const list = Array.isArray(data) ? data : []
    const names = list.map((item: any) => item.vesselName || item.name || '').slice(0, 10)
    const values = list.map((item: any) => item.total || item.totalContainer || item.duration || item.value || 0).slice(0, 10)
    if (vesselChart) {
      vesselChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value' },
        yAxis: { type: 'category', data: names.reverse(), axisLabel: { fontSize: 11 } },
        series: [{ type: 'bar', data: values.reverse(), itemStyle: { color: '#909399' } }]
      })
    }
  } catch (e) {
    if (vesselChart) vesselChart.setOption({ yAxis: { data: [] }, series: [{ data: [] }] })
  }
}

const handleResize = () => {
  containerChart?.resize()
  truckChart?.resize()
  oeeChart?.resize()
  throughputChart?.resize()
  gateChart?.resize()
  vesselChart?.resize()
}

onMounted(async () => {
  await nextTick()
  initCharts()
  loadStats()
  loadContainerStatus()
  loadTruckStatus()
  loadEquipmentOee()
  loadThroughputTrend()
  loadGateEfficiency()
  loadVesselTop()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  containerChart?.dispose()
  truckChart?.dispose()
  oeeChart?.dispose()
  throughputChart?.dispose()
  gateChart?.dispose()
  vesselChart?.dispose()
})
</script>

<style scoped>
.dashboard-wrap {
  width: 100%; height: 100%; padding: 16px 20px; box-sizing: border-box;
  overflow-y: auto; background-color: transparent;
}
.stats-row {
  display: flex; gap: 16px; margin-bottom: 16px;
}
.stat-card {
  flex: 1; background: #fff; border-radius: 8px; padding: 16px;
  display: flex; align-items: center; gap: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stat-icon {
  width: 48px; height: 48px; border-radius: 8px; color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; font-weight: bold;
}
.stat-value { font-size: 26px; font-weight: bold; color: #303133; }
.stat-label { font-size: 13px; color: #909399; margin-top: 2px; }
.charts-row {
  display: flex; gap: 16px; margin-bottom: 16px;
}
.chart-card {
  flex: 1; background: #fff; border-radius: 8px; padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.chart-card.large { flex: 2; }
.chart-card.full { flex: 1; }
.chart-title {
  font-size: 15px; font-weight: bold; color: #303133; margin-bottom: 8px;
}
.chart-container {
  width: 100%; height: 260px;
}
</style>
