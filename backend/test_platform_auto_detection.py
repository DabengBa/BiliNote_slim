#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试URL平台自动识别功能
"""

import requests
import json

def test_platform_auto_detection():
    """测试不带platform字段的自动检测功能"""
    
    # 测试数据 - 不包含platform字段，应该自动检测
    test_data = {
        "video_url": "https://www.bilibili.com/video/BV1xx411c7m8",
        "quality": "fast",
        "model_name": "test_model",
        "provider_id": "test_provider"
    }
    
    url = "http://localhost:8000/api/generate_note"
    
    print("🔍 测试平台自动识别功能...")
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=test_data, headers={"Content-Type": "application/json"})
        print(f"\n📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容:")
        
        response_data = response.json()
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print("\n✅ 平台自动检测功能正常工作!")
            if "task_id" in response_data.get("data", {}):
                print(f"🎯 成功获取任务ID: {response_data['data']['task_id']}")
        else:
            print(f"\n❌ 请求失败，错误详情: {response_data}")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

def test_backward_compatibility():
    """测试向后兼容性 - 带platform字段"""
    
    # 测试数据 - 包含platform字段，应该使用用户提供的值
    test_data = {
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "platform": "youtube",  # 显式指定平台
        "quality": "medium",
        "model_name": "test_model",
        "provider_id": "test_provider"
    }
    
    url = "http://localhost:8000/api/generate_note"
    
    print("\n🔄 测试向后兼容性...")
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=test_data, headers={"Content-Type": "application/json"})
        print(f"\n📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容:")
        
        response_data = response.json()
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print("\n✅ 向后兼容性正常!")
            if "task_id" in response_data.get("data", {}):
                print(f"🎯 成功获取任务ID: {response_data['data']['task_id']}")
        else:
            print(f"\n❌ 请求失败，错误详情: {response_data}")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

def test_unsupported_platform():
    """测试不支持的平台"""
    
    # 测试数据 - 使用不支持的平台
    test_data = {
        "video_url": "https://www.tiktok.com/@example/video/123456789",
        "quality": "fast",
        "model_name": "test_model",
        "provider_id": "test_provider"
    }
    
    url = "http://localhost:8000/api/generate_note"
    
    print("\n🚫 测试不支持的平台...")
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=test_data, headers={"Content-Type": "application/json"})
        print(f"\n📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容:")
        
        response_data = response.json()
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        if response.status_code != 200:
            print("\n✅ 正确检测到不支持的平台!")
        else:
            print(f"\n❌ 应该返回错误，但请求成功了")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    print("🚀 开始测试URL平台自动识别功能\n")
    
    # 1. 测试自动检测
    test_platform_auto_detection()
    
    # 2. 测试向后兼容性
    test_backward_compatibility()
    
    # 3. 测试不支持的平台
    test_unsupported_platform()
    
    print("\n🏁 测试完成!")