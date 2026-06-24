---
module_id: KE-3193---------frontend-architectur-003
title: 2. 前端架构原则（Frontend Architecture Principles）
category: documentation
---

# 2. 前端架构原则（Frontend Architecture Principles）

2. 前端架构原则（Frontend Architecture Principles）

以下 7 条是本视图的**不可违反铁律**，新增 App / package / 工具链选择都必须通过这 7 条过滤。

| # | 原则 | 含义 | 违反后果 |
|---|------|------|---------|
| **FE-P1** | **技术栈异构隔离**（Heterogeneous Stack Isolation）| TypeScript / React / Vite / pnpm 技术栈与后端 Python / uv / pytest 完全隔离，不得互相侵入（无 transpile、无 embed、无 shared build tool）| CI 管线交叉污染；发布不可独立；打破 KBG-0007 |
| **FE-P2** | **API Gateway 唯一对接**（Single Integration Point）| 前端仅通过 L08 `api_gateway/` 子模块对接后端，禁止直接调用 L00-L07/L09-L13 任何模块；禁止嵌入 Python 代码；禁止共享数据库连接 | 破坏分层架构；安全面扩大；OpenAPI 契约失效 |
| **FE-P3** | **契约先行**（Contract-First）| 所有前后端交互必须先在后端 OpenAPI 3.1 Spec 里定义、前端 `tools/codegen/` 自动生成 TypeScript 类型，不手写 DTO；WebSocket Topic 与 Message Schema 同样入契约 | 类型漂移；前后端联调崩溃；Schema 演进不可追溯 |
| **FE-P4** | **微前端边界（Module Federation 基准）**| apps/ 之间不得相互 `import`；可复用能力下沉到 packages/；apps 之间仅通过平台层（platform/）的事件总线 + URL 路由 + 共享 store 通信 | 业务耦合漂移；独立发布失效；增量编译崩溃 |
| **FE-P5** | **设计系统单一真源**（Design System SSoT）| UI 视觉规范、组件库（Design Tokens / Ant Design 扩展）源于 packages/ui-kit 与 `docs/` 内的设计系统说明；apps/ 不得私自定义颜色 / 字体 / 间距的硬编码值 | 视觉碎片化；无法主题切换；暗色模式实现受阻 |
| **FE-P6** | **可观测性内建**（Built-in Observability）| 所有 apps/ 必须自动向 L12 `system_telemetry` 发送三类信号：Web Vitals（LCP/CLS/FID）/ Error（Boundary + window.onerror）/ 业务埋点（TanStack Query 钩子 + 用户动作）；采样率由 platform/ 统一控制 | 线上问题盲飞；无法做用户体验分析；违反 04-TA §10 可观测性原则 |
| **FE-P7** | **渐进激活**（Progressive Activation）| frontend/ 不是 Day-1 资产；**当前不建物理目录**，以 CLI + IDE + Feishu Bot 作为 UI（参见 04-TA §11 Capacity §11.3）；当且仅当 §9 Activation Triggers 触发时才启动具体档位，避免过早抽象 | 提前投入高固定成本；AI 自治闭环未跑通时被 UI 绑架 |
