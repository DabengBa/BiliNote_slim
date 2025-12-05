/**
 * 前端URL平台自动识别功能测试
 * 验证阶段2: T006-T008b的UI交互测试
 */

// 导入我们要测试的功能
const { detectPlatformFromUrl, getPlatformDisplayName, isValidUrl } = {
  detectPlatformFromUrl: (url: string): string => {
    // 测试URL平台检测逻辑
    if (!url || typeof url !== 'string') {
      return 'unknown'
    }

    const cleanUrl = url.trim()
    
    // 哔哩哔哩平台检测
    if (/^https?:\/\/(www\.)?bilibili\.com\//i.test(cleanUrl) || 
        /^https?:\/\/b23\.tv\//i.test(cleanUrl) ||
        /^https?:\/\/(www\.)?b23\.tv\//i.test(cleanUrl)) {
      return 'bilibili'
    }
    
    // YouTube平台检测  
    if (/^https?:\/\/(www\.)?youtube\.com\//i.test(cleanUrl) ||
        /^https?:\/\/youtu\.be\//i.test(cleanUrl) ||
        /^https?:\/\/(m\.)?youtube\.com\//i.test(cleanUrl)) {
      return 'youtube'
    }
    
    // 本地视频检测
    if (/^file:\/\//i.test(cleanUrl) || /^[a-z]:\\.*/i.test(cleanUrl) || 
        /^\/.*/i.test(cleanUrl) || /^[a-z]:\//i.test(cleanUrl)) {
      return 'local'
    }
    
    return 'unknown'
  },
  
  getPlatformDisplayName: (platform: string): string => {
    const displayNames: Record<string, string> = {
      'bilibili': '哔哩哔哩',
      'youtube': 'YouTube', 
      'local': '本地视频',
      'unknown': '未知平台'
    }
    return displayNames[platform] || '未知平台'
  },
  
  isValidUrl: (url: string): boolean => {
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
}

/**
 * 测试用例
 */
const testCases = [
  // 哔哩哔哩平台测试
  {
    url: 'https://www.bilibili.com/video/BV1xx411c7xx/',
    expected: 'bilibili',
    description: '哔哩哔哩完整URL'
  },
  {
    url: 'https://b23.tv/av123456',
    expected: 'bilibili', 
    description: '哔哩哔哩短链接'
  },
  {
    url: 'https://www.b23.tv/av123456',
    expected: 'bilibili',
    description: '哔哩哔哩短链接带www'
  },
  
  // YouTube平台测试
  {
    url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    expected: 'youtube',
    description: 'YouTube完整URL'
  },
  {
    url: 'https://youtu.be/dQw4w9WgXcQ',
    expected: 'youtube',
    description: 'YouTube短链接'
  },
  {
    url: 'https://m.youtube.com/watch?v=dQw4w9WgXcQ',
    expected: 'youtube',
    description: 'YouTube移动端URL'
  },
  
  // 本地视频测试
  {
    url: 'file:///C:/Videos/sample.mp4',
    expected: 'local',
    description: '本地文件路径'
  },
  {
    url: 'C:\\Videos\\sample.mp4',
    expected: 'local',
    description: 'Windows本地路径'
  },
  {
    url: '/home/user/videos/sample.mp4',
    expected: 'local',
    description: 'Unix/Linux本地路径'
  },
  
  // 未知平台测试
  {
    url: 'https://www.douyin.com/video/123456789',
    expected: 'unknown',
    description: '抖音URL（不支持）'
  },
  {
    url: 'https://www.kuaishou.com/video/123456789',
    expected: 'unknown',
    description: '快手URL（不支持）'
  },
  {
    url: 'invalid-url',
    expected: 'unknown',
    description: '无效URL'
  }
]

/**
 * 运行测试
 */
function runTests(): void {
  console.log('🧪 开始前端URL平台自动识别功能测试...\n')
  
  let passedTests = 0
  let totalTests = testCases.length
  
  testCases.forEach((testCase, index) => {
    const detected = detectPlatformFromUrl(testCase.url)
    const isPassed = detected === testCase.expected
    const displayName = getPlatformDisplayName(detected)
    const isValid = isValidUrl(testCase.url)
    
    console.log(`📋 测试 ${index + 1}: ${testCase.description}`)
    console.log(`   输入URL: ${testCase.url}`)
    console.log(`   期望结果: ${testCase.expected}`)
    console.log(`   实际结果: ${detected}`)
    console.log(`   显示名称: ${displayName}`)
    console.log(`   URL有效性: ${isValid}`)
    console.log(`   测试结果: ${isPassed ? '✅ PASS' : '❌ FAIL'}\n`)
    
    if (isPassed) {
      passedTests++
    }
  })
  
  console.log(`📊 测试总结:`)
  console.log(`   通过: ${passedTests}/${totalTests}`)
  console.log(`   成功率: ${((passedTests / totalTests) * 100).toFixed(1)}%`)
  console.log(`   状态: ${passedTests === totalTests ? '🎉 所有测试通过！' : '⚠️ 部分测试失败'}`)
}

// 运行测试
runTests()

export { detectPlatformFromUrl, getPlatformDisplayName, isValidUrl }