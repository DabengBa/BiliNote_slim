# [移除非核心下载器]：251110-remove-unsupported-downloaders技术规格与任务分解
> **最后更新**: 2025-11-10

## 1. Observation (全局洞察)

- **后端仍保留 Douyin/Kuaishou 下载器及 `douyin_helper`、`kuaishou_helper` 目录，复杂依赖持续拖累维护成本并暴露外部 API 风险。**
- **`backend/app/services` 与 `app/validators/video_url_validator.py` 依旧将抖音/快手标记为可用平台，若直接删除实现将产生导入/运行期错误。**
- **前端 (如 `BillNote_frontend/src/constant/note.ts`) 仍显示抖音、快手、小宇宙选项，用户体验与当前能力不匹配且缺少即时告警。**
- **缺少覆盖“未支持平台”场景的自动化测试，验收标准 1 和 5 无法被回归验证。**

## 2. Scope & Goal (任务理解)

- **目标**: 精简下载链路，确保系统仅支持 Bilibili/YouTube/本地上传，并在 UI 与 API 层面提供明确的“平台不受支持”反馈。
- **范围**: 后端下载器、URL 校验器、服务注册、错误返回、前端常量/表单、面向开发者的文档及环境变量示例。
- **排除项**: 不调整 yt-dlp 核心逻辑、不改动 Bilibili 与 YouTube 的下载实现、不处理音频转录器中的快手方案（待额外决策）。

## 3. Existing Assets (现状盘点)

- **下载器注册常量**: `backend/app/services/constant.py`
  - **功能**: 维护平台到下载器实例的映射，被 `note.py` 等服务用于分发下载流程。
  - **限制**: 仍实例化 `DouyinDownloader`、`KuaiShouDownloader`，删除实现会触发导入错误。
- **URL 校验器**: `backend/app/validators/video_url_validator.py`
  - **功能**: 依据 `SUPPORTED_PLATFORMS` 与平台特征正则判断链接合法性。
  - **限制**: 当前仍将 `douyin`、`kuaishou` 判定为支持并在解析阶段特殊处理。
- **前端平台常量**: `BillNote_frontend/src/constant/note.ts`
  - **功能**: 定义前端可选平台/图标，被表单、下拉组件复用。
  - **限制**: 展示了已决定弃用的平台，且缺少统一错误提示配置。

## 4. Risks & Dependencies (风险与依赖)

| 风险描述 | 可能性 | 影响 | 缓解措施 |
|---|---|---|---|
| 删除下载器文件后遗漏 `app/services/note.py`、`app/services/constant.py`、`app/utils` 等引用导致运行时报 ImportError | 中 | 高 | 使用 `rg "(douyin|kuaishou|xiaoyuzhou)" -n` 生成基线并在 PR 中逐项勾除；新增 CI 检查阻止残留命名。 |
| 仍有配置/文档提及 `kuaishou` (如 `.env.example`, `AGENTS.MD`, transcriber 配置)，导致新成员误解能力范围 | 高 | 中 | 在文档阶段集中清理并同步更新 `AGENTS.MD`、环境变量样例，添加 Changelog。 |
| 前端未能及时展示“平台不支持”提示，导致用户重复提交无效任务 | 中 | 中 | 在前端校验层即时阻断，并为 API 错误消息编写单测/Story 复现。 |

## 5. Task List (任务列表)

### 阶段 0: 准备工作
- [ ] T001 [调研] 使用 `rg "(douyin|kuaishou|xiaoyuzhou)" -n` 列出所有后端/前端引用并记录影响面 —— **产出**: `docs/specs/251110-remove-unsupported-downloaders/impact-analysis.md`。
- [ ] T002 [环境] 搭建/验证 backend venv 与 frontend pnpm 环境，确保可运行 `pytest` 与 `pnpm lint` —— **验证**: 后端 `pytest -q`、前端 `pnpm lint`。

### 阶段 1: 后端清理
- [ ] T010 [后端] 删除 `backend/app/downloaders/douyin_downloader.py` 与 `backend/app/downloaders/douyin_helper/`，并移除相关配置读取逻辑 —— **产出**: 彻底移除文件；**验证**: `rg douyin backend/app/downloaders` 无匹配。
- [ ] T011 [后端] 删除 `backend/app/downloaders/kuaishou_downloader.py` 与 `backend/app/downloaders/kuaishou_helper/`，清理依赖 —— **产出**: 文件移除；**验证**: `rg kuaishou backend/app/downloaders` 无匹配。
- [ ] T012 [后端] 删除 `backend/app/downloaders/xiaoyuzhoufm_download.py` 占位及任何引用 —— **产出**: 文件删除；**验证**: `rg xiaoyuzhou` 空结果。
- [ ] T013 [后端] 更新 `backend/app/services/constant.py`、`backend/app/services/note.py` 及相关导入，改为对非白名单平台抛出业务异常 —— **验证**: `pytest app/tests/test_note_service.py::test_reject_unsupported_platform`。
- [ ] T014 [后端] 调整 `backend/app/validators/video_url_validator.py`、`backend/app/utils/url_parser.py`、`backend/app/utils/note_helper.py`，仅允许核心平台并返回统一错误 —— **验证**: `pytest app/tests/test_video_url_validator.py::test_supported_platforms`。
- [ ] T015 [后端] 在 `/api/note/generate` 路由增加 4xx 错误响应及结构化错误码，覆盖抖音/快手输入 —— **验证**: `pytest app/tests/test_note_router.py::test_generate_rejects_douyin`。

### 阶段 2: 前端 & 交互
- [ ] T020 [前端] 移除 `BillNote_frontend/src/constant/note.ts`、`src/components/Form/*` 中抖音/快手/小宇宙条目与资源文件 —— **验证**: `pnpm lint && pnpm typecheck`。
- [ ] T021 [前端] 在链接输入校验与错误提示组件中捕获“平台不支持”状态码，展示与验收标准一致的提示语 —— **验证**: `pnpm test note-form` 或 Storybook 手动验证记录。
- [ ] T022 [前端] 清理未使用的 Logo/Lottie 资源，避免打包残留 —— **验证**: `pnpm build` 通过且 bundle analyzer 无相关资源。

### 阶段 3: 测试、文档与验收
- [ ] T030 [测试] 新增后端单测（validators & router）覆盖抖音/快手输入返回 4xx，确保回归 —— **产出**: `backend/tests/test_video_url_validator.py`, `backend/tests/test_note_router.py`。
- [ ] T031 [测试] 编写前端单测/Story 覆盖错误提示渲染，防止回退 —— **产出**: `BillNote_frontend/src/__tests__/note-form.spec.tsx`。
- [ ] T032 [文档] 更新 `AGENTS.MD`、`README.md`、`.env.example`、`docs/specs/251110-remove-unsupported-downloaders/prd.md` 相关段落，明确仅支持平台与错误提示规则 —— **验证**: 文档 MR 通过评审。
- [ ] T033 [发布] 在 Changelog 或 Release Note 中记录此次功能裁剪及对用户的影响范围 —— **产出**: `docs/changelog.md` 新条目。

## 6. Open Questions (待确认事项)

- [ ] 是否同步移除 `app/transcriber/kuaishou.py` 及相关枚举，抑或保留供未来音频服务复用？
- [ ] 抖音/快手 logo 资产未来是否保留在品牌库以备市场宣传？若需保留，应迁移到单独位置防止被误用。
- [ ] 前端“平台不支持”提示是否需要多语言或可配置化，以便后续国际化版本引用？
- [ ] `.env.example` 中 `TRANSCRIBER_TYPE` 是否继续列出 `kuaishou` 选项，还是统一改为文档备注？
