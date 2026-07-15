import request from '../utils/request'

export interface AiRecognizeRequest {
    containerNo: string
    imageName: string
}

export interface AiRecognizeResult {
    inspectNo: string
    containerNo: string
    damageResult: string
    damageLevel: string
    confidence: number
    costMs: number
}

export function recognizeContainer(data: AiRecognizeRequest): Promise<{
    code: number
    msg: string
    data: AiRecognizeResult
}> {
    return request({
        url: '/api/ai/recognize',
        method: 'post',
        data
    })
}
