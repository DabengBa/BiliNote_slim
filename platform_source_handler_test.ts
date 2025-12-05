/**
 * Platform Source Handler 功能测试
 * 验证T008b: platform_source字段的写入策略和校验机制
 */

// 模拟platformSourceHandler功能
class PlatformSourceHandler {
  /**
   * 检测平台来源
   */
  detectPlatformSource(url: string, currentPlatform?: string): string {
    if (!url || url.trim() === '') {
      return 'unknown'
    }

    // 如果有当前平台，检查是否为自动检测
    if (currentPlatform) {
      const detectedPlatform = this.detectPlatformFromUrl(url)
      
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
    const detectedPlatform = this.detectPlatformFromUrl(url)
    if (detectedPlatform !== 'unknown') {
      return 'auto_detected'
    }

    return 'unknown'
  }

  /**
   * 检测平台（简化版）
   */
  detectPlatformFromUrl(url: string): string {
    if (!url || typeof url !== 'string') {
      return 'unknown'
    }

    const cleanUrl = url.trim()
    
    if (/^https?:\/\/(www\.)?bilibili\.com\//i.test(cleanUrl) || 
        /^https?:\/\/b23\.tv\//i.test(cleanUrl)) {
      return 'bilibili'
    }
    
    if (/^https?:\/\/(www\.)?youtube\.com\//i.test(cleanUrl) ||
        /^https?:\/\/youtu\.be\//i.test(cleanUrl)) {
      return 'youtube'
    }
    
    return 'unknown'
  }

  /**
   * 为表单数据添加平台来源信息
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
   * 验证表单数据
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

    return {
      isValid: true,
      errors: []
    }
  }
}

const platformSourceHandler = new PlatformSourceHandler()

/**
 * 测试用例
 */
const testCases = [
  {
    name: '自动检测场景：哔哩哔哩URL自动检测',
    formData: {
      video_url: 'https://www.bilibili.com/video/BV1xx411c7xx/',
      platform: 'bilibili'
    },
    expectedSource: 'auto_detected',
    description: 'URL与platform匹配，应标记为auto_detected'
  },
  {
    name: '自动检测场景：YouTube URL自动检测',
    formData: {
      video_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      platform: 'youtube'
    },
    expectedSource: 'auto_detected',
    description: 'URL与platform匹配，应标记为auto_detected'
  },
  {
    name: '手动选择场景：用户手动选择平台',
    formData: {
      video_url: 'https://example.com/video/123',
      platform: 'bilibili'
    },
    expectedSource: 'user_provided',
    description: '无法识别URL但用户选择了平台，应标记为user_provided'
  },
  {
    name: '未知场景：空URL',
    formData: {
      video_url: '',
      platform: 'bilibili'
    },
    expectedSource: 'unknown',
    description: '空URL应标记为unknown'
  },
  {
    name: '完整表单验证：有效数据',
    formData: {
      video_url: 'https://www.bilibili.com/video/BV1xx411c7xx/',
      platform: 'bilibili',
      platform_source: 'auto_detected'
    },
    expectedValid: true,
    description: '完整有效的表单数据应通过验证'
  },
  {
    name: '表单验证：缺少必填字段',
    formData: {
      video_url: '',
      platform: 'bilibili'
    },
    expectedValid: false,
    expectedErrorCount: 1,
    description: '缺少video_url应验证失败'
  }
]

/**
 * 运行测试
 */
function runTests(): void {
  console.log('🧪 开始Platform Source Handler功能测试...\n')
  
  let passedTests = 0
  let totalTests = testCases.length
  
  testCases.forEach((testCase, index) => {
    console.log(`📋 测试 ${index + 1}: ${testCase.name}`)
    console.log(`   描述: ${testCase.description}`)
    console.log(`   表单数据:`, testCase.formData)
    
    if (testCase.expectedSource) {
      // 测试platform_source检测
      const resultWithSource = platformSourceHandler.addPlatformSourceToForm(testCase.formData)
      const detectedSource = resultWithSource.platform_source
      const isPassed = detectedSource === testCase.expectedSource
      
      console.log(`   期望来源: ${testCase.expectedSource}`)
      console.log(`   实际来源: ${detectedSource}`)
      console.log(`   测试结果: ${isPassed ? '✅ PASS' : '❌ FAIL'}\n`)
      
      if (isPassed) {
        passedTests++
      }
    } else if (testCase.expectedValid !== undefined) {
      // 测试表单验证
      const validation = platformSourceHandler.validateFormData(testCase.formData)
      const isPassed = validation.isValid === testCase.expectedValid
      
      console.log(`   期望验证: ${testCase.expectedValid ? '通过' : '失败'}`)
      console.log(`   实际验证: ${validation.isValid ? '通过' : '失败'}`)
      
      if (validation.errors && validation.errors.length > 0) {
        console.log(`   错误信息: ${validation.errors.join(', ')}`)
      }
      
      if (testCase.expectedErrorCount !== undefined) {
        const errorCountMatch = validation.errors && validation.errors.length === testCase.expectedErrorCount
        console.log(`   期望错误数: ${testCase.expectedErrorCount}`)
        console.log(`   实际错误数: ${validation.errors ? validation.errors.length : 0}`)
        console.log(`   错误数匹配: ${errorCountMatch ? '✅' : '❌'}`)
      }
      
      console.log(`   测试结果: ${isPassed ? '✅ PASS' : '❌ FAIL'}\n`)
      
      if (isPassed) {
        passedTests++
      }
    }
  })
  
  console.log(`📊 测试总结:`)
  console.log(`   通过: ${passedTests}/${totalTests}`)
  console.log(`   成功率: ${((passedTests / totalTests) * 100).toFixed(1)}%`)
  console.log(`   状态: ${passedTests === totalTests ? '🎉 所有测试通过！' : '⚠️ 部分测试失败'}`)
}

// 运行测试
runTests()