---
module_id: KE-2143
status: active
title: 3.7 #25: TraceCapacityInjector
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.7 #25: TraceCapacityInjector

3.7 #25: TraceCapacityInjector

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\trace_capacity_injector.py`

实现 `TraceCapacityInjector` 类（蓝图 L2591-2654）：
- `inject_capacity_metadata(span: Span)`：向 W3C tracestate 注入：
  - `cap_budget_remaining`: 剩余 Error Budget 百分比
  - `cap_tier`: 当前响应级别 (L0-L4)
  - `cap_model_tier`: 当前模型级别
- `extract_from_tracecontext(headers: Dict) -> CapacityMetadata`：下游提取
- 蓝图 L2571-2654 代码完整实现
