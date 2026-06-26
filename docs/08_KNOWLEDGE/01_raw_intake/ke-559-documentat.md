---
module_id: KE-507
title: 7.5.1 前端模块三平面归属快查表
category: documentation
ttl: permanent
---

# 7.5.1 前端模块三平面归属快查表

7.5.1 前端模块三平面归属快查表

> **📋 SSoT 声明**：各模块的 `runtime_plane` 权威值定义在 [`frontend_model.yaml`](architecture_model/frontend/frontend_model.yaml)。下表为架构视角的快查索引。

| 前端模块 | 所属 FE 层 | Runtime Plane | 延迟特征 | 技术栈 | 部署拓扑 |
|---------|-----------|--------------|--------|-------|---------|
| **apps/trading-terminal** 交易终端核心视图 | FE-L1 App | **Warm 主**（React 渲染 + 用户交互，< 100ms 目标）| 10-100ms | React 18 + Vite | CDN 静态 |
| **apps/trading-terminal `/ws/*` 行情/成交订阅** | FE-L1 App | **Hot-adjacent**（浏览器端 WebSocket 客户端 < 20ms 回路 + L08 `/ws/v1/ticker` Hot Path 对接）| 10-50ms | 原生 WebSocket + TanStack Query merge | CDN + 后端 L08 Hot |
| **apps/research-ide** 研究 IDE | FE-L1 App | **Warm**（与 L09 research_innovation 对接，交互式但非极限低延迟）| 100-500ms | React + Monaco Editor | CDN |
| **apps/risk-dashboard** 风控仪表盘 | FE-L1 App | **Warm 实时指标 + Cold 报表导出**（实时位 Warm，PDF / Excel 批量导出 Cold 走后端批处理）| Warm 100-500ms / Cold 秒-分钟 | React + Recharts / Lightweight-charts + SSR 报表后端 | CDN + L08 + L12 批导出 |
| **apps/monitoring-center** 监控中心 | FE-L1 App | **Warm**（Grafana iframe 嵌入 + L12 telemetry 对接）| 100-500ms | React + Grafana panel | CDN + Grafana |
| **apps/ai-cockpit**（G4 激活，未建）| FE-L1 App | **Warm**（与 D-03 Decision Engine / D-06 Market Regime 对接）| 100-500ms | React + kbar | CDN + L08 |
| **platform/**（App Shell / Router / Auth / Theme / EventBus / CommandPalette）| FE-L2 Container | **Warm**（全局壳 + 路由 + 权限 + 事件总线 < 50ms 切换目标）| 10-100ms | React + Zustand + Module Federation host | CDN 静态 |
| **packages/data-client**（TanStack Query + OpenAPI SDK + WebSocket 封装）| FE-L3 Package | **Hot-adjacent（WebSocket 路径）+ Warm（REST 路径）双栖** | WS 10-50ms / REST 50-200ms | TanStack Query v5 + 原生 WebSocket | NPM 私有 |
| **packages/chart-engine**（TradingView lightweight-charts / Recharts 图表渲染）| FE-L3 Package | **Warm**（浏览器渲染 + Canvas / WebGL，帧率 60fps 目标）| 16ms 单帧预算 | TradingView + D3 | NPM 私有 |
| **packages/ui-kit / auth / shared-types / kbar-actions** | FE-L3 Package | **Warm**（都是运行时复用能力）| 10-100ms | React + TypeScript | NPM 私有 |
| **SSR 报表导出服务**（未来 G3+ 激活，承载 PDF / Excel / 周报）| 非前端 App，后端配套 | **Cold**（报表批生成 1-300s，cron 或 on-demand）| 秒-分钟 | Node.js + Puppeteer / Python + WeasyPrint | L12 批处理 |
| **tools/vite-config / codegen / e2e / lint-config / storybook** | FE-L4 Tools | **不入运行平面**（纯 dev-time，CI/IDE 内使用）| N/A | Vite + pnpm + Playwright | N/A |
