---
module_id: KE-1015
status: active
title: 7.4 Schema 校验（启动期强制）
category: governance
ttl: permanent
---

# 7.4 Schema 校验（启动期强制）

7.4 Schema 校验（启动期强制）

`GateEngine.reload_gates()` 必须对每个 YAML 执行：

1. 顶层必填字段存在性（`gate_id, gate_name, title, description, status, ttl, entry_conditions`）
2. `gate_id` 正则 `^G[1-5]$` 匹配
3. `gate_name` ∈ `{ingest, triage, evaluate, activate, extract}`
4. `gate_id` 与 YAML 文件名前缀一致（`g1_*.yaml` 必须 `gate_id=G1`）
5. `entry_conditions` 中每条 `id` 在同文件唯一
6. `severity` 字段值在允许集合内
7. `on_failure` 字段值在允许集合内

**失败动作**：引擎启动 `fail-fast`，拒绝启动；Owner 修复后重启。
