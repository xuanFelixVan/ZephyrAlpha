---
module_id: KE-350
status: active
title: 4.3 Remote 间通信三条通道
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 4.3 Remote 间通信三条通道

4.3 Remote 间通信三条通道

| # | 通道 | 用途 | 实现 | 数据流向 |
|---|------|------|------|---------|
| 1 | **URL 路由** | App 间跳转携带参数 | React Router `navigate('/app/:id', { state })` | 单向、低频 |
| 2 | **事件总线** | 跨 App 异步广播（如全局登出、主题切换、某交易通知）| `platform/eventBus` 提供 `emit` / `on` / `off`，类型由 `shared-types` 约束 | 多对多、中频 |
| 3 | **共享 Store** | 跨 App 必要的全局状态（user / auth / theme / i18n / feature-flags）| `platform/globalStore`（Zustand）| 多对多、高频但只读 |

**铁律**（对应 FE-P4）：

- ❌ App 之间**不得**相互 import；如需复用，代码必须先提到 packages/
- ❌ 不得使用 `window.postMessage` 等非受控通道
- ❌ 共享 Store 仅承载 "user / auth / theme / i18n / feature-flags" 5 类"必须全局"的状态；业务状态必须在单 App 内部
