---
task_id: "TASK-INF-0005"
title: "漂移状态机 state_machine.py 实现（D-023-04）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "4h"
actual_effort: null
assigned_to: null
created_by: "AI-Decomposer"
created_date: "2026-05-06"
updated_date: "2026-05-06"
depends_on: ["TASK-INF-0001","TASK-INF-0002","TASK-INF-0003"]
blocks: ["TASK-INF-0006","TASK-INF-0051"]
related_adrs: ["ADR-0022"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\state_machine.py"
acceptance_criteria:
  - "DriftStateMachine 类实现全 10 状态：DETECTED→TRIAGED→ACKNOWLEDGED→RESOLVING→RESOLVED→VERIFIED 正向链路 + FIX_FAILED + FALSE_POSITIVE + DEAD_LETTER + SUPPRESSED"
  - "每个状态转换包含 validate_transition(from, to) 方法"
  - "auto_transition 逻辑：TRIAGED 中 AUTO_FIXABLE → RESOLVING（自动触发修复）; FIX_FAILED → NEEDS_HUMAN"
  - "TTL 机制：DETECTED 24h 未 ACK → DEAD_LETTER; SUPPRESSED expires_at 到达 → DETECTED"
  - "状态变更写入 drift_events 表（UPDATE state + updated_at）"
rollback_instructions: "git checkout src/zephyr/drift_detector/state_machine.py"
context_assembly_manifest:
  - file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
    sections: ["§2.3"]
tags: ["drift-detector","state-machine","lifecycle","D-023-04"]
compliance_tags: ["GOV-DOC-002","GOV-TASK-003"]
risks:
  - risk_id: "R-INF-023-04"
    description: "状态机与 drift_events 表状态不一致"
    impact: "漂移状态显示错乱"
    likelihood: "low"
    mitigation: "状态变更使用 SQLite 事务 + 前置状态校验。禁止直接 UPDATE state 列，必须走 state_machine.transition() 方法"
    owner: "TASK-INF-0005执行者"
---

# TASK-INF-0005: 漂移状态机 state_machine.py

## 目标

实现完整的 10 状态漂移生命周期状态机，控制 DETECTED→VERIFIED 的正向修复链路和 DEAD_LETTER/FALSE_POSITIVE 异常路径。对标 blueprint §2.3。

## 执行步骤

### Step 1: 定义 DriftState 枚举

```python
class DriftState(Enum):
    DETECTED = "DETECTED"
    TRIAGED = "TRIAGED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVING = "RESOLVING"
    RESOLVED = "RESOLVED"
    VERIFIED = "VERIFIED"
    FIX_FAILED = "FIX_FAILED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    DEAD_LETTER = "DEAD_LETTER"
    SUPPRESSED = "SUPPRESSED"
```

### Step 2: 定义状态转移矩阵

```
DETECTED → TRIAGED, ACKNOWLEDGED, FALSE_POSITIVE, DEAD_LETTER(auto 24h)
TRIAGED → RESOLVING(auto if AUTO_FIXABLE), ACKNOWLEDGED
ACKNOWLEDGED → RESOLVING
RESOLVING → RESOLVED(修复成功), FIX_FAILED(修复失败)
RESOLVED → VERIFIED(下次scan通过)
FIX_FAILED → ACKNOWLEDGED(NEEDS_HUMAN)
FALSE_POSITIVE → 终端(记录到 detector feedback)
DEAD_LETTER → ACKNOWLEDGED(Owner ACK后)
SUPPRESSED → DETECTED(expires_at到达)
```

### Step 3: 实现 DriftStateMachine 类

- `transition(event_id, from_state, to_state)`：原子状态变更，写 drift_events
- `auto_transition(event_id)`：基于事件属性自动判断下一状态
- `check_ttl()`：定时扫描 DETECTED/SUPPRESSED 状态 TTL 过期事件

## 验收标准

- 全10状态和状态转移路径完整实现
- 每次状态变更走 SQLite 事务
- DETECTED 24h → DEAD_LETTER 自动升级
- SUPPRESSED expires_at → DETECTED 自动恢复

## 回滚指令

`git checkout src/zephyr/drift_detector/state_machine.py`
