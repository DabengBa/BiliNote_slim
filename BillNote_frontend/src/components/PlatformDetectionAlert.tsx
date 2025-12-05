/**
 * 平台检测失败提示组件
 * 当URL无法自动识别时显示，提供手动选择平台的选项
 */

import { useState, useEffect } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { AlertTriangle, Settings, CheckCircle } from 'lucide-react'
import { detectPlatformFromUrl, getPlatformDisplayName } from '@/utils/urlUtils'
import { videoPlatforms } from '@/constant/note'

interface PlatformDetectionAlertProps {
  url: string
  detectedPlatform?: string
  onPlatformSelect?: (platform: string) => void
  onDismiss?: () => void
  className?: string
}

/**
 * 平台检测失败提示组件
 */
const PlatformDetectionAlert: React.FC<PlatformDetectionAlertProps> = ({
  url,
  detectedPlatform = 'unknown',
  onPlatformSelect,
  onDismiss,
  className = ''
}) => {
  const [selectedPlatform, setSelectedPlatform] = useState('')
  const [hasManuallySelected, setHasManuallySelected] = useState(false)
  const [isVisible, setIsVisible] = useState(true)

  // 检查URL是否真的无法识别
  const actualPlatform = detectPlatformFromUrl(url)
  const isDetectionFailed = actualPlatform === 'unknown' && url.trim() !== ''

  // 如果URL能正常识别，不显示提示
  if (!isDetectionFailed) {
    return null
  }

  const handlePlatformSelect = (platform: string) => {
    setSelectedPlatform(platform)
    setHasManuallySelected(true)
    
    if (onPlatformSelect) {
      onPlatformSelect(platform)
    }
  }

  const handleDismiss = () => {
    setIsVisible(false)
    if (onDismiss) {
      onDismiss()
    }
  }

  const handleConfirmSelection = () => {
    if (selectedPlatform && onPlatformSelect) {
      onPlatformSelect(selectedPlatform)
    }
    handleDismiss()
  }

  if (!isVisible) {
    return null
  }

  return (
    <Alert className={`border-amber-200 bg-amber-50 ${className}`}>
      <AlertTriangle className="h-4 w-4 text-amber-600" />
      <div className="ml-2 flex-1">
        <AlertDescription className="text-amber-800">
          <div className="mb-3">
            <strong>无法自动识别视频平台</strong>
          </div>
          
          <div className="mb-3 text-sm text-amber-700">
            URL: <code className="bg-amber-100 px-1 py-0.5 rounded text-xs break-all">{url}</code>
          </div>

          {!hasManuallySelected ? (
            <div className="space-y-3">
              <p className="text-sm text-amber-700">
                请手动选择对应的视频平台：
              </p>
              
              <Select onValueChange={handlePlatformSelect}>
                <SelectTrigger className="w-full bg-white border-amber-300">
                  <SelectValue placeholder="选择视频平台" />
                </SelectTrigger>
                <SelectContent>
                  {videoPlatforms.map((platform) => (
                    <SelectItem key={platform.value} value={platform.value}>
                      <div className="flex items-center gap-2">
                        <div className="h-4 w-4">{platform.logo()}</div>
                        <span>{platform.label}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-green-700">
                <CheckCircle className="h-4 w-4" />
                已选择平台: <strong>{getPlatformDisplayName(selectedPlatform as any)}</strong>
              </div>
              
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={handleConfirmSelection}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  确认选择
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setHasManuallySelected(false)
                    setSelectedPlatform('')
                  }}
                  className="border-amber-300 text-amber-700 hover:bg-amber-100"
                >
                  重新选择
                </Button>
              </div>
            </div>
          )}

          <div className="mt-3 pt-2 border-t border-amber-200">
            <Button
              size="sm"
              variant="ghost"
              onClick={handleDismiss}
              className="h-auto p-0 text-xs text-amber-600 hover:text-amber-800 hover:bg-transparent"
            >
              知道了
            </Button>
          </div>
        </AlertDescription>
      </div>
    </Alert>
  )
}

export default PlatformDetectionAlert