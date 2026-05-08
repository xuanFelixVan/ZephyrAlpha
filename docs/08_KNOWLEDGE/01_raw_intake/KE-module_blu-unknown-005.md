---
module_id: KE-module_blu-unknown-005
title: 命名空间策略
category: module_blueprint
---

# 命名空间策略

命名空间策略

```
指标全限定名 (FQMN, Fully Qualified Metric Name):
  {module_id}::{metric_name}
  例: MOD-INF-008::llm_calls_total, MOD-INF-012::llm_calls_total

  注册规则:
    - Schema Registry 以 FQMN 为唯一 key 存储 MetricSchema
    - 两个不同 module_id 可以注册相同 metric_name——自动解歧为不同 FQMN
    - 同一 module_id 内 metric_name MUST 唯一
    - FQMN 在 SQLite 存储、Dashboard 查询、FLE 消费中统一使用

  冲突检测:
    - 新注册 metric_name 时自动检测是否与同 module_id 下已有指标冲突
    - 冲突 → 返回 CONFLICT 错误码 + 建议替代名称
    - 跨 module_id 不产生冲突告警（由 module_id 前缀自动解歧）
```
