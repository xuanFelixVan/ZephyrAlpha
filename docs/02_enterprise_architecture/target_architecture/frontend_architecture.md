---
module_id: VIEW-10-FRONTEND-ARCH
title: Target Architecture — Frontend Architecture / 目标架构：前端架构
doc_type: architecture_view
status: Active
version: 1.1.1
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-19
related_rationale:
- R64
- R69
related_open_questions:
- OQ-083
related_kb:
- KBG-0007
- KBG-0008
- KBG-0011
tags:
- target-architecture
- frontend
- react
- typescript
- monorepo
- module-federation
- microfrontend
- design-system
- api-gateway
- z-fe
- h1
- runtime-planes
- orthogonal-view
- j1
summary: ZephyrAlpha 2.0 TOGAF 第 10 个架构视图——前端架构。承载 KBG-0007 拍板的方案 D（前端独立 `frontend/`
  顶级目录，与 `src/zephyr/` 53 域 Python 后端完全异构），对标 Bloomberg Terminal / Refinitiv Workspace
  Platform / QuantConnect Lean+Cloud / Interactive Brokers TWS 四家机构共性。9 章节：与 03-AA
  边界 / 7 条前端架构原则 / Application-Container-Component-Tools 四层 / Module Federation 与
  MFE 策略 / State 管理 / Design System 与组件库 / 构建部署运行时拓扑 / Activation Triggers（7 档升级条件）。当前前端 `frontend/` 目录**尚未物理建立**，本视图仅定义"未来前端平台架构终局"；激活时机由
  §9 Activation Triggers 定义。
date: '2026-07-04'
ttl: permanent
---

# Target Architecture — Frontend Architecture / 目标架构：前端架构

## 1. 用途（Purpose）与 03-AA 边界

### 1.1 本视图回答的问题

1. 前端代码在物理上在哪？
2. 前端分哪几层？各层职责？
3. 多个前端 App 如何组织、通信、共享？
4. 前端与后端（`src/zephyr/`）如何对接？
5. 前端构建、部署、运行时拓扑如何？
6. 什么时候启动 / 升级前端平台架构？

### 1.2 本视图**不**回答的问题

| 问题 | 归属视图 |
|------|---------|
| 后端 `src/zephyr/` 53 域分层与模块职责 | `application_architecture.md`（AA） |
| 前端依赖的业务数据对象（Order / Signal / Position 等）| `data_architecture.md`（DA） |
| 前端 ↔ 后端 REST/WebSocket/OpenAPI 字段级契约清单 | `architecture_model/contracts/cross_layer_contracts.yaml` |
| 前端运行时依赖的 Redis / PostgreSQL / LLM 技术栈选型 | `technology_architecture.md`（TA）|
| 前端安全策略（CSP / CORS / CSRF / XSS / OAuth）| `security_architecture.md`（SEC，active）|
| 前端与外部集成拓扑（API Gateway / CDN / 第三方登录）| `integration_architecture.md`（INTEG）|
| 前端运维（监控/日志/告警/发布流水线）| `operations_architecture.md`（OPS）|

### 1.3 与 `03-AA` 的边界铁律

**铁律**：03-AA 定义的是 `src/zephyr/` 53 域 Python 后端架构（D_INTEGRATION_GATEWAY + 各业务域 + api_gateway 子模块），本视图（10-FE）定义的是 `frontend/` 前端独立平台架构。两者**物理隔离、技术栈异构、独立构建、独立部署**。

**接触点**：仅在 D_INTEGRATION_GATEWAY `api_gateway/` 子模块（FastAPI + WebSocket + OpenAPI Spec 生成）——这是前后端**唯一合法对接点**。任何试图让前端直接访问其他业务域的设计均违反 KBG-0007。

### 1.4 决策溯源

- **KBG-0007** 前端层不进 src/ 53 域，作为独立 `frontend/` 平台层（2026-04-18 accepted）
- **KBG-0008** 四架构联邦制（Federated-Light）与 Metamodel 桥梁（2026-04-18 accepted）
- **OQ-043**（closed，2026-04-18）前端层缺失 → 方案 D 采纳
- **OQ-072** EA 文档结构方案 → by-domain 双轨结构已于 2026-05-01 退役，内容回收至主视图
- **R64** 本批次 H 落盘的治理决策（见 `architecture-rationale-log.md`）

## 2. 前端架构原则（Frontend Architecture Principles）

以下 7 条是本视图的**不可违反铁律**，新增 App / package / 工具链选择都必须通过这 7 条过滤。

| # | 原则 | 含义 | 违反后果 |
|---|------|------|---------|
| **FE-P1** | **技术栈异构隔离**（Heterogeneous Stack Isolation）| TypeScript / React / Vite / pnpm 技术栈与后端 Python / uv / pytest 完全隔离，不得互相侵入（无 transpile、无 embed、无 shared build tool）| CI 管线交叉污染；发布不可独立；打破 KBG-0007 |
| **FE-P2** | **API Gateway 唯一对接**（Single Integration Point）| 前端仅通过 D_INTEGRATION_GATEWAY `api_gateway/` 子模块对接后端，禁止直接调用其他业务域任何模块；禁止嵌入 Python 代码；禁止共享数据库连接 | 破坏分层架构；安全面扩大；OpenAPI 契约失效 |
| **FE-P3** | **契约先行**（Contract-First）| 所有前后端交互必须先在后端 OpenAPI 3.1 Spec 里定义、前端 `tools/codegen/` 自动生成 TypeScript 类型，不手写 DTO；WebSocket Topic 与 Message Schema 同样入契约 | 类型漂移；前后端联调崩溃；Schema 演进不可追溯 |
| **FE-P4** | **微前端边界（Module Federation 基准）**| apps/ 之间不得相互 `import`；可复用能力下沉到 packages/；apps 之间仅通过平台层（platform/）的事件总线 + URL 路由 + 共享 store 通信 | 业务耦合漂移；独立发布失效；增量编译崩溃 |
| **FE-P5** | **设计系统单一真源**（Design System SSoT）| UI 视觉规范、组件库（Design Tokens / Ant Design 扩展）源于 packages/ui-kit 与 `docs/` 内的设计系统说明；apps/ 不得私自定义颜色 / 字体 / 间距的硬编码值 | 视觉碎片化；无法主题切换；暗色模式实现受阻 |
| **FE-P6** | **可观测性内建**（Built-in Observability）| 所有 apps/ 必须自动向 D_INFRA_TELEMETRY `system_telemetry` 发送三类信号：Web Vitals（LCP/CLS/FID）/ Error（Boundary + window.onerror）/ 业务埋点（TanStack Query 钩子 + 用户动作）；采样率由 platform/ 统一控制 | 线上问题盲飞；无法做用户体验分析；违反 04-TA §10 可观测性原则 |
| **FE-P7** | **渐进激活**（Progressive Activation）| frontend/ 不是 Day-1 资产；**当前不建物理目录**，以 CLI + IDE + Feishu Bot 作为 UI（参见 04-TA §11 Capacity §11.3）；当且仅当 §9 Activation Triggers 触发时才启动具体档位，避免过早抽象 | 提前投入高固定成本；AI 自治闭环未跑通时被 UI 绑架 |

### 2.1 与业界对标原则的对应关系

| 本原则 | Bloomberg Terminal | Refinitiv Workspace | QuantConnect Cloud | IBKR TWS | Spotify Backstage |
|--------|-------------------|-------------------|-------------------|---------|------------------|
| FE-P1 异构 | ✅ C++ / Electron | ✅ Web Components | ✅ React SPA 独立 repo | ✅ Java Swing / Web Trader | ✅ 独立 TypeScript monorepo |
| FE-P2 Gateway | ✅ BQuant API | ✅ Elektron API | ✅ Lean API | ✅ TWS API | ✅ Backstage Backend |
| FE-P3 契约 | 🟡 Proprietary | ✅ OpenAPI-like | ✅ OpenAPI | 🟡 Proprietary | ✅ OpenAPI |
| FE-P4 MFE | ✅ Plug-in Model | ✅ Web Components | 🟡 Single SPA | N/A | ✅ Plug-in Architecture |
| FE-P5 DS | ✅ Bloomberg UI | ✅ Refinitiv Design | ✅ QC Design | ✅ TWS Design | ✅ Material UI 扩展 |

## 3. 前端分层（Frontend Layering）

**本节与 03-AA 53 域 Python 后端分层平行但物理隔离**。前端采用 4 层模型（Application / Container / Component / Tools），数字越小越接近业务价值，数字越大越接近基础设施。

```
┌─────────────────────────────────────────────────────────────────┐
│  FE-L1 Application Layer（业务 App）                            │
│  frontend/apps/*                                                │
│  - trading-terminal / research-ide / risk-dashboard             │
│  - 每个 App 独立 package.json，独立构建入口                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ imports
┌──────────────────────────▼──────────────────────────────────────┐
│  FE-L2 Container / Platform Layer（宿主 + 命令引擎 + 路由）    │
│  frontend/platform/*                                            │
│  - 微前端宿主（Module Federation host）                         │
│  - 命令引擎（kbar 快捷键 / 命令面板）                           │
│  - 全局路由 / 权限 / 主题 / Auth / ErrorBoundary / Observability│
└──────────────────────────┬──────────────────────────────────────┘
                           │ imports
┌──────────────────────────▼──────────────────────────────────────┐
│  FE-L3 Component / Package Layer（可复用能力包）               │
│  frontend/packages/*                                            │
│  - ui-kit（Ant Design 扩展 + Design Tokens）                    │
│  - chart-engine（TradingView lightweight-charts / D3 金融图表） │
│  - data-client（SWR/TanStack Query + OpenAPI 代码生成客户端）   │
│  - auth（JWT/OIDC SDK）                                         │
│  - shared-types（前后端共享 TypeScript 类型，由 codegen 产生）  │
│  - kbar-actions（命令注册协议）                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │ uses
┌──────────────────────────▼──────────────────────────────────────┐
│  FE-L4 Tools Layer（工具链）                                    │
│  frontend/tools/*                                               │
│  - vite-config（统一 Vite 配置）                                │
│  - codegen（OpenAPI Spec → TypeScript 类型）                    │
│  - e2e（Playwright 配置 + Page Object 基类）                    │
│  - lint-config（ESLint / Prettier / tsconfig 基线）             │
│  - storybook（组件工作台）                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 3.1 各层职责与边界

| 层 | 物理目录 | 职责 | 禁止事项 |
|---|---------|------|---------|
| **FE-L1 Application** | `frontend/apps/{app-name}/` | 业务功能组合、路由定义、业务 state 与页面；每个 App 面向一类主要用户场景 | ❌ 不直接定义通用 UI 组件 / ❌ 不直接发 HTTP 请求（必须通过 data-client）/ ❌ 不引用其他 App |
| **FE-L2 Container** | `frontend/platform/` | Module Federation host；全局 App Shell（Sidebar/Topbar/CommandPalette）；跨 App 通信总线；统一 Auth / Theme / i18n / Error / Telemetry | ❌ 不包含具体业务功能 / ❌ 不依赖任何单个 App |
| **FE-L3 Component** | `frontend/packages/{name}/` | 可跨 App 复用的能力单元（UI 组件 / 图表引擎 / 数据客户端 / 认证 SDK 等）| ❌ 不包含业务页面 / ❌ 不依赖具体 App 的 store |
| **FE-L4 Tools** | `frontend/tools/{name}/` | 构建、测试、代码生成、规范工具的统一配置与脚本 | ❌ 不产生运行时代码（纯 dev-time） |

### 3.2 与后端 53 域的调用规则

```
frontend/apps/*        ──┐
frontend/platform/*    ──┼──→  D_INTEGRATION_GATEWAY api_gateway（FastAPI + WebSocket + OpenAPI）──→  各业务域 Python 后端
frontend/packages/*    ──┘
```

**唯一出口**：`packages/data-client/` 内部封装所有 HTTP/WebSocket 调用，通过 D_INTEGRATION_GATEWAY `api_gateway/`。apps/ 与 platform/ **不得直接 fetch** 后端模块。

## 4. Module Federation / MFE 策略

### 4.1 微前端拓扑

> **📊 微前端拓扑图**：见 [`diagrams/frontend_mfe_topology.mmd`](diagrams/frontend_mfe_topology.mmd)

### 4.2 MFE 技术选型（Activation 时定）

**当前方案**（FE-P7 渐进激活）：**Activation 时再最终选型**，候选已缩到 3 个：

| 方案 | 机制 | 优势 | 劣势 | 推荐触发阈值 |
|------|------|------|------|------------|
| **A：Webpack Module Federation 5** | 原生 MF Runtime | 生态成熟、跨框架可用、独立部署原子性最强 | 构建复杂、SSR 差 | App ≥ 3 + 团队 ≥ 2 人 |
| **B：Vite + @originjs/vite-plugin-federation** | Vite-native MF | 启动快、HMR 体验好、与 FE-P1 选用 Vite 一致 | Runtime 集成没 Webpack MF 成熟 | App ≤ 3 或初期（**推荐初启方案**）|
| **C：Single-SPA** | 路由级拼接 | 跨技术栈融合能力最强（React + Vue + Angular）| 运行时性能较差、开发体验不如 MF | 多团队多栈时 |

**决策规则**：初期激活用方案 B（Vite 原生），App 数量和团队规模满足方案 A 条件时升级到方案 A；方案 C 作为跨栈兜底（本项目单栈 React 不触发）。

### 4.3 Remote 间通信三条通道

| # | 通道 | 用途 | 实现 | 数据流向 |
|---|------|------|------|---------|
| 1 | **URL 路由** | App 间跳转携带参数 | React Router `navigate('/app/:id', { state })` | 单向、低频 |
| 2 | **事件总线** | 跨 App 异步广播（如全局登出、主题切换、某交易通知）| `platform/eventBus` 提供 `emit` / `on` / `off`，类型由 `shared-types` 约束 | 多对多、中频 |
| 3 | **共享 Store** | 跨 App 必要的全局状态（user / auth / theme / i18n / feature-flags）| `platform/globalStore`（Zustand）| 多对多、高频但只读 |

**铁律**（对应 FE-P4）：

- ❌ App 之间**不得**相互 import；如需复用，代码必须先提到 packages/
- ❌ 不得使用 `window.postMessage` 等非受控通道
- ❌ 共享 Store 仅承载 "user / auth / theme / i18n / feature-flags" 5 类"必须全局"的状态；业务状态必须在单 App 内部

## 5. State 管理（Global State + Cross-Module Communication）

### 5.1 State 分域

```
┌───────────────────────────────────────────────────────────────┐
│  Global Store（platform/globalStore，Zustand）               │
│  - user / auth / theme / i18n / featureFlags（5 域，只读注入）│
└───────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌───────────────────────────┴───────────────────────────────────┐
│  App-Local Store（apps/{app}/store，Zustand slice）          │
│  - 每个 App 私有业务状态（订单草稿、回测配置、图表时窗等）    │
└───────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌───────────────────────────┴───────────────────────────────────┐
│  Server State（packages/data-client，TanStack Query）         │
│  - 所有后端数据（GET 结果）的缓存、自动重取、乐观更新         │
│  - Query Key 规范：['resource', { filters }]                  │
│  - Mutation 规范：对应后端 OpenAPI 操作 operationId          │
└───────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌───────────────────────────┴───────────────────────────────────┐
│  Real-time State（packages/data-client，WebSocket）           │
│  - Ticker / Order / Fill / RiskAlert 推送                    │
│  - 合并到 TanStack Query Cache，订阅者自动 re-render          │
└───────────────────────────────────────────────────────────────┘
```

### 5.2 决策理由

| 决策 | 选择 | 不选的替代 | 理由 |
|------|------|----------|------|
| 客户端状态库 | **Zustand** | Redux Toolkit / Jotai / MobX | 最小 API 面、零 Provider 嵌套、与 React 18 并发模式兼容好 |
| 服务端状态库 | **TanStack Query v5** | SWR / Apollo Client / Redux Query | 对 REST/OpenAPI 支持成熟、自动失效策略强、WebSocket 合并能力好 |
| 实时通道 | **原生 WebSocket + 协议 Topic 约定** | Socket.IO / SignalR | 零依赖、后端 FastAPI 原生支持、Topic 字符串可直接入 OpenAPI 扩展 |

### 5.3 Auth / 权限注入路径

```
1. 用户登录 → platform/auth 发起 OIDC → 拿到 JWT
2. JWT 写入 Global Store（只读观察者） + localStorage（可选）
3. data-client 拦截器自动附加 Authorization: Bearer {jwt} 到所有请求
4. WebSocket 连接时把 JWT 作为 subprotocol 或首条消息传给后端
5. JWT 过期 → 静默 refresh → 失败则路由到登录页并清空 Global Store
```

权限模型**当前：单用户单角色**，未来激活 OQ-069 细粒度 RBAC / ABAC 时升级。

## 6. Design System & Component Library

### 6.1 Design System 三件套

| 件 | 物理位置 | 内容 |
|---|---------|------|
| **Design Tokens** | `packages/ui-kit/src/tokens/` | 颜色 / 字体 / 间距 / 阴影 / 圆角 / 动效时长（CSS Variables + JSON）|
| **Primitive Components** | `packages/ui-kit/src/primitives/` | Button / Input / Select / Modal / Table / Form 等原子组件（基于 Ant Design v5 封装）|
| **Pattern Library** | `packages/ui-kit/src/patterns/` + 设计文档 | 业务组合模式（OrderForm / RiskCard / PnLChart / CandlestickChart 等）|

### 6.2 主题策略

- 🌓 **暗色优先**：量化工作场景（夜间盯盘 + 交易大屏）默认 dark theme
- ☀️ **明色可切换**：`platform/theme` 提供切换 API，主题切换通过 CSS Variables 生效（无需重新渲染）
- 🎨 **品牌主题预留**：未来多租户时通过 Tokens 覆盖生成品牌主题

### 6.3 组件库与 Ant Design 的关系

**铁律**：

- Ant Design v5 是**底座**（提供 Button / Form / Table 等原子）
- `ui-kit/primitives/` 是**封装层**（固定默认样式 / 国际化 / 错误处理 / 无障碍 ARIA）
- apps/ **不得直接 import Ant Design**，必须经 ui-kit

这一层封装将来支撑"切换底座到 Material UI 或 Radix"的可能性（方案 R，FE-P7 渐进升级的降级路线）。

### 6.4 图表引擎策略

| 用途 | 选型 | 理由 |
|------|------|------|
| **金融 K 线 / 深度 / 分时** | TradingView lightweight-charts v4 | 开源、性能强、金融图表业界标配 |
| **PnL / Risk 仪表** | Recharts + D3 | React 生态、声明式、可控性强 |
| **Grafana 风格监控**（D_INFRA_TELEMETRY）| iframe 嵌入 Grafana（短期）/ react-grafana-panel（长期）| 不重造轮子 |

## 7. Build / Deploy / Runtime 拓扑

### 7.1 构建管线

> **📊 前端构建管线图**：见 [`diagrams/frontend_build_pipeline.mmd`](diagrams/frontend_build_pipeline.mmd)

### 7.2 部署拓扑

```
浏览器（用户）
    │ HTTPS
    ▼
┌─────────────────────────────────────────────────────────┐
│  CDN / Edge（静态文件）                                 │
│  - platform/dist/index.html + main.js                   │
│  - apps/{app}/dist/remoteEntry.js （Module Federation） │
│  - packages/ui-kit/chart-engine（CDN 共享）             │
└───────────────────────────────┬─────────────────────────┘
                                │ /api/v1/*  /ws
                                ▼
┌─────────────────────────────────────────────────────────┐
│  D_INTEGRATION_GATEWAY api_gateway/（FastAPI + WebSocket）│
│  - /api/v1/orders                                       │
│  - /api/v1/positions                                    │
│  - /api/v1/signals                                      │
│  - /ws/v1/ticker                                        │
│  - /ws/v1/order-updates                                 │
└───────────────────────────────┬─────────────────────────┘
                                │ in-process calls
                                ▼
┌─────────────────────────────────────────────────────────┐
│  src/zephyr/ (53 域 Python 后端)                        │
│  各业务域                                                │
└─────────────────────────────────────────────────────────┘
```

### 7.3 环境矩阵（与 04-TA §9 Environment Matrix 对齐）

| 环境 | 前端部署方式 | API Base | Auth | Feature Flags |
|------|-------------|---------|------|---------------|
| Dev | 本机 `vite dev` | `http://localhost:8000` | Bypass / Mock JWT | all-on |
| UAT | 临时 CDN / Netlify preview | `https://uat-api.zephyr.local` | Mock OIDC | staged |
| Staging | 生产同构 CDN | `https://staging-api.zephyr.local` | 真 OIDC | canary |
| Prod | 生产 CDN + 灰度 | `https://api.zephyr.local` | 真 OIDC | prod-only |

### 7.4 版本化与回滚

- **Platform** 版本与 Apps / Packages 解耦；以 `platform@major.minor.patch` 发布
- **Apps** 每个独立版本号，Module Federation 引用 `remoteEntry.js?version=X` 固定版本
- **Packages** 走 semver + Changeset，apps 升级前先评估 breaking change
- 回滚策略：CDN 层保留最近 10 个版本静态文件，`/platform?version=X` 查询参数可强制回退

### 7.5 Runtime Plane 归属（v1.1.0 新增，R69 / J1 批次，正交视图引用）

> **定位**：本节把前端 4 层（FE-L1 Apps / FE-L2 Platform / FE-L3 Packages / FE-L4 Tools）在 `runtime_planes.md` 正交视图的 **Hot / Warm / Cold 三平面**上做归属标注。**FE-L4 Tools 不入运行平面**（纯 dev-time 工具链，无运行时代码）。
> **SSoT**：`runtime_planes.md` §3.4 "前端平面归属" 是本标注的规范源头；本节只做前端视角的索引与澄清。

#### 7.5.1 前端模块三平面归属快查表

| 前端模块 | 所属 FE 层 | Runtime Plane | 延迟特征 | 技术栈 | 部署拓扑 |
|---------|-----------|--------------|--------|-------|---------|
| **apps/trading-terminal** 交易终端核心视图 | FE-L1 App | **Warm 主**（React 渲染 + 用户交互，< 100ms 目标）| 10-100ms | React 18 + Vite | CDN 静态 |
| **apps/trading-terminal `/ws/*` 行情/成交订阅** | FE-L1 App | **Hot-adjacent**（浏览器端 WebSocket 客户端 < 20ms 回路 + D_INTEGRATION_GATEWAY `/ws/v1/ticker` Hot Path 对接）| 10-50ms | 原生 WebSocket + TanStack Query merge | CDN + 后端 Hot |
| **apps/research-ide** 研究 IDE | FE-L1 App | **Warm**（与 D_RESEARCH 域对接，交互式但非极限低延迟）| 100-500ms | React + Monaco Editor | CDN |
| **apps/risk-dashboard** 风控仪表盘 | FE-L1 App | **Warm 实时指标 + Cold 报表导出**（实时位 Warm，PDF / Excel 批量导出 Cold 走后端批处理）| Warm 100-500ms / Cold 秒-分钟 | React + Recharts / Lightweight-charts + SSR 报表后端 | CDN + D_INTEGRATION_GATEWAY + D_REPORTING 批导出 |
| **apps/monitoring-center** 监控中心 | FE-L1 App | **Warm**（Grafana iframe 嵌入 + D_INFRA_TELEMETRY 对接）| 100-500ms | React + Grafana panel | CDN + Grafana |
| **apps/ai-cockpit**（G4 激活，未建）| FE-L1 App | **Warm**（与 D-03 Decision Engine / D-06 Market Regime 对接）| 100-500ms | React + kbar | CDN + D_INTEGRATION_GATEWAY |
| **platform/**（App Shell / Router / Auth / Theme / EventBus / CommandPalette）| FE-L2 Container | **Warm**（全局壳 + 路由 + 权限 + 事件总线 < 50ms 切换目标）| 10-100ms | React + Zustand + Module Federation host | CDN 静态 |
| **packages/data-client**（TanStack Query + OpenAPI SDK + WebSocket 封装）| FE-L3 Package | **Hot-adjacent（WebSocket 路径）+ Warm（REST 路径）双栖** | WS 10-50ms / REST 50-200ms | TanStack Query v5 + 原生 WebSocket | NPM 私有 |
| **packages/chart-engine**（TradingView lightweight-charts / Recharts 图表渲染）| FE-L3 Package | **Warm**（浏览器渲染 + Canvas / WebGL，帧率 60fps 目标）| 16ms 单帧预算 | TradingView + D3 | NPM 私有 |
| **packages/ui-kit / auth / shared-types / kbar-actions** | FE-L3 Package | **Warm**（都是运行时复用能力）| 10-100ms | React + TypeScript | NPM 私有 |
| **SSR 报表导出服务**（未来 G3+ 激活，承载 PDF / Excel / 周报）| 非前端 App，后端配套 | **Cold**（报表批生成 1-300s，cron 或 on-demand）| 秒-分钟 | Node.js + Puppeteer / Python + WeasyPrint | D_REPORTING 批处理 |
| **tools/vite-config / codegen / e2e / lint-config / storybook** | FE-L4 Tools | **不入运行平面**（纯 dev-time，CI/IDE 内使用）| N/A | Vite + pnpm + Playwright | N/A |

#### 7.5.2 前端 Hot Path 的特殊性与硬约束

**关键澄清**：**前端没有真正的 Hot Path**（04bis 定义 Hot Path = < 10ms 端到端 + kernel-bypass + C++/Rust + 不可中断），**浏览器 + React 技术栈天然不满足 Hot Path 硬门槛**。但前端存在 **Hot-adjacent（Hot 邻接）** 子模块——它们本身运行在 Warm Path（10-100ms），但 **对接后端 Hot Path 的下游数据**，需要特殊优化：

| Hot-adjacent 模块 | 何处"邻接 Hot" | 前端侧硬约束 |
|------------------|--------------|------------|
| `trading-terminal` 行情组件 | 订阅 D_INTEGRATION_GATEWAY `/ws/v1/ticker` Hot Path 推送 | ❌ 禁用 `setState` per-tick（必须批量 rAF 合并 / Web Worker 预聚合）; ❌ 禁用 React re-render per-tick（用 Zustand subscribeWithSelector + 手动 DOM 更新）; ✅ Canvas/WebGL 渲染（非 React DOM）; ✅ 接收端 WebSocket 缓冲区 < 10ms 批处理 |
| `trading-terminal` 下单面板 | 发送 D_INTEGRATION_GATEWAY `/api/v1/orders` Hot Path 下单 | ❌ 禁用任何 > 50ms 客户端校验（快速路径）; ✅ Optimistic UI（乐观更新，回滚在 TanStack Mutation onError）; ❌ 禁用下单流程中的 `import()` 懒加载 |
| `data-client WebSocket` | 所有 `/ws/v1/*` 订阅 | ✅ 单连接多路复用（不为每个 Topic 开连接）; ✅ 反压机制（client-side back-pressure，服务端推送超阈值时降级为轮询）; ✅ 断线自动重连 + 消息 gap 追补 |

#### 7.5.3 前端 Cold Path 场景

| 场景 | 触发 | 执行路径 |
|------|------|---------|
| **批量报表导出（PDF / Excel / 周报）** | `risk-dashboard` 点击 "导出周报" | 前端发 POST `/api/v1/reports/generate` → D_INTEGRATION_GATEWAY 接收 → 转发 D_REPORTING 批处理 → SSR 服务渲染（1-300s）→ 生成完成后 WebSocket 通知前端下载链接 |
| **策略回测历史回放** | `research-ide` 启动回测 | 前端仅发任务 ID，**不等待结果**；回测 Cold Path 运行时长可达分钟-小时级；完成后通过 Feishu/Email/WebSocket 异步通知 |
| **AI 训练任务触发**（G4 G5 激活后）| `ai-cockpit` 提交模型训练 | 前端仅启动任务 + 轮询状态；训练在 D_ML_TRAIN Cold Path（小时-天级） |

#### 7.5.4 与 `runtime_planes.md` 的同步规则

| 当发生这些变动时 | 必须联动更新 |
|----------------|------------|
| 新增前端 App | 本节 §7.5.1 加一行（标注 Warm / Hot-adjacent / Cold）+ `04bis` §3.4 前端平面归属表同步 |
| 前端某模块延迟预算从 Warm 升级到 Hot-adjacent（或降级） | 本节 §7.5.2 Hot-adjacent 表更新 + `04bis` §5 跨面通信协议章节同步 + KB 决策记录审批（如果是 Hot-adjacent 首次引入一整类场景）|
| SSR 报表或批处理导出服务启用 | 本节 §7.5.3 + `04bis` §3.4 + 04-TA Cold Path 技术栈章节同步 |

**硬约束**：任何前端模块若自称 "Hot Path 原生"（< 10ms + kernel-bypass + 不可中断）均属**伪 Hot 声明**——浏览器技术栈无法满足 04bis 定义的 Hot Path 硬门槛，PR reviewer 必须驳回。前端所有低延迟需求的上限都是 Hot-adjacent。

## 8. 双轨/下沉结构（已退役）

> **2026-05-01 更新**：原 `by-domain/` 双轨结构已于 README v2.0.0 统一移除。所有原计划下沉到 `by-domain/frontend-domain/` 的内容已吸纳入本视图及 `architecture_model/` YAML 联邦模型。以下触发清单保留为历史参考，实际落地不再依赖独立 by-domain 目录。

**下沉触发条件（历史记录）**：

| 触发 | 动作 |
|------|------|
| 03-AA §frontend 章节 > 800 行 | 下沉到 `frontend-domain/architecture.md` |
| 实际开始建 `frontend/` 仓 | 新建 `module-topology.mmd` + `apps-portfolio.md` + `interfaces.md` |
| App ≥ 5 时 | 新建 `apps-portfolio.md` |
| packages ≥ 3 时 | 新建 `packages-inventory.md` |
| API 路由 ≥ 10 类时 | 新建 `interfaces.md`（OpenAPI/WebSocket Topic/Auth）|
| AI Operator 启用 | 新建 `ai-ops-frontend.md` |

## 9. Activation Triggers（升级触发条件）

**本视图遵循 FE-P7 渐进激活原则**。当前前端 `frontend/` 目录**尚未物理建立**；CLI + IDE + Feishu Bot 承担 Day-1 UI 职责（参见 04-TA §11.3 LLM 用户界面假设）。本章节定义 7 档激活升级条件。

### 9.1 激活档位表

| 档位 | 名称 | 触发条件（任一即可）| 激活动作 | 预计工作量 |
|------|------|-------------------|---------|-----------|
| **G0** | 当前态（未激活）| — | 无前端代码；CLI + Cursor + Feishu bot 满足所有交互 | 0 |
| **G1** | 最小 dashboard | 外部干系人（非本人 Owner）看报表/监控的需求 ≥ 2 周/次 | 搭 `frontend/` 骨架 + 1 个 App（risk-dashboard 或 monitoring-center）+ 最小 packages（ui-kit / data-client）+ tools | 5-8 天 |
| **G2** | 2-3 App 平台 | (a) G1 已运行且稳定 ≥ 1 个月 & (b) 第 2 个 App 的业务需求成熟 | 启动 Module Federation（方案 B：Vite-native MF）+ platform/ 骨架 + 第 2/3 App | 8-12 天 |
| **G3** | 团队级平台 | (a) App ≥ 3 & (b) 出现第 2 个前端开发者（人或 AI Operator）| 切换到 Webpack MF（方案 A）+ 私有 NPM + CI gate + Design System v2 | 10-15 天 |
| **G4** | AI Operator 集成 | OQ-063 F-1/F-2/F-3 AI Operator 启用到 frontend 域 | 新建 `frontend/apps/ai-cockpit` + `packages/kbar-actions` AI 指令协议 + 自动化测试增强 | 8-12 天 |
| **G5** | 外部租户 | 多账户 / 多机构需求浮出 | 主题 Token 多租户化 + Auth 升级到企业 OIDC + 权限 RBAC/ABAC 细粒度化 | 12-20 天 |
| **G6** | 移动原生端 | (a) 盯盘 / 风控告警移动端需求 & (b) PWA 不满足 | React Native 新分支（不进 web monorepo）or Capacitor PWA | 视需求定 |

### 9.2 不应激活的反信号

| 信号 | 含义 | 正确动作 |
|------|------|---------|
| "想做 UI 但说不出第一个用户是谁" | 业务需求未成熟 | 继续停留 G0，用 CLI / Feishu 验证需求 |
| "Cursor / Copilot 生成了一个页面要不要留" | 代码先于架构 | 先让它过 §1-§7 原则审核；不过则舍弃，不做"临时方案" |
| "交易信号页面嵌到 D_PF_CORE 里" | 违反 KBG-0007 + FE-P1/FE-P2 | 强制踢回 G0 或 G1，不允许临时破例 |
| "搭个后台管理页改数据库" | 违反 FE-P2 + 安全原则 | 改用后端 admin CLI 或 Feishu Bot 工具，不要为此开 G1 |

### 9.3 每档激活的必做 KB 决策记录 / 视图更新

| 档位 | 需起草的 KB 决策记录 | 需更新的视图 |
|------|------------|-----------|
| G1 | KBG-0007-A（API 契约 OpenAPI 版本 / 错误格式 / 认证）| 本视图 v1.0.0 → v1.1.0（G1 运行反馈回注）|
| G2 | KBG-0007-B（前端治理扩展：ESLint / MFE 约束 / 共享包）| 本视图 §4 更新实际选型方案 |
| G3 | KBG-0007-C（团队协作 / Release Train / Design System v2）| 本视图 §4 扩展前端治理章节 |
| G4 | KB 决策记录（AI Operator Frontend 整合）| OQ-063 F-1/F-2/F-3 激活闭环 |

### 9.4 下沉规则（与 OQ-072 双轨制协同）

- **本视图正文**：架构级决策、业界对标、原则、分层、拓扑、激活触发 → 永远留在本视图
- **详细实现细节**（具体 package 清单 / App 路由树 / OpenAPI Operation 列表 / 组件 API）→ 待触发下沉时在本视图 §7.5/§8 扩展
- **触发条件**：本视图某章节 > 400 行 且 OQ-072 三条件满足（架构终局已锁 + 父章节超阈值 + 用户批准下沉计划）

> 修订记录由 git log 承载，不再手写。
