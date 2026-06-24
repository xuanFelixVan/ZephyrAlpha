---
module_id: KE-2557----ai-agent-003
status: active
title: 七、Anti-Patterns —— AI agent 绝对禁止的集成行为
category: module_blueprint
---

# 七、Anti-Patterns —— AI agent 绝对禁止的集成行为

七、Anti-Patterns —— AI agent 绝对禁止的集成行为

> 氛围编程社区（Cursor Rules / Windsurf Rules）的核心教条：
> 集成文档的首要价值不是告诉 AI 该做什么，而是告诉 AI **什么绝对不能做**。
> 以下每一条违反都会导致系统级故障——没有例外。

| # | Anti-Pattern | 违反后果 | 正确做法 |
|---|-------------|---------|---------|
| AP1 | **绕过集成契约直接调用**——子系统A不经过CT-*契约直接import子系统B的内部模块 | 契约SSoT失效 → CI校验无意义 → 重构时全盘崩溃 | 任何跨系统调用必须通过CT-*契约定义的接口 |
| AP2 | **M1-M5产出物直接进入B-zone**——Pipeline A-zone(生产)产出的artifact未经审核直接流入B-zone(审计) | 生产数据污染审计数据 → 审计结论失真 | A-zone产出物必须经过M6边界明确标记后才能进入B-zone |
| AP3 | **无异常检测触发回滚**——FLE未检测到异常就执行THROTTLE/ROLLBACK | 正常系统被误杀 → 假阳性导致任务堆积 | ROLLBACK仅当FLE.detect_anomaly()返回true时触发 |
| AP4 | **CE compress阶段丢弃raw_text**——上下文引擎压缩时删除原始文本只保留向量 | 下游LLM安全审查失败（需要raw_text做注入检测）| compress永远保留raw_text字段——LSG消费raw_text |
| AP5 | **熔断降级时跳过安全校验**——circuit_breaker触发后跳过LSG检查以恢复性能 | 攻击者利用熔断窗口注入恶意prompt | LSG不可降级——fail-closed优先于availability |
| AP6 | **任务卡片跨status跳跃**——TaskCard.status从DRAFT直接跳到COMPLETED | 绕过G0-G7全部门禁 → 门控引擎形同虚设 | status迁移必须遵循 DRAFT→TODO→IN_PROGRESS→REVIEW→COMPLETED |
| AP7 | **共享Schema字段私自扩展**——子模块为方便在SCHEMA-*上追加字段但不更新本蓝图 | 多系统消费同一Schema但字段不一致 → 反序列化失败 | SCHEMA-*变更必须本蓝图审批后广播所有消费系统 |
| AP8 | **模拟对方系统的"假成功"响应**——测试时用mock返回CT-*契约里未定义的响应格式 | 测试通过但集成时break | mock必须定义在CT-*契约的`mock_strategy`字段内 |

---
