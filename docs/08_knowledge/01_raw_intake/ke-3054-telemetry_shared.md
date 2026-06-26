---
module_id: KE-2953-----shared-003
title: 新建清单（Telemetry 独有的、shared 不提供的）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 新建清单（Telemetry 独有的、shared 不提供的）

新建清单（Telemetry 独有的、shared 不提供的）

| 新建组件 | 所在子系统 | 理由（为什么 shared 没有提供） |
|---------|----------|------|
| MetricPoint（含 Histogram/Summary） | §4 metrics | shared 无指标采集/聚合能力 |
| JSONLFileWriter（按日轮转） | §5 logs | shared.logging 提供格式化但不提供持久化策略 |
| Span 数据模型 + tail-based sampler | §6 traces | shared 有 TraceContext 传播但无 Span 模型和采样 |
| AIBehaviorEvent + 7 维度 tracker | §7 ai_behavior | 业务专属，shared 不应承载 |
| Schema Registry（YAML SSoT + 运行时校验） | §12 schema | shared 无指标 schema 治理 |
| Multi-Window Burn Rate 告警规则 | §11 alerts | shared 无告警领域逻辑 |
| Telemetry watchdog 独立进程 | §10 health | 系统进程类（非 library），不应放在 shared |
| profile collector（py-spy → pprof） | §9 profiles | 外部工具集成，非 shared 职责 |

---
