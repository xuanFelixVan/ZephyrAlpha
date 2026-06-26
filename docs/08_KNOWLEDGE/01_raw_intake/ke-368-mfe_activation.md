---
module_id: KE-333------activation-004
status: active
title: 4.2 MFE 技术选型（Activation 时定）
category: documentation
ttl: permanent
---

# 4.2 MFE 技术选型（Activation 时定）

4.2 MFE 技术选型（Activation 时定）

> **📋 SSoT 声明**：前端技术栈选型（框架、构建工具、状态管理库、图表引擎等）的权威定义见 [`frontend_model.yaml`](architecture_model/frontend/frontend_model.yaml) 各模块的 `description` 字段。本节提供架构级选型决策与对比分析。

**当前方案**（FE-P7 渐进激活）：**Activation 时再最终选型**，候选已缩到 3 个：

| 方案 | 机制 | 优势 | 劣势 | 推荐触发阈值 |
|------|------|------|------|------------|
| **A：Webpack Module Federation 5** | 原生 MF Runtime | 生态成熟、跨框架可用、独立部署原子性最强 | 构建复杂、SSR 差 | App ≥ 3 + 团队 ≥ 2 人 |
| **B：Vite + @originjs/vite-plugin-federation** | Vite-native MF | 启动快、HMR 体验好、与 FE-P1 选用 Vite 一致 | Runtime 集成没 Webpack MF 成熟 | App ≤ 3 或初期（**推荐初启方案**）|
| **C：Single-SPA** | 路由级拼接 | 跨技术栈融合能力最强（React + Vue + Angular）| 运行时性能较差、开发体验不如 MF | 多团队多栈时 |

**决策规则**：初期激活用方案 B（Vite 原生），App 数量和团队规模满足方案 A 条件时升级到方案 A；方案 C 作为跨栈兜底（本项目单栈 React 不触发）。
