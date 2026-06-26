---
module_id: KE-3245
title: 3.1 各层职责与边界
category: documentation
ttl: permanent
---

# 3.1 各层职责与边界

3.1 各层职责与边界

| 层 | 物理目录 | 职责 | 禁止事项 |
|---|---------|------|---------|
| **FE-L1 Application** | `frontend/apps/{app-name}/` | 业务功能组合、路由定义、业务 state 与页面；每个 App 面向一类主要用户场景 | ❌ 不直接定义通用 UI 组件 / ❌ 不直接发 HTTP 请求（必须通过 data-client）/ ❌ 不引用其他 App |
| **FE-L2 Container** | `frontend/platform/` | Module Federation host；全局 App Shell（Sidebar/Topbar/CommandPalette）；跨 App 通信总线；统一 Auth / Theme / i18n / Error / Telemetry | ❌ 不包含具体业务功能 / ❌ 不依赖任何单个 App |
| **FE-L3 Component** | `frontend/packages/{name}/` | 可跨 App 复用的能力单元（UI 组件 / 图表引擎 / 数据客户端 / 认证 SDK 等）| ❌ 不包含业务页面 / ❌ 不依赖具体 App 的 store |
| **FE-L4 Tools** | `frontend/tools/{name}/` | 构建、测试、代码生成、规范工具的统一配置与脚本 | ❌ 不产生运行时代码（纯 dev-time） |
