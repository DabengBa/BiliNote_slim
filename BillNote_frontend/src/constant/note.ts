/* -------------------- 常量 -------------------- */
import {
  BiliBiliLogo,
  LocalLogo,
  YoutubeLogo,
} from '@/components/Icons/platform.tsx'

export const noteFormats = [
  { label: '目录', value: 'toc' },
  { label: '原片跳转', value: 'link' },
  { label: '原片截图', value: 'screenshot' },
  { label: 'AI总结', value: 'summary' },
] as const

export const noteStyles = [
  { label: '精简', value: 'minimal' },
  { label: '详细', value: 'detailed' },
  { label: '教程', value: 'tutorial' },
  { label: '学术', value: 'academic' },
  { label: '小红书', value: 'xiaohongshu' },
  { label: '生活向', value: 'life_journal' },
  { label: '任务导向', value: 'task_oriented' },
  { label: '商业风格', value: 'business' },
  { label: '会议纪要', value: 'meeting_minutes' },
] as const

export const videoPlatforms = [
  { label: '哔哩哔哩', value: 'bilibili', logo: BiliBiliLogo },
  { label: 'YouTube', value: 'youtube', logo: YoutubeLogo },
  { label: '本地视频', value: 'local', logo: LocalLogo },
] as const

/**
 * URL白名单：仅允许这些域名
 * 包含短链接和完整域名
 */
export const SUPPORTED_URL_HOSTS = [
  // Bilibili
  'bilibili.com',
  'b23.tv',
  // YouTube
  'youtube.com',
  'youtu.be',
] as const

/**
 * 禁止的关键词：用于检测不支持的平台
 * 如果URL包含这些关键词，直接拒绝
 */
export const BLOCKED_KEYWORDS = [
  'douyin.com',
  'v.douyin.com',
  'kuaishou.com',
  'v.kuaishou.com',
  'xiaoyuzhoufm.com',
  'tiktok.com',
] as const

/**
 * 错误提示文案（与后端保持一致）
 */
export const ERROR_MESSAGES = {
  PLATFORM_NOT_SUPPORTED: '暂不支持该视频平台或链接格式无效',
  INVALID_URL: '请输入正确的视频链接',
  MISSING_URL: '视频链接不能为空',
  MISSING_LOCAL_PATH: '本地视频路径不能为空',
} as const
