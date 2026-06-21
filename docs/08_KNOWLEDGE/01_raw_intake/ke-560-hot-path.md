---
module_id: KE-508----hot-path-000
title: 7.5.2 前端 Hot Path 的特殊性与硬约束
category: documentation
---

# 7.5.2 前端 Hot Path 的特殊性与硬约束

7.5.2 前端 Hot Path 的特殊性与硬约束

**关键澄清**：**前端没有真正的 Hot Path**（04bis 定义 Hot Path = < 10ms 端到端 + kernel-bypass + C++/Rust + 不可中断），**浏览器 + React 技术栈天然不满足 Hot Path 硬门槛**。但前端存在 **Hot-adjacent（Hot 邻接）** 子模块——它们本身运行在 Warm Path（10-100ms），但 **对接后端 Hot Path 的下游数据**，需要特殊优化：

| Hot-adjacent 模块 | 何处"邻接 Hot" | 前端侧硬约束 |
|------------------|--------------|------------|
| `trading-terminal` 行情组件 | 订阅 L08 `/ws/v1/ticker` Hot Path 推送 | ❌ 禁用 `setState` per-tick（必须批量 rAF 合并 / Web Worker 预聚合）; ❌ 禁用 React re-render per-tick（用 Zustand subscribeWithSelector + 手动 DOM 更新）; ✅ Canvas/WebGL 渲染（非 React DOM）; ✅ 接收端 WebSocket 缓冲区 < 10ms 批处理 |
| `trading-terminal` 下单面板 | 发送 L08 `/api/v1/orders` Hot Path 下单 | ❌ 禁用任何 > 50ms 客户端校验（快速路径）; ✅ Optimistic UI（乐观更新，回滚在 TanStack Mutation onError）; ❌ 禁用下单流程中的 `import()` 懒加载 |
| `data-client WebSocket` | 所有 `/ws/v1/*` 订阅 | ✅ 单连接多路复用（不为每个 Topic 开连接）; ✅ 反压机制（client-side back-pressure，服务端推送超阈值时降级为轮询）; ✅ 断线自动重连 + 消息 gap 追补 |
