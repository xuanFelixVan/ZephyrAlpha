---
module_id: KE-227-------frontend-layering-001
status: active
title: 3. 前端分层（Frontend Layering）
category: documentation
---

# 3. 前端分层（Frontend Layering）

3. 前端分层（Frontend Layering）

> **📋 SSoT 声明**：前端模块清单（模块 ID / 状态 / 优先级 / runtime_plane / 激活条件等）的**唯一权威来源（Single Source of Truth）**是 [`frontend_model.yaml`](architecture-model/frontend/frontend_model.yaml)。本节仅提供架构级分层概览与职责说明；如需查询具体模块列表、状态或优先级，请以 YAML 为准。

**本节与 03-AA 14 层 Python 后端分层平行但物理隔离**。前端采用 4 层模型（Application / Container / Component / Tools），数字越小越接近业务价值，数字越大越接近基础设施。

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
