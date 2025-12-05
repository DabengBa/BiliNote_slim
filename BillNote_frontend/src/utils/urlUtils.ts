/**
 * URL 平台自动识别工具
 * 根据输入的URL自动识别视频平台
 */

// 支持的平台类型
export type SupportedPlatform = 'bilibili' | 'youtube' | 'local' | 'unknown'

// 平台映射规则
interface PlatformRule {
  platform: SupportedPlatform
  patterns: RegExp[]
  priority: number // 优先级，数值越大优先级越高
}

/**
 * URL平台映射规则
 * 按优先级排序，包含精确匹配和模糊匹配
 */
const PLATFORM_RULES: PlatformRule[] = [
  {
    platform: 'bilibili',
    priority: 100,
    patterns: [
      /^https?:\/\/(www\.)?bilibili\.com\//i,
      /^https?:\/\/b23\.tv\//i,
      /^https?:\/\/(www\.)?b23\.tv\//i,
    ]
  },
  {
    platform: 'youtube', 
    priority: 90,
    patterns: [
      /^https?:\/\/(www\.)?youtube\.com\//i,
      /^https?:\/\/youtu\.be\//i,
      /^https?:\/\/(m\.)?youtube\.com\//i,
    ]
  },
  {
    platform: 'local',
    priority: 10,
    patterns: [
      /^file:\/\//i,
      /^[a-z]:\\.*/i, // Windows 本地路径
      /^\/.*/i, // Unix/Linux 本地路径
      /^[a-z]:\//i, // Windows 根目录
    ]
  }
]

/**
 * 验证URL格式
 * @param url 输入的URL字符串
 * @returns 是否为有效的URL格式
 */
export function isValidUrl(url: string): boolean {
  if (!url || typeof url !== 'string') {
    return false
  }
  
  try {
    // 对于本地路径，不进行URL验证
    if (url.startsWith('file:') || /^[a-z]:[\\/]/i.test(url) || /^\/[a-zA-Z]/.test(url)) {
      return true
    }
    
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * 自动识别URL对应的平台
 * @param url 输入的URL字符串
 * @returns 识别的平台类型，如果无法识别则返回 'unknown'
 */
export function detectPlatformFromUrl(url: string): SupportedPlatform {
  if (!url || typeof url !== 'string') {
    return 'unknown'
  }

  // 清理URL，去除前后空格
  const cleanUrl = url.trim()
  
  // 遍历平台规则，按优先级排序
  const sortedRules = [...PLATFORM_RULES].sort((a, b) => b.priority - a.priority)
  
  for (const rule of sortedRules) {
    for (const pattern of rule.patterns) {
      if (pattern.test(cleanUrl)) {
        return rule.platform
      }
    }
  }
  
  return 'unknown'
}

/**
 * 获取平台显示名称
 * @param platform 平台类型
 * @returns 平台显示名称
 */
export function getPlatformDisplayName(platform: SupportedPlatform): string {
  const displayNames: Record<SupportedPlatform, string> = {
    'bilibili': '哔哩哔哩',
    'youtube': 'YouTube', 
    'local': '本地视频',
    'unknown': '未知平台'
  }
  
  return displayNames[platform] || '未知平台'
}

/**
 * 检查URL是否受支持
 * @param url 输入的URL字符串
 * @returns 是否受支持的平台
 */
export function isSupportedPlatform(url: string): boolean {
  const platform = detectPlatformFromUrl(url)
  return platform !== 'unknown' && platform !== 'local'
}

/**
 * 获取URL的详细信息
 * @param url 输入的URL字符串
 * @returns URL详细信息对象
 */
export function getUrlInfo(url: string) {
  const platform = detectPlatformFromUrl(url)
  const isValid = isValidUrl(url)
  const isSupported = isSupportedPlatform(url)
  
  return {
    platform,
    platformDisplayName: getPlatformDisplayName(platform),
    isValid,
    isSupported,
    originalUrl: url
  }
}