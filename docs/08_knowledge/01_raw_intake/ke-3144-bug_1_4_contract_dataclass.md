---
module_id: KE-3042---contract-dataclass-000
status: active
title: Bug #1: 4 个 contract dataclass 字段排序被 codegen 覆盖
category: session_log
ttl: permanent
doc_type: knowledge_entry
---

# Bug #1: 4 个 contract dataclass 字段排序被 codegen 覆盖

Bug #1: 4 个 contract dataclass 字段排序被 codegen 覆盖
- **位置**: synthesized_signal.py, experiment_result.py, system_configuration.py, telemetry_emitter.py
- **现象**: non-default fields after default fields → TypeError
- **修复**: 所有非默认字段提到默认字段之前（同 Phase C 修复）
