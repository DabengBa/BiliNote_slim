# 更新日志 (Changelog)

本文件记录 BiliNote 项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中
- 笔记导出为 PDF / Word / Notion

---

## [1.9.0] - 2025-11-11

### 🚀 新增功能
- 增强的URL验证：三层验证机制（协议检查、域名白名单、关键词黑名单）
- 改进的错误处理：统一API错误格式，错误代码300101
- 即时前端验证：实时拦截不支持平台的视频链接

### 🔧 改进
- 优化的用户界面：移除不必要平台选项，界面更简洁
- 改进的测试覆盖率：17个后端测试，14个前端验证测试
- 更好的错误提示：用户友好的错误信息展示
- 增强的转录器管理：统一转录器类型管理

### ❌ 移除功能 (Breaking Changes)
- **移除抖音 (Douyin) 下载支持**
  - 移除 `DouyinDownloader` 及所有相关代码
  - 移除 douyin 相关的URL验证和跳转逻辑

- **移除快手 (Kuaishou) 下载支持**
  - 移除 `KuaishouDownloader` 及所有相关代码
  - 移除 `KuaishouTranscriber` 转录器实现
  - 从环境变量 `TRANSCRIBER_TYPE` 中移除 kuaishou 选项

- **移除小宇宙FM (Xiaoyuzhou) 下载支持**
  - 移除占位文件和相关引用
  - 清理未实现功能的代码

### 🧪 测试
- **新增测试文件**:
  - `tests/test_video_url_validator.py`: 7个URL验证测试用例
  - `tests/test_note_service.py`: 5个平台验证测试用例
  - `tests/test_note_router.py`: 5个API错误处理测试用例

- **测试覆盖率**:
  - 后端：17/17 测试通过 (100%)
  - 前端：14/14 验证测试通过 (100%)

### 📚 文档更新
- 更新 `README.md`：移除已移除平台的描述
- 更新 `AGENTS.md`：更新技术栈和架构文档
- 更新 `.env.example`：移除快手转录器选项
- 更新 `backend/.env.example`：移除快手转录器选项
- 更新 `prd.md`：标记所有验收标准为已完成
- 新增 `docs/specs/251110-remove-unsupported-downloaders/` 任务规范文档

### 🔒 破坏性变更 (Breaking Changes)
- **支持的视频平台**: 仅保留 Bilibili、YouTube、本地视频
- **转录器类型**: 仅支持 fast-whisper、mlx-whisper、bcut、groq
- **API错误格式**: 统一为 `{"code": 300101, "msg": "...", "data": null}`

### 🐛 修复
- 修复前端无法识别 `PLATFORM_NOT_SUPPORTED` 错误码的问题
- 修复 API 错误格式不一致的问题 (422状态码 + 业务错误码)
- 修复前端缺少即时验证导致后端报错的问题
- 修复 pytest 等测试依赖未包含在 requirements.txt 的问题
- 修复 ctranslate2 版本兼容性问题 (升级至 4.6.0)

### 🏗️ 代码质量
- **遵循设计原则**:
  - SOLID: 单一职责、开闭原则
  - KISS: 简化转录器管理
  - DRY: 统一的验证和错误处理
  - YAGNI: 移除不需要的功能

- **代码清理**:
  - 删除2个下载器文件和2个辅助目录
  - 清理54处代码引用
  - 移除未使用的转录器实现

### 📋 技术债务
- 移除了依赖不稳定第三方API的功能
- 清理了未实现的占位功能
- 统一了错误处理和验证逻辑

### 👥 贡献者
- 本次变更由开发团队完成

### 📝 升级指南

#### 对开发者
1. **更新环境变量**:
   ```bash
   # 从 .env.example 重新生成 .env
   # 移除 kuaishou 转录器类型配置
   ```

2. **更新测试环境**:
   ```bash
   pip install -r backend/requirements.txt  # 包含测试依赖
   pytest tests/                           # 验证测试通过
   ```

3. **清理代码**:
   - 移除任何对已移除平台的引用
   - 更新API调用和错误处理

#### 对用户
1. **支持的平台**:
   - ✅ 哔哩哔哩 (Bilibili)
   - ✅ YouTube
   - ✅ 本地视频文件

2. **不支持的平台** (如尝试使用将收到友好错误提示):
   - ❌ 抖音 (Douyin)
   - ❌ 快手 (Kuaishou)
   - ❌ 小宇宙FM (Xiaoyuzhou)

### 🔗 相关链接
- 项目文档: [https://docs.bilinote.app/](https://docs.bilinote.app/)
- 体验地址: [https://www.bilinote.app/](https://www.bilinote.app/)
- 源码仓库: [https://github.com/JefferyHcool/BiliNote](https://github.com/JefferyHcool/BiliNote)

### 📊 统计信息
- **文件修改**: 15+ 文件
- **代码行数**: +50/-500 (净删除约450行)
- **测试用例**: 17个后端测试 + 14个前端验证
- **文档文件**: 6个文档更新 + 1个新文档

---

## [1.8.1] - 2024-12-XX

### 🔧 改进
- 优化转录质量
- 改进用户界面

### 🐛 修复
- 修复各种Bug

---

## 格式说明

### 版本号格式
- **主版本号 (MAJOR)**: 包含破坏性变更
- **次版本号 (MINOR)**: 新增功能，向下兼容
- **修订号 (PATCH)**: 修复问题，向下兼容

### 变更类型
- **新增功能 (Added)**: 新功能
- **改进 (Changed)**: 对现有功能的变更
- **移除功能 (Removed)**: 已删除的功能
- **修复 (Fixed)**: 任何问题的修复
- **安全 (Security)**: 安全相关修复

### 特殊标记
- **🚀**: 新功能
- **🔧**: 改进
- **❌**: 移除功能
- **🧪**: 测试
- **📚**: 文档
- **🔒**: 破坏性变更
- **🐛**: 修复
- **🏗️**: 代码质量
- **👥**: 贡献者
- **📝**: 升级指南
- **🔗**: 相关链接
- **📊**: 统计信息

---

💬 **你的支持与反馈是我持续优化的动力！** 欢迎 [PR](https://github.com/JefferyHcool/BiliNote/pulls)、[提 issue](https://github.com/JefferyHcool/BiliNote/issues)、⭐️ [Star](https://github.com/JefferyHcool/BiliNote)
