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

// 全局数据源：始终存放后端返回的数据库最新数据（唯一数据源）
let containerListData: ContainerItem[] = []
// 轮询定时器
let pollTimer: number | null = null


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

// 整合 loadStatus + rawStatus 双重判断
const getContainerState = (rawStatus: number, loadStatus: 0 | 1): ContainerState => {
    // 只要装船状态为1，直接返回船上蓝色状态
    if (loadStatus === 1) {
        return 'ship'
    }
    // 堆场存放：按原始状态区分颜色
    switch (rawStatus) {
        case 0:
        case 1:
            return 'normal' // 绿色：待装船
        case 2:
            return 'damage' // 橙色：破损
        case 3:
            return 'tilt'   // 红色：堆码超限
        default:
            return 'normal'
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

const createTowerCrane = () => {
    const group = new THREE.Group()
    const pillarGeo = new THREE.BoxGeometry(4, 46, 4)
    const pillarMat = new THREE.MeshStandardMaterial({ color: 0x505050, roughness: 0.8 })
    const pillar = new THREE.Mesh(pillarGeo, pillarMat)
    pillar.position.y = 23
    pillar.castShadow = true
    group.add(pillar)
    const armGeo = new THREE.BoxGeometry(56, 2.4, 3)
    const armMat = new THREE.MeshStandardMaterial({ color: 0x606060 })
    const arm = new THREE.Mesh(armGeo, armMat)
    arm.position.set(28, 42, 0)
    arm.castShadow = true
    group.add(arm)
    group.position.set(130, 0, 0)
    scene.add(group)
    towerCrane = group
}

const createShip = () => {
    const group = new THREE.Group()
    const hullGeo = new THREE.BoxGeometry(92, 13, 30)
    const hullMat = new THREE.MeshStandardMaterial({ color: 0x204060, roughness: 0.7 })
    const hull = new THREE.Mesh(hullGeo, hullMat)
    hull.position.y = -6.5
    hull.receiveShadow = true
    group.add(hull)
    const cabinGeo = new THREE.BoxGeometry(76, 8, 23)
    const cabinMat = new THREE.MeshStandardMaterial({ color: 0x183048 })
    const cabin = new THREE.Mesh(cabinGeo, cabinMat)
    cabin.position.y = 4
    group.add(cabin)
    group.position.set(190, -12, 0)
    scene.add(group)
    shipGroup = group
}

const initScene = () => {
    const domWrap = sceneContainer.value as HTMLDivElement
    const w = domWrap.clientWidth
    const h = domWrap.clientHeight

    scene = new THREE.Scene()
    scene.background = new THREE.Color(0x86bfe9)
    scene.fog = new THREE.FogExp2(0x86bfe9, 0.01)

    camera = new THREE.PerspectiveCamera(52, w / h, 0.1, 3000)
    camera.position.set(45, 35, 95)
    camera.lookAt(0, 0, 0)

    renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' })
    renderer.setSize(w, h)
    renderer.setPixelRatio(window.devicePixelRatio)
    renderer.shadowMap.enabled = true
    renderer.shadowMap.type = THREE.PCFSoftShadowMap
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.12

    renderer.domElement.style.width = "100%";
    renderer.domElement.style.height = "100%";
    renderer.domElement.style.display = "block";
    renderer.domElement.style.userSelect = 'none'
    renderer.domElement.style.touchAction = 'none'
    renderer.domElement.style.cursor = 'grab'

    domWrap.appendChild(renderer.domElement)

    controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.05
    controls.minDistance = 45
    controls.maxDistance = 240
    controls.maxPolarAngle = Math.PI / 2.03
    controls.enabled = !dragEnable.value

    const sunLight = new THREE.DirectionalLight(0xfff8e6, 1.25)
    sunLight.position.set(95, 140, 70)
    sunLight.castShadow = true
    sunLight.shadow.camera.left = -180
    sunLight.shadow.camera.right = 180
    sunLight.shadow.camera.top = 180
    sunLight.shadow.camera.bottom = -180
    sunLight.shadow.mapSize.set(2048, 2048)
    scene.add(sunLight)
    scene.add(new THREE.AmbientLight(0xc4e0f7, 0.35))

    const groundGeo = new THREE.PlaneGeometry(360, 360)
    const groundMat = new THREE.MeshStandardMaterial({ color: 0x555b60, roughness: 0.9, metalness: 0.01 })
    const ground = new THREE.Mesh(groundGeo, groundMat)
    ground.rotation.x = -Math.PI / 2
    ground.receiveShadow = true
    scene.add(ground)

    const lineGeo = new THREE.PlaneGeometry(360, 0.6)
    const lineMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.7 })
    for (let i = -180; i <= 180; i += 28) {
        const lineH = new THREE.Mesh(lineGeo, lineMat)
        lineH.rotation.x = -Math.PI / 2
        lineH.position.y = 0.01
        lineH.position.z = i
        scene.add(lineH)
        const lineV = new THREE.Mesh(lineGeo, lineMat)
        lineV.rotation.x = -Math.PI / 2
        lineV.rotation.z = Math.PI / 2
        lineV.position.y = 0.01
        lineV.position.x = i
        scene.add(lineV)
    }

    const splitLineMat = new THREE.MeshBasicMaterial({ color: 0xffff00, transparent: true, opacity: 0.8 })
    const split1 = new THREE.Mesh(new THREE.PlaneGeometry(360, 1.2), splitLineMat)
    split1.rotation.x = -Math.PI / 2
    split1.rotation.z = Math.PI / 2
    split1.position.y = 0.02
    split1.position.x = -60
    scene.add(split1)

    const split2 = new THREE.Mesh(new THREE.PlaneGeometry(360, 1.2), splitLineMat)
    split2.rotation.x = -Math.PI / 2
    split2.rotation.z = Math.PI / 2
    split2.position.y = 0.02
    split2.position.x = 60
    scene.add(split2)

    const waterGeo = new THREE.PlaneGeometry(800, 800)
    const waterMat = new THREE.MeshStandardMaterial({ color: 0x4582b5, roughness: 0.18, metalness: 0.22 })
    const water = new THREE.Mesh(waterGeo, waterMat)
    water.rotation.x = -Math.PI / 2
    water.position.y = -12
    scene.add(water)

    createTowerCrane()
    createShip()

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
        return m.geometry instanceof THREE.PlaneGeometry && (m.material as THREE.MeshStandardMaterial).color.getHex() === 0x555b60
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

// 拖拽松开：保存入库后立刻重载数据库最新数据渲染场景（核心修复）
// 拖拽松开：保存入库后立刻重载数据库最新数据渲染场景（核心修复）
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
        // ========== 第一步：先执行装船/卸船业务（修改loadStatus、areaNo）==========
        if (item.loadStatus === 0 && pos.x > 160) {
            console.log('🚢 执行装船')
            await $api.put(`/api/container/load/ship/${item.id}`)
        }
        else if (item.loadStatus === 1 && pos.x < 160) {
            let areaNo = 1
            if (pos.x >= -60 && pos.x < 60) areaNo = 2
            if (pos.x >= 60) areaNo = 3
            console.log('📦 执行卸船，分区：', areaNo)
            await $api.post(`/api/container/unload/yard?id=${item.id}&areaNo=${areaNo}`)
        }

        // ========== 第二步：再保存拖拽后的三维坐标 ==========
        await $api.post('/api/container/savePos', {
            id: item.id,
            x: finalX,
            z: finalZ
        })

        // ========== 第三步：刷新3D场景数据 ==========
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
    console.log("✅ 箱体基础模板创建完成", containerModel)
}

// 销毁场景所有旧箱体，用最新数据重新生成
const createContainerList = (list: ContainerItem[]) => {
    if (!list.length || containerModel === null) {
        console.warn("⚠️ 箱体模板未就绪，暂不渲染集装箱")
        return
    }

    // 清空旧场景物体
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
            if (newMat.color.getHex() === 0xaaaaaa && colorMap[item.state]) {
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

        // 坐标完全取自数据库字段saveX / saveZ
        if (item.loadStatus === 1) {
            instance.position.set(205, 2, 0)
        } else {
            instance.position.set(item.saveX, 1.3, item.saveZ)
        }

        scene.add(instance)
        containerMap.set(String(item.id), instance)
    }
}

// 从后端拉取数据库最新所有集装箱数据
const refreshAllContainer = async () => {
    try {
        const res = await $api.get('/api/container/twin')
        console.log("接口完整返回：", res)
        const rawList = res.data.data ?? []
        containerListData = rawList.map((row: any) => {
            const slot = row.areaNo ? `A0${row.areaNo}-01-01` : 'A02-01-01'
            return {
                id: row.id,
                containerNo: row.containerNo,
                cargoType: row.cargoType,
                destPort: row.destPort,
                weight: row.weight,
                rawStatus: row.status,
                // 调用新方法
                state: getContainerState(row.status, row.loadStatus as 0 | 1),
                areaNo: row.areaNo,
                loadStatus: row.loadStatus,
                slotCode: slot,
                saveX: Number(row.x),
                saveZ: Number(row.z)
            } as ContainerItem
        })

        // 重新渲染场景
        createContainerList(containerListData)
    } catch (err) {
        console.error('获取集装箱数据异常：', err)
    }
}

// 开启兜底轮询：5秒拉取一次数据库数据
const startPoll = () => {
    pollTimer = window.setInterval(() => {
        refreshAllContainer()
    }, 5000)
}

const renderLoop = () => {
    animationId = requestAnimationFrame(renderLoop)
    controls.update()
    renderer.render(scene, camera)
}

onMounted(async () => {
    await nextTick()
    initTexture()
    initScene()
    createContainer()
    // 首次载入拉取数据渲染
    await refreshAllContainer()
    // 开启轮询
    startPoll()
    // WebSocket绑定刷新回调：收到后端推送消息重载数据
    initWebSocket(() => {
        refreshAllContainer()
    })
    renderLoop()
})

onUnmounted(() => {
    cancelAnimationFrame(animationId)
    // 销毁定时器
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
    padding: 16px 24px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 20px;
    background: #ffffff;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    z-index: 10;
}
.header-right {
    display: flex;
    align-items: center;
    gap: 12px;
}
.tip-text {
    font-size: 14px;
    color: #333;
}
.status-desc {
    display: flex;
    gap: 10px;
}
.three-canvas {
    flex: 1;
    width: 100%;
    overflow: hidden;
}
</style>
