---
module_id: KE-4027
title: 2e. FeatureFlag 控制矩阵 🆕
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2e. FeatureFlag 控制矩阵 🆕

2e. FeatureFlag 控制矩阵 🆕

> **B20 修复**——v0.5.0 新增。所有 Telemetry 实验性或资源敏感功能 MUST 由 `shared/flags.py` 的 FeatureFlag 三态开关守护。AI 新增的功能初始为 OFF，人工在 `config/` 中启用后才生效。

| Flag Key | 控制功能 | 默认值 | 开关影响的子系统 |
|---------|------|:---:|------|
| `telemetry.enable_profiling` | profiling 子系统全量开关 | OFF | §9 profiles |
| `telemetry.debug_full_sampling` | 临时将 trace 采样率提到 100%（排障用） | OFF | §6 traces |
| `telemetry.cost_alert_threshold_usd` | 日 LLM 成本告警阈值 | 5.0 | §7 ai_behavior → §11 alerts |
| `telemetry.log_level_override.{module}` | 按模块覆盖日志级别（如 `telemetry.log_level_override.pipeline = DEBUG`） | 无覆盖 | §5 logs |
| `telemetry.enable_ai_behavior_tracking` | AI 行为 7 维度全量追踪 | ON | §7 ai_behavior |
| `telemetry.cardinality_strict_mode` | 严格基数模式：超限指标直接拒绝（而非聚合） | OFF | §4 metrics |
| `telemetry.archive_auto_cleanup` | 过期归档自动物理删除 | ON | §8 archive |
| `telemetry.enable_slo_postmortem` | SLO 违规自动生成 Postmortem 草稿 | OFF | §11 alerts → Audit Trail |
