---
module_id: KE-120
title: 10. 修订记录
category: documentation
ttl: permanent
---

# 10. 修订记录

10. 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-19 | **1.1.0（S15-experimental J1 批次，R69 / OQ-083 closed / ADR-0011 accepted）**：引入 `runtime_planes.md` 正交视图的前端三平面归属索引。**核心变动**：新增 §7.5 "Runtime Plane 归属" 一整节，包含四个子节——§7.5.1 前端模块三平面归属快查表（覆盖 apps/trading-terminal / research-ide / risk-dashboard / monitoring-center / ai-cockpit + platform/ + packages/data-client / chart-engine / ui-kit + SSR 报表 + tools 共 12 行标注）；§7.5.2 前端 Hot Path 的特殊性与硬约束（核心澄清——浏览器 + React 栈天然不满足 04bis 定义的 Hot Path 硬门槛 < 10ms + kernel-bypass + 不可中断，前端所有低延迟需求的上限只能是 **Hot-adjacent**，列出 trading-terminal 行情组件 / 下单面板 / data-client WebSocket 三类 Hot-adjacent 模块的前端侧硬约束——禁用 per-tick setState、Canvas/WebGL 渲染、Optimistic UI、单连接多路复用、反压机制等）；§7.5.3 前端 Cold Path 场景（批量报表导出 / 回测历史回放 / AI 训练任务触发，均走异步通知不阻塞前端）；§7.5.4 与 04bis 同步规则。frontmatter 相应更新：version 1.0.0 → 1.1.0 / related_rationale +R69 / related_open_questions +OQ-083 / related_adr +ADR-0011 / tags +runtime-planes +orthogonal-view +j1。**零前端架构决策变动**——§1 边界 / §2 七原则 / §3 四层模型 / §4 MFE 策略 / §5 State / §6 Design System / §7.1-7.4 构建部署 / §8 双轨 / §9 Activation Triggers 全部保持 v1.0.0 原样，本次仅新增 §7.5 一整节正交视图映射。|
| 2026-04-19 | 1.0.0 | S14-beta 批次 H（Z-FE / 10.1）初版。承载 ADR-0007 accepted（方案 D，前端独立 `frontend/` 顶级目录 + 与后端异构隔离）+ ADR-0008 accepted（Federated-Light + Metamodel）。9 章节：§1 用途与边界 / §2 7 条架构原则 / §3 4 层模型 / §4 Module Federation + MFE 策略 / §5 State 管理 4 域 / §6 Design System 三件套 / §7 构建部署运行时拓扑 / §8 与 `by-domain/frontend-domain/` 关联 / §9 7 档 Activation Triggers。R64 对应本轮治理决策（批次 F R 号并发派号修复 + ADR-0007/0008 追溯性升格 + ADR-0006 跳号登记 + 本视图新建）。|
