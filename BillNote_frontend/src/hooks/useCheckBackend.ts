import { useEffect, useState } from 'react'
import request from '@/utils/request'

const MAX_RETRIES = 3
const RETRY_INTERVAL = 10000 // 10秒

export const useCheckBackend = () => {
  const [loading, setLoading] = useState(false)
  const [initialized, setInitialized] = useState(false)

  useEffect(() => {
    let retries = 0

    const check = async () => {
      try {
        console.log('尝试访问/sys_check接口...');
        const response = await request.get('/sys_check');
        console.log('/sys_check接口请求成功:', response);
        setInitialized(true);
        setLoading(false);
      } catch (error) {
        console.error('/sys_check接口请求失败:', error);
        if (retries === 0) {
          // 第一次失败时开始显示加载状态
          setLoading(true);
        }

        if (retries < MAX_RETRIES) {
          retries++;
          console.log(`重试次数: ${retries}/${MAX_RETRIES}`);
          setTimeout(check, RETRY_INTERVAL);
        } else {
          // 达到重试上限，继续轮询直到后端就绪
          waitUntilBackendReady();
        }
      }
    }

    const waitUntilBackendReady = async () => {
      console.log('开始轮询/sys_health接口...');
      while (true) {
        try {
          const response = await request.get('/sys_health');
          console.log('/sys_health接口请求成功:', response);
          setInitialized(true);
          setLoading(false);
          break;
        } catch (error) {
          console.error('/sys_health接口请求失败:', error);
          await new Promise(res => setTimeout(res, RETRY_INTERVAL));
        }
      }
    }

    check()
  }, [])

  return { loading, initialized }
}