---
task_id: TASK-INF-0105
status: planned
priority: P1
severity: high
module_id: MOD-INF-007
phase: 1
category: implementation
effort_estimated: 2h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §3.3、§六 DD6、§九 R3
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\circuit_breaker.py
acceptance_criteria:
  - "AC1: CircuitBreaker failure_threshold=5，非 3——与蓝图 §3.3 精确对齐"
  - "AC2: cooldown_seconds=60，非 5 分钟——与蓝图 §3.3 精确对齐"
  - "AC3: half_open_max_requests=1——半开状态下只允许 1 个请求通过"
  - "AC4: 状态枚举：CLOSED / OPEN / HALF_OPEN——与蓝图 DD6 对齐"
  - "AC5: record_failure()→failure_count>5→→OPEN；满 cooldown→→HALF_OPEN；1 成功→→CLOSED"
  - "AC6: CircuitBreaker 按 model_name 独立计数——每个模型独立熔断（reason 关联到模型而不是全局）"
rollback_instructions:
  - "circuit_breaker.py→空桩：allow_request() 永远返回 True"
  - "删除所有 CircuitBreaker 引用——G5 gate 退化为无条件 PASS"
created_at: 2026-05-06T23:38:00Z
updated_at: 2026-05-07T00:32:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0104
blocked_by:
  - TASK-INF-0101
  - TASK-INF-0104
blocks:
  - TASK-INF-0102
  - TASK-INF-0128
tags:
  - gate-engine
  - circuit-breaker
  - §3.3
  - threshold=5
  - cooldown=60s
  - blueprint-v0.5.0
version: 2.0.0
change_log: |
  v2.0.0 (2026-05-07): 二次核查修正——threshold=5、cooldown=60s、参数与蓝图 §3.3 精确对齐。此前 v1.0.0 用 threshold=3、cooldown=5min 为错误推断。
  v1.0.0 (2026-05-06): 初始创建（错误版本——已废弃）
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections:
    - §3.3 熔断器模式
    - §六 DD6 熔断器设计决策
    - §九 R3 DeepSeek 幻觉风险
  keywords:
    - circuit-breaker
    - §3.3
    - threshold-5
    - cooldown-60s
    - blueprint-v0.5.0
  ai_reads_for_inference: true
---

# TASK-INF-0105: CircuitBreaker 熔断器实现（v2.0.0 修正版）

## 背景与动机

CircuitBreaker 按蓝图 §3.3 定义：**failure_threshold=5、cooldown_seconds=60**。防止一个模型连续 5 次门禁 FAIL 后继续消耗资源，60s 后自动半开试探恢复。

## 蓝图 §3.3 精确对齐

```python
class CircuitBreaker:
    FAILURE_THRESHOLD = 5      # ← 蓝图 §3.3
    COOLDOWN_SECONDS = 60      # ← 蓝图 §3.3
    HALF_OPEN_MAX_REQUESTS = 1 # 半开状态只允许 1 个探测请求

    def __init__(self):
        self._failures: dict[str, list[float]] = {}  # model → [failure_timestamps]

    def record_failure(self, model: str) -> None:
        now = time.time()
        self._failures.setdefault(model, []).append(now)
        # 保留最近 threshold+1 个时间戳

    def allow_request(self, model: str) -> bool:
        failures = self._failures.get(model, [])
        now = time.time()
        recent = [t for t in failures if now - t < self.COOLDOWN_SECONDS]
        return len(recent) < self.FAILURE_THRESHOLD

    def record_success(self, model: str) -> None:
        self._failures[model] = []  # 成功后清零

    def get_state(self, model: str) -> str:
        return "OPEN" if not self.allow_request(model) else "CLOSED"
```

## 回退方案

`allow_request()` → 永远返回 True。G5 gate → 无条件 PASS。

## 验收标准

| # | 标准 |
|---|------|
| AC1 | failure_threshold=5（非 3） |
| AC2 | cooldown_seconds=60（非 300） |
| AC3 | half_open_max_requests=1 |
| AC4 | 状态：CLOSED / OPEN / HALF_OPEN |
| AC5 | 5 次失败→OPEN；60s→HALF_OPEN；1 成功→CLOSED |
| AC6 | 按 model_name 独立计数 |
