---
module_id: KE-3044
title: 发现的 Bug 与修复
category: session_log
ttl: permanent
doc_type: knowledge_entry
---

# 发现的 Bug 与修复

发现的 Bug 与修复

| # | 类型 | 文件 | 问题 | 修复 |
|---|------|------|------|------|
| 1 | 缺失导入 | shared/contracts/risk_limits.py | `from typing import Optional, Dict` 未导入 | 添加 typing 导入 |
| 2 | 字段顺序 | shared/contracts/experiment_result.py | `variant_b_improvement` / `idempotency_key` 跟默认参数后 | 移至 metrics/actionable_suggestions 之前 |
| 3 | 字段顺序 | shared/contracts/system_configuration.py | `created_at` 等 4 字段跟默认参数后 | 移至 config_data 之前 |
| 4 | 字段顺序 | shared/contracts/telemetry_emitter.py | `timestamp` 等 9 字段跟默认参数后 | 移至 labels 之前 |
| 5 | 缺失导出 | L02 __init__.py | codegen 覆盖后丢失 FactorRegistry/autodiscover_factors | 补充从 factor_base 导入 |
| 6 | 缺失导出 | L03 __init__.py | DegradationMonitorBase + CapitalAllocationResult + SynthesizedSignal 未导出 | 从 3 个文件补全导入 |
| 7 | 失效导入 | L04 __init__.py | 残留 StopLossEngine 导入（不存在） | 改为正确的 4 模块完整导出 |
| 8 | 失效导入 | L06 __init__.py | 引用不存在的 OrderRouter | 移除，仅保留 BrokerInterface |
| 9 | 名称错误 | L10 __init__.py | SecurityGatewayBase → 实际类名 SecurityGateway | 修正导入名称 |
| 10 | 缺失导出 | L11 __init__.py | 未导出 codegen 生成的 ModelMetadata/ModelRegistry/ModelTrainerBase | 添加导入 |
