<template>
    <div class="twin-wrap">
        <div class="page-header">
            <h2>数字孪生港口时空统一视图</h2>
            <div class="header-right">
                <el-button
                    :type="dragEnable ? 'danger' : 'primary'"
                    @click="toggleDragMode"
                >
                    {{ dragEnable ? '关闭装卸拖拽模式' : '开启装卸拖拽模式' }}
                </el-button>
                <span class="tip-text" v-if="dragEnable">✅ 按住集装箱任意位置拖拽完成装船/卸船</span>
                <span class="tip-text" v-else>🔒 场景查看模式，箱子固定不可移动</span>
            </div>
            <div class="status-desc">
                <el-tag color="#27ae60">绿色：已核验待装船</el-tag>
                <el-tag color="#f39c12">橙色：破损待处置</el-tag>
                <el-tag color="#e74c3c">红色：堆码异常超限</el-tag>
                <el-tag color="#0088cc">蓝色：船上已装船</el-tag>
            </div>
        </div>
        <div ref="sceneContainer" class="three-canvas"></div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, getCurrentInstance } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { TextureLoader, Sprite, SpriteMaterial, CanvasTexture } from 'three'
import { ElButton, ElTag } from 'element-plus'
import { initWebSocket } from '../utils/websocket'
import containerSideImg from '../assets/2.png'

const { appContext } = getCurrentInstance()!
const $api = appContext.config.globalProperties.$api

type ContainerState = 'normal' | 'damage' | 'tilt' | 'ship'
interface ContainerItem {
    id: number
    slotCode: string
    containerNo: string
    cargoType: string
    destPort: string
    weight: number
    rawStatus: number
    state: ContainerState
    areaNo: number | null
    loadStatus: 0 | 1
    saveX: number
    saveZ: number
}

const sceneContainer = ref<HTMLDivElement | null>(null)
const dragEnable = ref<boolean>(false)

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let controls: OrbitControls
let animationId = 0

const raycaster = new THREE.Raycaster()
const mouse = new THREE.Vector2()
let selectedContainer: THREE.Group | null = null

const containerMap = new Map<string, THREE.Group>()
const colorMap: Record<ContainerState, THREE.Color> = {
    normal: new THREE.Color(0x27ae60),
    damage: new THREE.Color(0xf39c12),
    tilt: new THREE.Color(0xe74c3c),
    ship: new THREE.Color(0x0088cc)
}

let containerModel: THREE.Group | null = null
let sideTexture: THREE.Texture | null = null
let towerCrane: THREE.Group | null = null
let shipGroup: THREE.Group | null = null
let waterMesh: THREE.Mesh | null = null
let trucks: THREE.Group[] = []
let rtgCranes: THREE.Group[] = []

// 全局数据源
let containerListData: ContainerItem[] = []
let pollTimer: number | null = null
let clock = new THREE.Clock()

const toggleDragMode = () => {
    dragEnable.value = !dragEnable.value
    selectedContainer = null
    controls.enabled = !dragEnable.value
}

const initTexture = () => {
    const loader = new TextureLoader()
    sideTexture = loader.load(containerSideImg)
    sideTexture.wrapS = THREE.RepeatWrapping
    sideTexture.wrapT = THREE.RepeatWrapping
    sideTexture.repeat.set(1, 1)
}

function createInfoSprite(info: string): Sprite {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')!
    canvas.width = 320
    canvas.height = 180
    ctx.font = "bold 15px Microsoft YaHei"
    ctx.fillStyle = "#000000"
    ctx.textAlign = "center"
    const textLines = info.split('\n')
    textLines.forEach((line, index) => {
        ctx.fillText(line, canvas.width / 2, 26 + index * 28)
    })
    ctx.fillStyle = '#ff3333'
    ctx.font = '13px Microsoft YaHei'
    ctx.fillText('🔴 按住箱体拖拽装卸', canvas.width / 2, 170)
    const canvasTex = new CanvasTexture(canvas)
    const spriteMat = new SpriteMaterial({ map: canvasTex, transparent: true })
    const sprite = new Sprite(spriteMat)
    sprite.scale.set(14, 8, 1)
    return sprite
}

const getContainerState = (rawStatus: number, loadStatus: 0 | 1): ContainerState => {
    if (loadStatus === 1) return 'ship'
    switch (rawStatus) {
        case 0: case 1: return 'normal'
        case 2: return 'damage'
        case 3: return 'tilt'
        default: return 'normal'
    }
}

const getStatusChinese = (num: number): string => {
    switch (num) {
        case 0: return '待分配'
        case 1: return '已分配堆场'
        case 2: return '破损锁定'
        case 3: return '堆码异常超限'
        default: return '未知状态'
    }
}

// ========== 岸桥（优化版） ==========
const createTowerCrane = () => {
    const group = new THREE.Group()
    // 塔身
    const pillarGeo = new THREE.BoxGeometry(3, 48, 3)
    const pillarMat = new THREE.MeshStandardMaterial({ color: 0xe74c3c, roughness: 0.6, metalness: 0.3 })
    const pillar = new THREE.Mesh(pillarGeo, pillarMat)
    pillar.position.y = 24
    pillar.castShadow = true
    group.add(pillar)
    // 塔身桁架装饰
    for (let i = 0; i < 8; i++) {
        const beamGeo = new THREE.BoxGeometry(3.5, 0.3, 3.5)
        const beamMat = new THREE.MeshStandardMaterial({ color: 0xc0392b })
        const beam = new THREE.Mesh(beamGeo, beamMat)
        beam.position.y = 3 + i * 5.5
        group.add(beam)
    }
    // 起重臂
    const armGeo = new THREE.BoxGeometry(60, 2, 2.5)
    const armMat = new THREE.MeshStandardMaterial({ color: 0xe74c3c, roughness: 0.5, metalness: 0.4 })
    const arm = new THREE.Mesh(armGeo, armMat)
    arm.position.set(30, 44, 0)
    arm.castShadow = true
    group.add(arm)
    // 平衡臂
    const counterArmGeo = new THREE.BoxGeometry(20, 2, 2.5)
    const counterArm = new THREE.Mesh(counterArmGeo, armMat)
    counterArm.position.set(-10, 44, 0)
    counterArm.castShadow = true
    group.add(counterArm)
    // 配重块
    const counterGeo = new THREE.BoxGeometry(6, 5, 4)
    const counterMat = new THREE.MeshStandardMaterial({ color: 0x34495e, roughness: 0.8 })
    const counter = new THREE.Mesh(counterGeo, counterMat)
    counter.position.set(-16, 42, 0)
    group.add(counter)
    // 操作室
    const cabGeo = new THREE.BoxGeometry(5, 4, 4)
    const cabMat = new THREE.MeshStandardMaterial({ color: 0x2c3e50, roughness: 0.5 })
    const cab = new THREE.Mesh(cabGeo, cabMat)
    cab.position.set(2, 41, 0)
    group.add(cab)
    // 吊钩小车
    const trolleyGeo = new THREE.BoxGeometry(4, 2, 3)
    const trolleyMat = new THREE.MeshStandardMaterial({ color: 0xf1c40f, roughness: 0.4, metalness: 0.5 })
    const trolley = new THREE.Mesh(trolleyGeo, trolleyMat)
    trolley.position.set(35, 42, 0)
    trolley.name = 'trolley'
    group.add(trolley)
    // 吊绳
    const ropeGeo = new THREE.CylinderGeometry(0.1, 0.1, 8, 8)
    const ropeMat = new THREE.MeshStandardMaterial({ color: 0x2c3e50 })
    const rope = new THREE.Mesh(ropeGeo, ropeMat)
    rope.position.set(35, 37, 0)
    rope.name = 'rope'
    group.add(rope)
    // 吊具
    const spreaderGeo = new THREE.BoxGeometry(7, 0.8, 3)
    const spreaderMat = new THREE.MeshStandardMaterial({ color: 0xf1c40f, metalness: 0.6 })
    const spreader = new THREE.Mesh(spreaderGeo, spreaderMat)
    spreader.position.set(35, 32, 0)
    spreader.name = 'spreader'
    group.add(spreader)

    group.position.set(140, 0, 0)
    scene.add(group)
    towerCrane = group
}

// ========== 船舶（优化版） ==========
const createShip = () => {
    const group = new THREE.Group()
    // 船身
    const hullGeo = new THREE.BoxGeometry(100, 14, 32)
    const hullMat = new THREE.MeshStandardMaterial({ color: 0x2c3e50, roughness: 0.7, metalness: 0.2 })
    const hull = new THREE.Mesh(hullGeo, hullMat)
    hull.position.y = -7
    hull.receiveShadow = true
    hull.castShadow = true
    group.add(hull)
    // 甲板
    const deckGeo = new THREE.BoxGeometry(96, 2, 30)
    const deckMat = new THREE.MeshStandardMaterial({ color: 0x7f8c8d, roughness: 0.8 })
    const deck = new THREE.Mesh(deckGeo, deckMat)
    deck.position.y = 1
    group.add(deck)
    // 船舱
    const cabinGeo = new THREE.BoxGeometry(20, 12, 26)
    const cabinMat = new THREE.MeshStandardMaterial({ color: 0x34495e, roughness: 0.6 })
    const cabin = new THREE.Mesh(cabinGeo, cabinMat)
    cabin.position.set(-30, 8, 0)
    cabin.castShadow = true
    group.add(cabin)
    // 驾驶台
    const bridgeGeo = new THREE.BoxGeometry(14, 6, 20)
    const bridgeMat = new THREE.MeshStandardMaterial({ color: 0xecf0f1, roughness: 0.5 })
    const bridge = new THREE.Mesh(bridgeGeo, bridgeMat)
    bridge.position.set(-30, 17, 0)
    group.add(bridge)
    // 烟囱
    const funnelGeo = new THREE.CylinderGeometry(2.5, 3, 8, 16)
    const funnelMat = new THREE.MeshStandardMaterial({ color: 0xe74c3c, roughness: 0.5 })
    const funnel = new THREE.Mesh(funnelGeo, funnelMat)
    funnel.position.set(-35, 22, 0)
    group.add(funnel)
    // 桅杆
    const mastGeo = new THREE.CylinderGeometry(0.3, 0.3, 15, 8)
    const mastMat = new THREE.MeshStandardMaterial({ color: 0x2c3e50 })
    const mast = new THREE.Mesh(mastGeo, mastMat)
    mast.position.set(-25, 25, 0)
    group.add(mast)
    // 船舷栏杆
    const railMat = new THREE.MeshStandardMaterial({ color: 0x95a5a6, metalness: 0.6 })
    for (let side = -1; side <= 1; side += 2) {
        const railGeo = new THREE.BoxGeometry(90, 1, 0.3)
        const rail = new THREE.Mesh(railGeo, railMat)
        rail.position.set(10, 3, side * 15)
        group.add(rail)
    }

    group.position.set(200, -12, 0)
    scene.add(group)
    shipGroup = group
}

// ========== 龙门吊 RTG ==========
const createRTG = (x: number, z: number, color: number = 0x27ae60): THREE.Group => {
    const group = new THREE.Group()
    const legMat = new THREE.MeshStandardMaterial({ color, roughness: 0.5, metalness: 0.4 })
    const beamMat = new THREE.MeshStandardMaterial({ color, roughness: 0.4, metalness: 0.5 })
    // 四根支腿
    const legGeo = new THREE.BoxGeometry(1.5, 18, 1.5)
    const positions = [[-8, 9, -5], [8, 9, -5], [-8, 9, 5], [8, 9, 5]]
    positions.forEach(pos => {
        const leg = new THREE.Mesh(legGeo, legMat)
        leg.position.set(pos[0], pos[1], pos[2])
        leg.castShadow = true
        group.add(leg)
    })
    // 主梁
    const beamGeo = new THREE.BoxGeometry(20, 2, 2)
    const beam = new THREE.Mesh(beamGeo, beamMat)
    beam.position.y = 18
    beam.castShadow = true
    group.add(beam)
    // 端梁
    const endBeamGeo = new THREE.BoxGeometry(2, 2, 14)
    const endBeam1 = new THREE.Mesh(endBeamGeo, beamMat)
    endBeam1.position.set(-9, 18, 0)
    group.add(endBeam1)
    const endBeam2 = new THREE.Mesh(endBeamGeo, beamMat)
    endBeam2.position.set(9, 18, 0)
    group.add(endBeam2)
    // 小车
    const trolleyGeo = new THREE.BoxGeometry(4, 1.5, 4)
    const trolleyMat = new THREE.MeshStandardMaterial({ color: 0xf1c40f, metalness: 0.5 })
    const trolley = new THREE.Mesh(trolleyGeo, trolleyMat)
    trolley.position.set(0, 19.5, 0)
    trolley.name = 'rtgTrolley'
    group.add(trolley)
    // 吊具
    const spreaderGeo = new THREE.BoxGeometry(7, 0.6, 3)
    const spreaderMat = new THREE.MeshStandardMaterial({ color: 0xf1c40f, metalness: 0.6 })
    const spreader = new THREE.Mesh(spreaderGeo, spreaderMat)
    spreader.position.set(0, 14, 0)
    spreader.name = 'rtgSpreader'
    group.add(spreader)
    // 轮胎
    const wheelGeo = new THREE.CylinderGeometry(1.2, 1.2, 0.8, 16)
    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.9 })
    const wheelPositions = [[-8, 1.2, -6], [8, 1.2, -6], [-8, 1.2, 6], [8, 1.2, 6]]
    wheelPositions.forEach(pos => {
        const wheel = new THREE.Mesh(wheelGeo, wheelMat)
        wheel.rotation.z = Math.PI / 2
        wheel.position.set(pos[0], pos[1], pos[2])
        group.add(wheel)
    })
    // 操作室
    const cabGeo = new THREE.BoxGeometry(3, 3, 3)
    const cabMat = new THREE.MeshStandardMaterial({ color: 0x3498db, roughness: 0.4 })
    const cab = new THREE.Mesh(cabGeo, cabMat)
    cab.position.set(-7, 12, 6)
    group.add(cab)

    group.position.set(x, 0, z)
    scene.add(group)
    return group
}

// ========== 集卡 Truck ==========
const createTruck = (x: number, z: number, color: number = 0xe67e22): THREE.Group => {
    const group = new THREE.Group()
    // 车头
    const cabGeo = new THREE.BoxGeometry(5, 3.5, 3)
    const cabMat = new THREE.MeshStandardMaterial({ color, roughness: 0.5, metalness: 0.3 })
    const cab = new THREE.Mesh(cabGeo, cabMat)
    cab.position.set(-5, 2.5, 0)
    cab.castShadow = true
    group.add(cab)
    // 驾驶室窗户
    const windowGeo = new THREE.BoxGeometry(0.1, 1.5, 2.2)
    const windowMat = new THREE.MeshStandardMaterial({ color: 0x87ceeb, roughness: 0.1, metalness: 0.8 })
    const window1 = new THREE.Mesh(windowGeo, windowMat)
    window1.position.set(-2.6, 3, 0)
    group.add(window1)
    // 货箱平板
    const flatGeo = new THREE.BoxGeometry(14, 0.8, 3.5)
    const flatMat = new THREE.MeshStandardMaterial({ color: 0x7f8c8d, roughness: 0.7, metalness: 0.4 })
    const flat = new THREE.Mesh(flatGeo, flatMat)
    flat.position.set(2, 1.8, 0)
    flat.castShadow = true
    group.add(flat)
    // 集装箱（放在平板上）
    const boxGeo = new THREE.BoxGeometry(12, 2.6, 2.8)
    const boxMat = new THREE.MeshStandardMaterial({ color: 0x3498db, roughness: 0.6, metalness: 0.2 })
    const box = new THREE.Mesh(boxGeo, boxMat)
    box.position.set(2, 3.5, 0)
    box.castShadow = true
    group.add(box)
    // 车轮
    const wheelGeo = new THREE.CylinderGeometry(1, 1, 0.6, 16)
    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.9 })
    const wheelPositions = [
        [-6, 1, -1.8], [-6, 1, 1.8],
        [-2, 1, -1.8], [-2, 1, 1.8],
        [5, 1, -1.8], [5, 1, 1.8]
    ]
    wheelPositions.forEach(pos => {
        const wheel = new THREE.Mesh(wheelGeo, wheelMat)
        wheel.rotation.z = Math.PI / 2
        wheel.position.set(pos[0], pos[1], pos[2])
        group.add(wheel)
    })
    // 排气管
    const pipeGeo = new THREE.CylinderGeometry(0.2, 0.2, 2, 8)
    const pipeMat = new THREE.MeshStandardMaterial({ color: 0x2c3e50, metalness: 0.7 })
    const pipe = new THREE.Mesh(pipeGeo, pipeMat)
    pipe.position.set(-7, 4, 1.2)
    group.add(pipe)

    group.position.set(x, 0, z)
    group.userData = { speed: 8 + Math.random() * 6, direction: 1, baseZ: z }
    scene.add(group)
    return group
}

// ========== 闸口 Gate ==========
const createGate = () => {
    const group = new THREE.Group()
    // 闸口立柱
    const pillarGeo = new THREE.BoxGeometry(2, 10, 2)
    const pillarMat = new THREE.MeshStandardMaterial({ color: 0x2c3e50, roughness: 0.6, metalness: 0.3 })
    const pillar1 = new THREE.Mesh(pillarGeo, pillarMat)
    pillar1.position.set(-8, 5, 0)
    pillar1.castShadow = true
    group.add(pillar1)
    const pillar2 = new THREE.Mesh(pillarGeo, pillarMat)
    pillar2.position.set(8, 5, 0)
    pillar2.castShadow = true
    group.add(pillar2)
    // 横梁
    const beamGeo = new THREE.BoxGeometry(20, 2.5, 2)
    const beamMat = new THREE.MeshStandardMaterial({ color: 0xe74c3c, roughness: 0.5, metalness: 0.3 })
    const beam = new THREE.Mesh(beamGeo, beamMat)
    beam.position.y = 11
    beam.castShadow = true
    group.add(beam)
    // 闸口招牌
    const signGeo = new THREE.BoxGeometry(14, 2, 0.3)
    const signMat = new THREE.MeshStandardMaterial({ color: 0xf1c40f, roughness: 0.4 })
    const sign = new THREE.Mesh(signGeo, signMat)
    sign.position.set(0, 11, 1.2)
    group.add(sign)
    // 道闸杆
    const barrierGeo = new THREE.BoxGeometry(14, 0.4, 0.4)
    const barrierMat = new THREE.MeshStandardMaterial({ color: 0xe74c3c, roughness: 0.4 })
    const barrier = new THREE.Mesh(barrierGeo, barrierMat)
    barrier.position.set(0, 4, 0)
    barrier.name = 'barrier'
    group.add(barrier)
    // 道闸条纹
    for (let i = -6; i <= 6; i += 3) {
        const stripeGeo = new THREE.BoxGeometry(1.5, 0.45, 0.45)
        const stripeMat = new THREE.MeshStandardMaterial({ color: 0xffffff })
        const stripe = new THREE.Mesh(stripeGeo, stripeMat)
        stripe.position.set(i, 4, 0)
        group.add(stripe)
    }
    // 岗亭
    const boothGeo = new THREE.BoxGeometry(5, 4, 4)
    const boothMat = new THREE.MeshStandardMaterial({ color: 0x3498db, roughness: 0.5 })
    const booth = new THREE.Mesh(boothGeo, boothMat)
    booth.position.set(-14, 2, 0)
    booth.castShadow = true
    group.add(booth)
    // 岗亭屋顶
    const roofGeo = new THREE.BoxGeometry(6, 0.8, 5)
    const roofMat = new THREE.MeshStandardMaterial({ color: 0x2c3e50 })
    const roof = new THREE.Mesh(roofGeo, roofMat)
    roof.position.set(-14, 4.4, 0)
    group.add(roof)

    group.position.set(-150, 0, 0)
    scene.add(group)
}

// ========== 堆场仓位 ==========
const createYardSlots = () => {
    const slotMat = new THREE.MeshStandardMaterial({ color: 0x4a5568, roughness: 0.9 })
    const borderMat = new THREE.MeshBasicMaterial({ color: 0x718096, transparent: true, opacity: 0.6 })
    // A区 (-120 ~ -60)
    // B区 (-60 ~ 60)
    // C区 (60 ~ 120)
    const areas = [
        { xStart: -115, label: 'A区', color: 0x27ae60 },
        { xStart: -55, label: 'B区', color: 0x3498db },
        { xStart: 5, label: 'C区', color: 0x9b59b6 }
    ]
    areas.forEach(area => {
        for (let row = 0; row < 3; row++) {
            for (let col = 0; col < 6; col++) {
                const x = area.xStart + col * 10
                const z = -60 + row * 30
                // 仓位底座
                const slotGeo = new THREE.BoxGeometry(8, 0.3, 12)
                const slot = new THREE.Mesh(slotGeo, slotMat)
                slot.position.set(x, 0.15, z)
                slot.receiveShadow = true
                scene.add(slot)
                // 仓位边框
                const borderGeo = new THREE.BoxGeometry(8.5, 0.1, 12.5)
                const border = new THREE.Mesh(borderGeo, borderMat)
                border.position.set(x, 0.35, z)
                scene.add(border)
            }
        }
        // 区域标识牌
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')!
        canvas.width = 128
        canvas.height = 64
        ctx.fillStyle = `#${area.color.toString(16).padStart(6, '0')}`
        ctx.fillRect(0, 0, 128, 64)
        ctx.fillStyle = '#fff'
        ctx.font = 'bold 36px Microsoft YaHei'
        ctx.textAlign = 'center'
        ctx.fillText(area.label, 64, 44)
        const tex = new CanvasTexture(canvas)
        const spriteMat = new SpriteMaterial({ map: tex, transparent: true })
        const sprite = new Sprite(spriteMat)
        sprite.position.set(area.xStart + 25, 8, -80)
        sprite.scale.set(12, 6, 1)
        scene.add(sprite)
    })
}

// ========== 仓库/办公楼 ==========
const createBuildings = () => {
    // 仓库1
    const warehouse1Geo = new THREE.BoxGeometry(30, 12, 20)
    const warehouseMat = new THREE.MeshStandardMaterial({ color: 0x95a5a6, roughness: 0.8 })
    const warehouse1 = new THREE.Mesh(warehouse1Geo, warehouseMat)
    warehouse1.position.set(-150, 6, 80)
    warehouse1.castShadow = true
    warehouse1.receiveShadow = true
    scene.add(warehouse1)
    // 仓库屋顶
    const roof1Geo = new THREE.BoxGeometry(32, 2, 22)
    const roofMat = new THREE.MeshStandardMaterial({ color: 0x7f8c8d, roughness: 0.7 })
    const roof1 = new THREE.Mesh(roof1Geo, roofMat)
    roof1.position.set(-150, 13, 80)
    scene.add(roof1)
    // 仓库门
    const door1Geo = new THREE.BoxGeometry(8, 7, 0.3)
    const doorMat = new THREE.MeshStandardMaterial({ color: 0x2c3e50, roughness: 0.6 })
    const door1 = new THREE.Mesh(door1Geo, doorMat)
    door1.position.set(-150, 3.5, 90.1)
    scene.add(door1)

    // 办公楼
    const officeGeo = new THREE.BoxGeometry(20, 20, 15)
    const officeMat = new THREE.MeshStandardMaterial({ color: 0xecf0f1, roughness: 0.5 })
    const office = new THREE.Mesh(officeGeo, officeMat)
    office.position.set(-150, 10, -80)
    office.castShadow = true
    scene.add(office)
    // 办公楼窗户
    const winMat = new THREE.MeshStandardMaterial({ color: 0x3498db, roughness: 0.1, metalness: 0.7 })
    for (let floor = 0; floor < 5; floor++) {
        for (let col = 0; col < 4; col++) {
            const winGeo = new THREE.BoxGeometry(3, 2.5, 0.2)
            const win = new THREE.Mesh(winGeo, winMat)
            win.position.set(-158 + col * 5, 3 + floor * 3.5, -72.4)
            scene.add(win)
        }
    }
    // 办公楼楼顶
    const officeRoofGeo = new THREE.BoxGeometry(22, 1.5, 17)
    const officeRoof = new THREE.Mesh(officeRoofGeo, roofMat)
    officeRoof.position.set(-150, 20.75, -80)
    scene.add(officeRoof)

    // 维修车间
    const workshopGeo = new THREE.BoxGeometry(25, 8, 18)
    const workshopMat = new THREE.MeshStandardMaterial({ color: 0xe67e22, roughness: 0.7 })
    const workshop = new THREE.Mesh(workshopGeo, workshopMat)
    workshop.position.set(150, 4, 80)
    workshop.castShadow = true
    scene.add(workshop)
}

// ========== 灯塔 ==========
const createLighthouse = () => {
    const group = new THREE.Group()
    // 塔身
    const towerGeo = new THREE.CylinderGeometry(1.5, 2.5, 25, 16)
    const towerMat = new THREE.MeshStandardMaterial({ color: 0xecf0f1, roughness: 0.6 })
    const tower = new THREE.Mesh(towerGeo, towerMat)
    tower.position.y = 12.5
    tower.castShadow = true
    group.add(tower)
    // 红色条纹
    for (let i = 0; i < 4; i++) {
        const stripeGeo = new THREE.CylinderGeometry(1.6 + i * 0.1, 1.8 + i * 0.1, 2, 16)
        const stripeMat = new THREE.MeshStandardMaterial({ color: 0xe74c3c })
        const stripe = new THREE.Mesh(stripeGeo, stripeMat)
        stripe.position.y = 5 + i * 5
        group.add(stripe)
    }
    // 灯室
    const lampGeo = new THREE.CylinderGeometry(2, 2, 4, 16)
    const lampMat = new THREE.MeshStandardMaterial({ color: 0xf1c40f, emissive: 0xf1c40f, emissiveIntensity: 0.5 })
    const lamp = new THREE.Mesh(lampGeo, lampMat)
    lamp.position.y = 27
    group.add(lamp)
    // 塔顶
    const topGeo = new THREE.ConeGeometry(2.5, 3, 16)
    const topMat = new THREE.MeshStandardMaterial({ color: 0x2c3e50 })
    const top = new THREE.Mesh(topGeo, topMat)
    top.position.y = 30.5
    group.add(top)
    // 点光源
    const pointLight = new THREE.PointLight(0xf1c40f, 1, 50)
    pointLight.position.y = 27
    group.add(pointLight)

    group.position.set(-170, 0, -120)
    scene.add(group)
}

// ========== 初始化场景 ==========
const initScene = () => {
    const domWrap = sceneContainer.value as HTMLDivElement
    const w = domWrap.clientWidth
    const h = domWrap.clientHeight

    scene = new THREE.Scene()
    scene.background = new THREE.Color(0x87ceeb)
    scene.fog = new THREE.FogExp2(0x87ceeb, 0.006)

    camera = new THREE.PerspectiveCamera(52, w / h, 0.1, 3000)
    camera.position.set(60, 50, 120)
    camera.lookAt(0, 0, 0)

    renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' })
    renderer.setSize(w, h)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.shadowMap.enabled = true
    renderer.shadowMap.type = THREE.PCFShadowMap
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.15

    renderer.domElement.style.width = "100%"
    renderer.domElement.style.height = "100%"
    renderer.domElement.style.display = "block"
    renderer.domElement.style.userSelect = 'none'
    renderer.domElement.style.touchAction = 'none'
    renderer.domElement.style.cursor = 'grab'

    domWrap.appendChild(renderer.domElement)

    controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.05
    controls.minDistance = 40
    controls.maxDistance = 300
    controls.maxPolarAngle = Math.PI / 2.05
    controls.enabled = !dragEnable.value
    controls.target.set(20, 5, 0)

    // 光照
    const sunLight = new THREE.DirectionalLight(0xfff5e6, 1.4)
    sunLight.position.set(100, 150, 80)
    sunLight.castShadow = true
    sunLight.shadow.camera.left = -200
    sunLight.shadow.camera.right = 200
    sunLight.shadow.camera.top = 200
    sunLight.shadow.camera.bottom = -200
    sunLight.shadow.mapSize.set(2048, 2048)
    sunLight.shadow.bias = -0.0005
    scene.add(sunLight)
    scene.add(new THREE.AmbientLight(0xb8d4e8, 0.45))
    // 半球光
    const hemiLight = new THREE.HemisphereLight(0x87ceeb, 0x555b60, 0.3)
    scene.add(hemiLight)

    // 地面
    const groundGeo = new THREE.PlaneGeometry(400, 400)
    const groundMat = new THREE.MeshStandardMaterial({ color: 0x5d6d7e, roughness: 0.9, metalness: 0.02 })
    const ground = new THREE.Mesh(groundGeo, groundMat)
    ground.rotation.x = -Math.PI / 2
    ground.receiveShadow = true
    scene.add(ground)

    // 地面网格线
    const gridHelper = new THREE.GridHelper(400, 40, 0xffffff, 0xffffff)
    gridHelper.position.y = 0.02
    gridHelper.material.transparent = true
    gridHelper.material.opacity = 0.15
    scene.add(gridHelper)

    // 道路（集卡行驶路线）
    const roadMat = new THREE.MeshStandardMaterial({ color: 0x2c3e50, roughness: 0.95 })
    const road1 = new THREE.Mesh(new THREE.PlaneGeometry(400, 12), roadMat)
    road1.rotation.x = -Math.PI / 2
    road1.position.set(0, 0.03, 100)
    scene.add(road1)
    const road2 = new THREE.Mesh(new THREE.PlaneGeometry(12, 400), roadMat)
    road2.rotation.x = -Math.PI / 2
    road2.position.set(-130, 0.03, 0)
    scene.add(road2)
    // 道路标线
    const lineMat = new THREE.MeshBasicMaterial({ color: 0xf1c40f, transparent: true, opacity: 0.8 })
    for (let i = -190; i <= 190; i += 15) {
        const dash = new THREE.Mesh(new THREE.PlaneGeometry(6, 0.4), lineMat)
        dash.rotation.x = -Math.PI / 2
        dash.position.set(i, 0.04, 100)
        scene.add(dash)
    }

    // 分区线
    const splitLineMat = new THREE.MeshBasicMaterial({ color: 0xf1c40f, transparent: true, opacity: 0.7 })
    const split1 = new THREE.Mesh(new THREE.PlaneGeometry(180, 1), splitLineMat)
    split1.rotation.x = -Math.PI / 2
    split1.position.set(-30, 0.05, 0)
    split1.rotation.z = Math.PI / 2
    scene.add(split1)
    const split2 = new THREE.Mesh(new THREE.PlaneGeometry(180, 1), splitLineMat)
    split2.rotation.x = -Math.PI / 2
    split2.position.set(30, 0.05, 0)
    split2.rotation.z = Math.PI / 2
    scene.add(split2)

    // 水面（带波动动画）
    const waterGeo = new THREE.PlaneGeometry(900, 900, 50, 50)
    const waterMat = new THREE.MeshStandardMaterial({
        color: 0x4a90c2, roughness: 0.15, metalness: 0.3,
        transparent: true, opacity: 0.85
    })
    waterMesh = new THREE.Mesh(waterGeo, waterMat)
    waterMesh.rotation.x = -Math.PI / 2
    waterMesh.position.y = -12
    scene.add(waterMesh)

    // 岸边
    const quayGeo = new THREE.BoxGeometry(10, 3, 400)
    const quayMat = new THREE.MeshStandardMaterial({ color: 0x7f8c8d, roughness: 0.8 })
    const quay = new THREE.Mesh(quayGeo, quayMat)
    quay.position.set(165, -1.5, 0)
    quay.receiveShadow = true
    scene.add(quay)

    // 创建所有3D模型
    createYardSlots()
    createTowerCrane()
    createShip()
    createGate()
    createBuildings()
    createLighthouse()

    // 龙门吊（3台，分别在A/B/C区）
    rtgCranes.push(createRTG(-90, -20, 0x27ae60))
    rtgCranes.push(createRTG(0, 20, 0x3498db))
    rtgCranes.push(createRTG(90, -20, 0x9b59b6))

    // 集卡（4辆，在道路上行驶）
    trucks.push(createTruck(-100, 100, 0xe67e22))
    trucks.push(createTruck(50, 100, 0x2ecc71))
    trucks.push(createTruck(-130, -50, 0x9b59b6))
    trucks.push(createTruck(-130, 80, 0xe74c3c))

    renderer.domElement.addEventListener('mousedown', onMouseDown)
    renderer.domElement.addEventListener('mousemove', onMouseMove)
    renderer.domElement.addEventListener('mouseup', onMouseUp)
    window.addEventListener('resize', resizeHandler)
}

const onMouseDown = (e: MouseEvent) => {
    e.preventDefault()
    if (!dragEnable.value) return
    const canvas = renderer.domElement
    const rect = canvas.getBoundingClientRect()
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1
    raycaster.setFromCamera(mouse, camera)
    const intersects = raycaster.intersectObjects(scene.children, true)
    selectedContainer = null
    for (let i = 0; i < intersects.length; i++) {
        let obj: THREE.Object3D | null = intersects[i].object
        while (obj) {
            const group = obj as THREE.Group
            if (group.userData?.id) {
                selectedContainer = group
                break
            }
            if (obj.parent === scene) break
            obj = obj.parent
        }
        if (selectedContainer) break
    }
    if (selectedContainer) {
        controls.enabled = false
        renderer.domElement.style.cursor = 'grabbing'
    }
}

const onMouseMove = (e: MouseEvent) => {
    if (!selectedContainer || !dragEnable.value) return
    const canvas = renderer.domElement
    const rect = canvas.getBoundingClientRect()
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1
    raycaster.setFromCamera(mouse, camera)

    const groundMesh = scene.children.find((obj): obj is THREE.Mesh => {
        const m = obj as THREE.Mesh
        return m.geometry instanceof THREE.PlaneGeometry && (m.material as THREE.MeshStandardMaterial).color?.getHex() === 0x5d6d7e
    })
    if (!groundMesh) return

    const intersect = raycaster.intersectObject(groundMesh)
    if (intersect.length > 0) {
        const p = intersect[0].point
        p.x = Math.round(p.x / 25) * 25
        p.z = Math.round(p.z / 25) * 25
        selectedContainer.position.copy(p)
        selectedContainer.position.y = 1.3
    }
}

const onMouseUp = async () => {
    if (!selectedContainer || !dragEnable.value) return
    const tempBox = selectedContainer
    selectedContainer = null
    controls.enabled = true
    renderer.domElement.style.cursor = 'grab'

    const item = tempBox.userData as ContainerItem
    const pos = tempBox.position
    const finalX = Number(pos.x.toFixed(2))
    const finalZ = Number(pos.z.toFixed(2))

    try {
        if (item.loadStatus === 0 && pos.x > 160) {
            await $api.put(`/api/container/load/ship/${item.id}`)
        } else if (item.loadStatus === 1 && pos.x < 160) {
            let areaNo = 1
            if (pos.x >= -60 && pos.x < 60) areaNo = 2
            if (pos.x >= 60) areaNo = 3
            await $api.post(`/api/container/unload/yard?id=${item.id}&areaNo=${areaNo}`)
        }
        await $api.post('/api/container/savePos', { id: item.id, x: finalX, z: finalZ })
        await refreshAllContainer()
    } catch (err) {
        console.error("保存失败", err)
        alert('操作异常，数据回滚')
        await refreshAllContainer()
    }
}

const resizeHandler = () => {
    const domWrap = sceneContainer.value as HTMLDivElement
    const w = domWrap.clientWidth
    const h = domWrap.clientHeight
    camera.aspect = w / h
    camera.updateProjectionMatrix()
    renderer.setSize(w, h)
}

const createContainer = () => {
    const group = new THREE.Group()
    const boxGeo = new THREE.BoxGeometry(12, 2.6, 2.4)
    const bodyMat = new THREE.MeshStandardMaterial({ color: 0xaaaaaa, roughness: 0.72, metalness: 0.15 })
    const body = new THREE.Mesh(boxGeo, bodyMat)
    body.castShadow = true
    group.add(body)
    const cornerGeo = new THREE.BoxGeometry(0.5, 0.5, 0.5)
    const cornerMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.55 })
    const corners = [
        [-5.75, 1.05, -0.95], [5.75, 1.05, -0.95],
        [-5.75, 1.05, 0.95], [5.75, 1.05, 0.95],
        [-5.75, -1.05, -0.95], [5.75, -1.05, -0.95],
        [-5.75, -1.05, 0.95], [5.75, -1.05, 0.95],
    ]
    corners.forEach(pos => {
        const c = new THREE.Mesh(cornerGeo, cornerMat)
        c.position.set(pos[0], pos[1], pos[2])
        c.castShadow = true
        group.add(c)
    })
    const doorFrameGeo = new THREE.BoxGeometry(0.3, 2.2, 2.2)
    const doorMat = new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.6 })
    const doorFrame = new THREE.Mesh(doorFrameGeo, doorMat)
    doorFrame.position.x = 5.85
    group.add(doorFrame)
    const planeGeo = new THREE.PlaneGeometry(11.8, 2.5)
    const planeMat = new THREE.MeshStandardMaterial({
        map: sideTexture, transparent: true, opacity: 0.96, roughness: 0.6, metalness: 0.2, alphaTest: 0.1
    })
    const rightSide = new THREE.Mesh(planeGeo, planeMat)
    rightSide.position.set(0, 0, 1.22)
    group.add(rightSide)
    const leftSide = new THREE.Mesh(planeGeo, planeMat.clone())
    leftSide.position.set(0, 0, -1.22)
    leftSide.rotation.y = Math.PI
    group.add(leftSide)

    containerModel = group
}

const createContainerList = (list: ContainerItem[]) => {
    if (!list.length || containerModel === null) {
        console.warn("⚠️ 箱体模板未就绪，暂不渲染集装箱")
        return
    }
    containerMap.forEach(oldGroup => {
        scene.remove(oldGroup)
        oldGroup.traverse(child => {
            const mesh = child as THREE.Mesh
            if (mesh.geometry) mesh.geometry.dispose()
            if (mesh.material) {
                const mats = mesh.material as THREE.Material | THREE.Material[]
                Array.isArray(mats) ? mats.forEach(m => m.dispose()) : mats.dispose()
            }
        })
    })
    containerMap.clear()

    for (const item of list) {
        if (!containerModel) continue
        const instance = containerModel.clone(true) as THREE.Group
        instance.userData = item

        instance.traverse(child => {
            const mesh = child as THREE.Mesh
            if (!mesh.isMesh) return
            const originMat = mesh.material as THREE.MeshStandardMaterial
            const newMat = originMat.clone()
            if (newMat.color?.getHex() === 0xaaaaaa && colorMap[item.state]) {
                newMat.color.copy(colorMap[item.state])
            }
            mesh.material = newMat
        })

        let areaDesc = item.loadStatus === 1 ? '货轮船舱（未分配仓位）' : `分区A ${item.areaNo}排1列`
        const infoStr = `箱号：${item.containerNo}
货物：${item.cargoType}
目的港：${item.destPort}
重量：${item.weight} t
状态：${getStatusChinese(item.rawStatus)}
仓位：${areaDesc}`

        const textSprite = createInfoSprite(infoStr)
        textSprite.position.y = 3.5
        instance.add(textSprite)

        if (item.loadStatus === 1) {
            instance.position.set(205, 2, 0)
        } else {
            instance.position.set(item.saveX, 1.3, item.saveZ)
        }

        scene.add(instance)
        containerMap.set(String(item.id), instance)
    }
}

const refreshAllContainer = async () => {
    try {
        const res: any = await $api.get('/api/container/twin')
        let rawList: any[] = []
        if (Array.isArray(res)) {
            rawList = res
        } else if (Array.isArray(res?.data)) {
            rawList = res.data
        } else if (Array.isArray(res?.data?.data)) {
            rawList = res.data.data
        } else if (Array.isArray(res?.data?.records)) {
            rawList = res.data.records
        }
        containerListData = rawList.map((row: any) => {
            const slot = row.areaNo ? `A0${row.areaNo}-01-01` : 'A02-01-01'
            return {
                id: row.id,
                containerNo: row.containerNo,
                cargoType: row.cargoType,
                destPort: row.destPort,
                weight: row.weight,
                rawStatus: row.status,
                state: getContainerState(row.status, row.loadStatus as 0 | 1),
                areaNo: row.areaNo,
                loadStatus: row.loadStatus,
                slotCode: slot,
                saveX: Number(row.x ?? row.xPos ?? 0),
                saveZ: Number(row.z ?? row.zPos ?? 0)
            } as ContainerItem
        })
        createContainerList(containerListData)
    } catch (err) {
        console.error('获取集装箱数据异常：', err)
    }
}

const startPoll = () => {
    pollTimer = window.setInterval(() => {
        refreshAllContainer()
    }, 5000)
}

// 动画循环
const renderLoop = () => {
    animationId = requestAnimationFrame(renderLoop)
    const delta = clock.getDelta()
    const elapsed = clock.getElapsedTime()

    // 水面波动动画
    if (waterMesh) {
        const positions = (waterMesh.geometry as THREE.PlaneGeometry).attributes.position
        for (let i = 0; i < positions.count; i++) {
            const x = positions.getX(i)
            const y = positions.getY(i)
            const z = Math.sin(x * 0.05 + elapsed * 1.5) * 0.5 + Math.cos(y * 0.05 + elapsed * 1.2) * 0.5
            positions.setZ(i, z)
        }
        positions.needsUpdate = true
        waterMesh.geometry.computeVertexNormals()
    }

    // 集卡移动动画
    trucks.forEach(truck => {
        const data = truck.userData
        if (data.baseZ === 100) {
            // 水平道路行驶
            truck.position.x += data.speed * data.direction * delta
            if (truck.position.x > 180) {
                truck.position.x = -180
                truck.rotation.y = 0
            }
        } else {
            // 垂直道路行驶
            truck.position.z += data.speed * data.direction * delta
            if (truck.position.z > 180) {
                truck.position.z = -180
            }
            if (truck.position.z < -180) {
                truck.position.z = 180
            }
        }
    })

    // 龙门吊小车移动动画
    rtgCranes.forEach((rtg, idx) => {
        const trolley = rtg.getObjectByName('rtgTrolley')
        const spreader = rtg.getObjectByName('rtgSpreader')
        if (trolley) {
            trolley.position.x = Math.sin(elapsed * 0.8 + idx * 2) * 6
        }
        if (spreader) {
            spreader.position.x = Math.sin(elapsed * 0.8 + idx * 2) * 6
            spreader.position.y = 14 + Math.sin(elapsed * 1.2 + idx) * 2
        }
    })

    // 岸桥吊钩小车移动
    if (towerCrane) {
        const trolley = towerCrane.getObjectByName('trolley')
        const rope = towerCrane.getObjectByName('rope')
        const spreader = towerCrane.getObjectByName('spreader')
        if (trolley) {
            const tx = 25 + Math.sin(elapsed * 0.5) * 15
            trolley.position.x = tx
            if (rope) rope.position.x = tx
            if (spreader) spreader.position.x = tx
        }
    }

    // 船舶轻微晃动
    if (shipGroup) {
        shipGroup.position.y = -12 + Math.sin(elapsed * 0.8) * 0.3
        shipGroup.rotation.z = Math.sin(elapsed * 0.6) * 0.01
    }

    controls.update()
    renderer.render(scene, camera)
}

onMounted(async () => {
    await nextTick()
    initTexture()
    initScene()
    createContainer()
    await refreshAllContainer()
    startPoll()
    initWebSocket(() => {
        refreshAllContainer()
    })
    renderLoop()
})

onUnmounted(() => {
    cancelAnimationFrame(animationId)
    if (pollTimer) clearInterval(pollTimer)
    window.removeEventListener('resize', resizeHandler)
    renderer.domElement.removeEventListener('mousedown', onMouseDown)
    renderer.domElement.removeEventListener('mousemove', onMouseMove)
    renderer.domElement.removeEventListener('mouseup', onMouseUp)
    renderer.dispose()
})
</script>

<style scoped>
.twin-wrap {
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
}
.page-header {
    padding: 14px 24px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 16px;
    background: rgba(255, 255, 255, 0.95);
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    z-index: 10;
}
.page-header h2 {
    margin: 0;
    font-size: 20px;
    color: #11616B;
    font-weight: 600;
}
.header-right {
    display: flex;
    align-items: center;
    gap: 12px;
}
.tip-text {
    font-size: 13px;
    color: #606266;
}
.status-desc {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}
.three-canvas {
    flex: 1;
    width: 100%;
    overflow: hidden;
}
</style>
