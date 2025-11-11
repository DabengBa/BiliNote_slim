# 移除非核心下载器影响分析

> **生成时间**: 2025-11-11
> **扫描命令**: `rg -n "(douyin|kuaishou|tiktok|xiaoyuzhou)" --ignore-case`

## 执行摘要

本次扫描共发现 **54 处** 相关引用，涉及 4 个主要领域：
- **后端代码**: 30 处引用（下载器、URL验证器、服务层、工具类、转录器）
- **前端代码**: 6 处引用（常量、图标、表单组件）
- **配置文档**: 7 处引用（环境变量、README、AGENTS文档）
- **项目文档**: 11 处引用（规格文档、PRD）

## 详细影响分析

### 一、后端模块 (30处)

#### 1. 下载器模块 (13处)
| 文件路径 | 引用类型 | 处理策略 |
|---------|---------|---------|
| `backend/app/downloaders/douyin_downloader.py` | 核心下载器 | **完全删除** |
| `backend/app/downloaders/douyin_helper/` | 辅助模块 | **完全删除** |
| `backend/app/downloaders/douyin_helper/abogus.py` | 加密参数生成 | **完全删除** |
| `backend/app/downloaders/kuaishou_downloader.py` | 核心下载器 | **完全删除** |
| `backend/app/downloaders/kuaishou_helper/` | 辅助模块 | **完全删除** |
| `backend/app/downloaders/kuaishou_helper/kuaishou.py` | 快手API封装 | **完全删除** |
| `backend/app/downloaders/xiaoyuzhoufm_download.py` | 占位实现 | **完全删除** |
| `backend/app/downloaders/__init__.py` | 导出声明 | **清理引用** |

**删除前检查**: 确认这些文件确实存在且包含相关代码

#### 2. 服务层 (3处)
| 文件路径 | 引用类型 | 处理策略 |
|---------|---------|---------|
| `backend/app/services/constant.py:2-3` | Import语句 | **移除导入** |
| `backend/app/services/constant.py:10-12` | 平台映射 | **精简映射** |
| `backend/app/services/note.py:15` | Import语句 | **移除导入** |

**影响**: 需更新 `SUPPORT_PLATFORM_MAP` 常量，删除 douyin/tiktok/kuaishou 键

#### 3. 验证与解析 (4处)
| 文件路径 | 引用类型 | 处理策略 |
|---------|---------|---------|
| `backend/app/validators/video_url_validator.py:8-9,21` | 平台枚举 | **精简白名单** |
| `backend/app/utils/url_parser.py:11,30-31` | URL解析分支 | **删除分支** |
| `backend/app/utils/note_helper.py:24-25` | 内容标记替换 | **删除逻辑** |

**影响**: 需更新URL验证正则，删除非核心平台支持

#### 4. 转录器 (10处)
| 文件路径 | 引用类型 | 处理策略 |
|---------|---------|---------|
| `backend/app/transcriber/kuaishou.py` | 转录器实现 | **待定策略** |
| `backend/app/transcriber/transcriber_provider.py:8,17,37,63-64,78,107-108` | 转录提供者 | **待定策略** |

**影响**: 任务文档中标记为"待确认事项"，需产品决策

### 二、前端模块 (6处)

#### 1. 常量与资源 (3处)
| 文件路径 | 引用类型 | 处理策略 |
|---------|---------|---------|
| `BillNote_frontend/src/constant/note.ts:4-5,32-33` | 平台常量 | **删除条目** |
| `BillNote_frontend/src/components/Icons/platform.tsx:1,31` | 平台图标 | **删除组件** |

#### 2. 表单组件 (3处)
| 文件路径 | 引用类型 | 处理策略 |
|---------|---------|---------|
| `BillNote_frontend/src/components/Form/DownloaderForm/Options.tsx:5` | 图标引用 | **删除引用** |

### 三、配置与文档 (18处)

#### 1. 环境配置 (3处)
| 文件路径 | 引用类型 | 处理策略 |
|---------|---------|---------|
| `.env.example:21` | TRANSCRIBER_TYPE | **清理选项** |
| `backend/.env.example:11` | TRANSCRIBER_TYPE | **清理选项** |

#### 2. 项目文档 (3处)
| 文件路径 | 引用类型 | 处理策略 |
|---------|---------|---------|
| `README.md:129` | 致谢声明 | **保留致谢** |
| `AGENTS.md:14,48-49,165` | 代理说明 | **清理描述** |

#### 3. 规格文档 (12处)
| 文件路径 | 引用类型 | 处理策略 |
|---------|---------|---------|
| `docs/specs/251110-remove-unsupported-downloaders/*` | 任务/PRD文档 | **更新标记** |

## 风险评估

### 高风险项 ⚠️
1. **运行期导入错误**: `constant.py` 和 `note.py` 的导入语句如未清理将导致 `ImportError`
2. **转录器残留**: `transcriber_provider.py` 中多处引用需谨慎处理

### 中风险项 ⚡
1. **文档不一致**: 多个文档提及已删除功能需同步更新
2. **前端构建**: 图标资源删除可能影响构建（如被Tree-shaking忽略则无影响）

### 低风险项 ✓
1. **环境变量**: `.env.example` 为样例文件，不影响运行时
2. **致谢声明**: README中的致谢可保留

## 实施建议

### 分阶段清理
1. **阶段1**: 优先处理后端下载器文件（自动可验证）
2. **阶段2**: 同步更新服务层和验证器（需代码审查）
3. **阶段3**: 清理前端资源（影响UI）
4. **阶段4**: 更新文档（易遗漏）

### 验证机制
- 每个子任务完成后执行 `rg douyin|kuaishou` 验证无残留
- 前后端分别运行 lint 和 test 验证
- 手动测试核心下载流程（B站/YouTube）

## 待确认事项

1. **转录器 kuaishou.py**: 是否保留供未来音频服务复用？
2. **环境变量**: TRANSCRIBER_TYPE 中是否移除 kuaishou 选项？
3. **致谢声明**: README.md 中的致谢是否需要调整？

## 结论

本次影响分析为后续清理工作提供了全面的参考。建议按照风险等级优先处理高风险项，并确保每个阶段完成后进行充分验证。
