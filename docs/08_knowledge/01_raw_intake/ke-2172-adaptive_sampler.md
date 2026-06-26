---
module_id: KE-2080
status: active
title: 3.2 #6: AdaptiveSampler
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.2 #6: AdaptiveSampler

3.2 #6: AdaptiveSampler

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\adaptive_sampler.py`

实现 `AdaptiveSampler` 类：
- `compute_interval(system_load: float, error_budget_tier: str) -> int`：
  - 高负载(>0.8) → 1800s（大幅降频）
  - 中负载(>0.6) → 600s（降频50%）
  - 预算健康(warning/healthy) → 再放宽 1.5×
- `estimate_self_overhead() -> SelfOverheadReport`：自身 CPU/内存/IO 开销 < 2% 系统资源验证
- 蓝图 L1334-1355 完整实现
