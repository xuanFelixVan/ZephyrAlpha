---
module_id: ADR-0007
title: 前端层不进 src/ 15 层，作为独立 frontend/ 平台层
doc_type: adr
status: active
version: 1.1.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-18
superseded_by: null
supersedes: null
related_rationale:
- R29
- R30
- R64
related_open_questions:
- OQ-043
tags:
- adr
- frontend
- platform
- react
- typescript
- monorepo
- api-gateway
- microfrontend
summary: 决定前端代码不进入 Python 后端的 src/zephyr/ 15 层架构，而是作为独立的 frontend/ 顶级目录（与 src/ 平级）。对标
  Bloomberg Terminal / Refinitiv Workspace Platform / QuantConnect Lean+Cloud / Interactive
  Brokers TWS 四家机构的共性模式。Python 后端 15 层保持不变，前端 TypeScript/React 完全异构隔离。**2026-04-19
  批次 H 追溯性从 ADR-DRAFT-0007 升格为 accepted**，同步新建 `10-frontend-architecture.md` 作为本 ADR
  的视图承载文件（R64）。
date: '2026-04-22'
ttl: permanent
---

# ADR-0007：前端层不进 src/ 15 层，作为独立 frontend/ 平台层

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-18（作为 ADR-DRAFT-0007 起草）
- **拍板日期**：2026-04-18（OQ-043 会话 10 由用户拍板，方案 D 选定）
- **升格日期**：2026-04-19（批次 H 追溯性从 `adr-drafts/` 搬至 `adr/`，status `proposed` → `accepted`，对应视图 `10-frontend-architecture.md` v1.0.0 同步落盘）
- **被谁取代**：无
- **取代了谁**：无（新能力，OQ-043 首次定义）

## 2. 上下文（Context）

### 2.1 问题起源

V1 技术仓库 §4368/§9468 明确前端技术栈（React / Vite / Ant Design），但当前 15 层架构（L00-L13 + shared）和 5 份差距分析 PDF **全部遗漏前端层**。OQ-043 在会话 09 确认为真盲点。

### 2.2 影响范围

所有 human-facing 功能均无归属层定义：

| 功能模块 | 当前候选层 | 问题 |
|---------|----------|------|
| Strategy IDE | L05 signal_generation | 代码编辑器是前端，与 Python 信号引擎混杂 |
| Backtest UI | L05 | 可视化图表是前端，回测引擎是后端 |
| Risk Dashboard | L07 risk_management | 前端仪表盘与风险计算引擎混杂 |
| Agent Conversation | L08 human_ai_interface | 聊天界面是前端，NLU 引擎是后端 |
| Monitoring Dashboard | L12 system_telemetry | Grafana 类面板是前端，遥测采集是后端 |

### 2.3 技术栈异构约束

| 维度 | Python 后端（src/zephyr/） | TypeScript 前端 |
|-----|--------------------------|----------------|
| 语言 | Python 3.11+ | TypeScript 5.x |
| 包管理 | uv / pip | pnpm |
| 构建工具 | setuptools / pyproject.toml | Vite |
| 发布 | PyPI / Docker | CDN / S3 静态文件 |
| 测试 | pytest | Vitest + Playwright |
| Lint | ruff / mypy | ESLint + Prettier |

将 TypeScript 代码放入 Python monorepo 的任一层都会导致：构建系统冲突、CI 管线交叉污染、部署逻辑分裂。

## 3. 候选方案

### 方案 A：新增 L14-UI 独立层（升级到 16 层）

- 在 `src/zephyr/l14_ui/` 下建立前端代码
- **否决理由**：TypeScript 不属于 Python monorepo；uv/pip 无法管理 npm 依赖；CI 需为 l14 单独建 Node.js 管线，违反 src/ 一致性原则

### 方案 B：扩展 shared/ui 共享子目录

- 在 `src/zephyr/shared/ui/` 下放前端组件
- **否决理由**：shared 定位是 Python 共享库（日志/配置/错误处理），混入 TypeScript 打破 shared 的语义；且 shared 无独立发布能力

### 方案 C：并入 L08 Human-AI Interface

- 所有 UI 统一放入 `src/zephyr/l08_human_ai_interface/web/`
- **否决理由**：L08 是 Agent 编排层，前端 5 个 App 的 40+ 路由远超 L08 职责；且对标机构无一将前端嵌入 Agent 层

### 方案 D：【推荐】前端作为独立 frontend/ 顶级目录

- 前端代码物理位置：`frontend/`（monorepo 顶层目录，与 `src/` 平级）
- 15 层 Python 架构保持不变
- 通过 API Gateway 与后端解耦

## 4. 决策（Decision）

**采用方案 D**。

### 4.1 对标依据

| 机构/产品 | 前端架构模式 | 与 ZephyrAlpha 对应 |
|----------|-----------|-------------------|
| **Bloomberg Terminal** | 独立 C++ 桌面客户端 + Web UI（Electron），完全独立于 BQuant Python 引擎 | 前端独立于计算后端 |
| **Refinitiv Workspace Platform** | Web Components 微前端架构，独立 npm monorepo，通过 REST/WS 与 Elektron 数据引擎通信 | monorepo 内部 apps/ + packages/ 分治 |
| **QuantConnect Lean + Cloud** | Lean（C# 回测引擎）与 Cloud IDE（React SPA）完全独立 repo，通过 API 对接 | 引擎与 IDE 物理隔离 |
| **Interactive Brokers TWS** | Java Swing 桌面端 + Web Trader（独立前端），通过 TWS API 与交易引擎通信 | API Gateway 作为分界 |

**共性模式**：前端从不进核心业务代码层 → API Gateway 是分界 → 前端独立构建/发布。

### 4.2 目录结构

```
ZephyrAlpha/
├── src/zephyr/             # Python 后端 15 层（不变）
│   ├── l00_data_source/
│   ├── ...
│   ├── l13_experiment_pipeline/
│   ├── shared/
│   └── l08_human_ai_interface/
│       └── api_gateway/    # 【新增子模块】FastAPI + WebSocket，前后端分界
│
├── frontend/               # 【新增顶级目录】TypeScript/React 前端平台
│   ├── platform/           # 微前端宿主 + 命令引擎 + 路由/权限/主题
│   ├── apps/               # 业务 App（每个 App 独立构建）
│   │   ├── strategy-ide/       # 策略编辑器
│   │   ├── backtest-ui/        # 回测可视化
│   │   ├── risk-dashboard/     # 风控仪表盘
│   │   ├── agent-chat/         # Agent 对话界面
│   │   ├── monitoring/         # 监控大屏
│   │   ├── portfolio-view/     # 组合管理
│   │   ├── factor-explorer/    # 因子浏览器
│   │   ├── data-dictionary/    # 数据字典检索
│   │   ├── oss-catalog/        # 开源组件目录
│   │   └── admin/              # 系统管理
│   ├── packages/           # 可复用组件包
│   │   ├── ui-kit/             # Ant Design 扩展组件库
│   │   ├── chart-engine/       # 金融图表引擎（TradingView 轻量图表 / D3）
│   │   ├── data-client/        # API 数据层（SWR/React Query + OpenAPI 自动生成）
│   │   ├── auth/               # 认证/权限 SDK
│   │   └── shared-types/       # 前后端共享 TypeScript 类型
│   ├── tools/              # 构建工具链
│   │   ├── vite-config/        # 统一 Vite 配置
│   │   ├── codegen/            # OpenAPI → TypeScript 代码生成
│   │   └── e2e/                # Playwright E2E 测试配置
│   ├── docs/               # 前端专属文档（组件规范、API 契约、上手指南）
│   ├── pnpm-workspace.yaml
│   ├── package.json
│   └── tsconfig.base.json
│
├── docs/                   # 文档架构（不变，新增第 10 视图）
├── scripts/                # 治理架构（不变）
└── .metadata/              # 元模型桥梁（ADR-0008 定义）
```

### 4.3 前后端对接规范

| 维度 | 规范 |
|-----|------|
| **API 协议** | REST（CRUD 操作）+ WebSocket（实时推送：行情、持仓、告警）|
| **Schema 契约** | OpenAPI 3.1 Spec，后端自动生成 → 前端 `codegen/` 自动消费 |
| **认证** | JWT（Bearer Token），L08 `api_gateway/` 统一签发 |
| **版本管理** | URL 路径版本 `/api/v1/`，重大不兼容变更 bump minor |
| **错误格式** | RFC 7807 Problem Details（type/title/status/detail/instance）|

### 4.4 文档视图

新增 `02_enterprise_architecture/target-architecture/10-frontend-architecture.md` 作为第 10 个 TOGAF 视图，专门描述前端平台的：

1. 微前端拓扑
2. 10 个 App 职责与路由
3. packages 复用矩阵
4. 构建/部署管线
5. 前后端 API 契约目录

### 4.5 治理规则

- 7 层文件治理的 L3（路径/命名）/ L4（Import-Linter）/ L5（Index 完整性）扩展覆盖 `frontend/`
- Import-Linter 类比：ESLint `no-restricted-imports` 规则禁止 apps 之间直接引用（必须通过 packages）
- 每个 App 的 `package.json` 必须声明 `peerDependencies` 指向 platform 版本

## 5. 后果（Consequences）

### 5.1 收益

- **技术栈隔离**：uv/pip 不污染 pnpm/vite，CI 管线独立
- **部署隔离**：前端 CDN 独立发布，后端 Docker 独立滚动，互不阻塞
- **对标一致**：Bloomberg/Refinitiv/QC/IBKR 四家共性模式
- **团队独立**：未来前端工程师无需理解 Python 15 层，只需对接 API Gateway

### 5.2 代价

- 新增 1 个顶级目录 `frontend/` 和 1 个 docs 视图（第 10 视图）
- API 契约维护成本（OpenAPI Spec 需后端同步更新）
- 前后端 shared-types 需手动或自动同步

### 5.3 派生 ADR

| ADR | 标题 | 时机 |
|-----|------|------|
| ADR-0007-A | API 契约规范（OpenAPI 版本策略 + 错误格式 + 认证流） | 前端 App-1 开发前 |
| ADR-0007-B | 前端治理扩展（ESLint 规则 + 微前端约束 + 共享包策略）| platform 骨架搭建后 |

## 6. 回滚条件（Rollback）

若 12 个月内前端工作量 < 2 人月且仅需 1-2 个简单页面，可降级为方案 C：将 UI 合并入 `l08_human_ai_interface/api_gateway/web/`，删除 `frontend/` 目录。

## 7. 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-18 | 1.0.0 | 初版（作为 `adr-drafts/ADR-DRAFT-0007`）。会话 10（Opus 47）OQ-043 专题讨论产出。对标四家机构，否决方案 A/B/C，选定方案 D。status `proposed`。 |
| 2026-04-19 | 1.1.0 | **追溯性升格为 accepted**（Retroactive Backfill，对标 Amazon "No Anonymous Decisions" + Google SRE Book 实践）：拍板日期仍为 2026-04-18（OQ-043 关闭日），升格日期为 2026-04-19（批次 H S14-Phase2-BatchH）。文件物理位置从 `adr-drafts/ADR-DRAFT-0007-frontend-platform.md` 搬至 `adr/adr-0007-frontend-platform.md`，草稿原件删除。module_id 从 `EA-ADR-DRAFT-0007` 改为 `ADR-0007`，status `proposed` → `accepted`，related_rationale 追加 R64（本次升格的治理决策登记）。本 ADR 的架构视图落地文件 `10-frontend-architecture.md` v1.0.0 同步新建。`adr/index.md` 同步登记。 |
