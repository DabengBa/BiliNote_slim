/**
 * Platform Source 处理器
 * 处理 platform_source 字段的写入策略和校验机制
 */

import { detectPlatformFromUrl } from './urlUtils'

// 平台来源类型
export type PlatformSourceType = 'auto_detected' | 'user_provided' | 'unknown'

// 平台来源配置
const PLATFORM_SOURCE_CONFIG = {
  auto_detected: {
    label: '自动检测',
    description: 'URL自动识别平台',
    priority: 100
  },
  user_provided: {
    label: '手动选择', 
    description: '用户手动选择平台',
    priority: 90
  },
  unknown: {
    label: '未知来源',
    description: '来源未知',
    priority: 10
  }
} as const

/**
 * 平台来源策略接口
 */
interface PlatformSourceStrategy {
  detectSource: (url: string, currentPlatform?: string) => PlatformSourceType
  validateSource: (url: string, platform: string, source: PlatformSourceType) => {
    isValid: boolean
    errorMessage?: string
  }
  getSourceDescription: (source: PlatformSourceType) => string
}

/**
 * 默认平台来源策略
 */
const defaultStrategy: PlatformSourceStrategy = {
  detectSource: (url: string, currentPlatform?: string): PlatformSourceType => {
    if (!url || url.trim() === '') {
      return 'unknown'
    }

    // 如果有当前平台，检查是否为自动检测
    if (currentPlatform) {
      const detectedPlatform = detectPlatformFromUrl(url)
      
      // 如果检测到的平台与当前平台匹配，认为是自动检测
      if (detectedPlatform === currentPlatform && detectedPlatform !== 'unknown') {
        return 'auto_detected'
      }
      
      // 如果检测不到平台或检测结果与当前平台不匹配，认为是手动选择
      if (detectedPlatform === 'unknown' || detectedPlatform !== currentPlatform) {
        return 'user_provided'
      }
    }

    // 如果没有当前平台，尝试自动检测
    const detectedPlatform = detectPlatformFromUrl(url)
    if (detectedPlatform !== 'unknown') {
      return 'auto_detected'
    }

    return 'unknown'
  },

  validateSource: (url: string, platform: string, source: PlatformSourceType) => {
    // 基本校验
    if (!url || !platform) {
      return {
        isValid: false,
        errorMessage: 'URL和平台信息不能为空'
      }
    }

    // 根据来源类型进行具体校验
    switch (source) {
      case 'auto_detected': {
        const detectedPlatform = detectPlatformFromUrl(url)
        
        if (detectedPlatform === 'unknown') {
          return {
            isValid: false,
            errorMessage: '无法从URL自动检测平台，不能设置为自动检测来源'
          }
        }
        
        if (detectedPlatform !== platform) {
          return {
            isValid: false,
            errorMessage: `自动检测到平台为 ${detectedPlatform}，但设置的是 ${platform}`
          }
        }
        
        return { isValid: true }
      }

      case 'user_provided': {
        // 手动选择需要验证平台是否合理
        const validPlatforms = ['bilibili', 'youtube', 'local']
        if (!validPlatforms.includes(platform)) {
          return {
            isValid: false,
            errorMessage: `不支持的平台类型: ${platform}`
          }
        }
        return { isValid: true }
      }

      default:
        return {
          isValid: false,
          errorMessage: '未知的平台来源类型'
        }
    }
  },

  getSourceDescription: (source: PlatformSourceType): string => {
    return PLATFORM_SOURCE_CONFIG[source].description
  }
}

/**
 * Platform Source Handler 类
 */
export class PlatformSourceHandler {
  private strategy: PlatformSourceStrategy

  constructor(strategy?: PlatformSourceStrategy) {
    this.strategy = strategy || defaultStrategy
  }

  /**
   * 检测平台来源
   * @param url 视频URL
   * @param currentPlatform 当前平台
   * @returns 平台来源类型
   */
  detectPlatformSource(url: string, currentPlatform?: string): PlatformSourceType {
    return this.strategy.detectSource(url, currentPlatform)
  }

  /**
   * 校验平台来源
   * @param url 视频URL
   * @param platform 平台
   * @param source 平台来源
   * @returns 校验结果
   */
  validatePlatformSource(url: string, platform: string, source: PlatformSourceType) {
    return this.strategy.validateSource(url, platform, source)
  }

  /**
   * 获取平台来源描述
   * @param source 平台来源类型
   * @returns 描述文字
   */
  getSourceDescription(source: PlatformSourceType): string {
    return this.strategy.getSourceDescription(source)
  }

  /**
   * 为表单数据添加平台来源信息
   * @param formData 表单数据
   * @returns 包含platform_source的表单数据
   */
  addPlatformSourceToForm(formData: any): any {
    const { video_url, platform } = formData
    
    if (!video_url) {
      return {
        ...formData,
        platform_source: 'unknown'
      }
    }

    const source = this.detectPlatformSource(video_url, platform)
    
    return {
      ...formData,
      platform_source: source
    }
  }

  /**
   * 验证完整的表单数据
   * @param formData 表单数据
   * @returns 验证结果
   */
  validateFormData(formData: any) {
    const { video_url, platform, platform_source } = formData

    // 基本字段校验
    if (!video_url) {
      return {
        isValid: false,
        errors: ['视频URL不能为空']
      }
    }

    if (!platform) {
      return {
        isValid: false,
        errors: ['平台信息不能为空']
      }
    }

    if (!platform_source) {
      return {
        isValid: false,
        errors: ['平台来源信息不能为空']
      }
    }

    // 使用策略验证
    const validation = this.validatePlatformSource(video_url, platform, platform_source)
    
    if (!validation.isValid) {
      return {
        isValid: false,
        errors: [validation.errorMessage || '平台来源验证失败']
      }
    }

    return {
      isValid: true,
      errors: []
    }
  }

  /**
   * 获取平台来源显示信息
   * @param source 平台来源类型
   * @returns 显示信息
   */
  getSourceDisplayInfo(source: PlatformSourceType) {
    const config = PLATFORM_SOURCE_CONFIG[source]
    
    return {
      label: config.label,
      description: config.description,
      priority: config.priority
    }
  }
}

// 导出默认实例
export const platformSourceHandler = new PlatformSourceHandler()

// 导出工具函数
export const detectPlatformSource = (url: string, currentPlatform?: string) =>
  platformSourceHandler.detectPlatformSource(url, currentPlatform)

export const validatePlatformSource = (url: string, platform: string, source: PlatformSourceType) =>
  platformSourceHandler.validatePlatformSource(url, platform, source)

export const addPlatformSourceToForm = (formData: any) =>
  platformSourceHandler.addPlatformSourceToForm(formData)

export const validateFormDataWithSource = (formData: any) =>
  platformSourceHandler.validateFormData(formData)