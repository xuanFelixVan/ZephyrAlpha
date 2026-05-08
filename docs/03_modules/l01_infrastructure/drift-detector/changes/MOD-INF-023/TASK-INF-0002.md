---
task_id: "TASK-INF-0002"
title: "核心引擎 drift_engine.py + 数据模型 drift_models.py 实现"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "8h"
actual_effort: null
assigned_to: null
created_by: "AI-Decomposer"
created_date: "2026-05-06"
updated_date: "2026-05-06"
depends_on: ["TASK-INF-0001"]
blocks: ["TASK-INF-0003","TASK-INF-0005","TASK-INF-0006"]
related_adrs: ["ADR-0022"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_engine.py"
acceptance_criteria:
  - "drift_models.py 包含所有数据类：DriftEvent（含11字段）、BaselineSnapshot（含tree_hash/interface_snapshot/import_graph/config_snapshot）、ScanResult、DriftReport、DriftBudget、Runbook、CascadeEvent、ForensicsReport、ConfigConflict、BreakingChange、OrphanFile"
  - "DriftEvent 使用 dataclass 或 Pydantic BaseModel，包含 event_id(UUID)/module_id/detector_id/drift_dimension/baseline_version/state/created_at/updated_at/resolved_by/resolution_detail/auto_fixed/rollback_verified"
  - "drift_engine.py 实现核心扫描循环：加载_detector_registry.yaml → 发现检测器 → 按scan_level调度 → 汇总ScanResult → 批量写入drift_events → 返回DriftReport"
  - "drift_engine.py 支持 scan(level=ScanLevel.LIGHT|STANDARD|DEEP, scope: Optional[list[str]] = None)"
  - "所有类型注解完整，无 Any 逃逸"
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_models.py src/zephyr/drift_detector/drift_engine.py 恢复原始版本。"
context_assembly_manifest:
  - file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
    sections: ["§2.1","§2.3","§2.4","§2.5","§5.1","§7"]
tags: ["drift-detector","core-engine","data-models","implementation"]
compliance_tags: ["GOV-DOC-002"]
risks:
  - risk_id: "R-INF-023-01"
    description: "数据模型字段与blueprint §2.3 drift_events未完全对齐"
    impact: "state_machine无法正确读写状态"
    likelihood: "medium"
    mitigation: "逐字段对照 §2.3 drift_events fields 清单，生成字段对齐矩阵"
    owner: "TASK-INF-0002执行者"
---

# TASK-INF-0002: 核心引擎 + 数据模型实现

## 目标

实现 drift-detector 的核心数据模型 `drift_models.py`（包含12个数据类）和核心引擎 `drift_engine.py`（检测器发现→调度→汇总→写入的完整扫描循环）。对标 blueprint.md §2.1（检测器注册表）、§2.3（漂移状态机数据表）、§2.4（三级扫描）、§5.1（时序存储）。

## 触发条件

- TASK-INF-0001 完成（模块骨架存在）
- `_detector_registry.yaml` 已被填充检测器注册条目

## 执行步骤

### Step 1: 实现 drift_models.py

按 blueprint.md §7 定义实现以下数据模型：

| 类名 | 核心字段 | 来源 |
|------|---------|------|
| `DriftEvent` | event_id(UUID), module_id, detector_id, drift_dimension, baseline_version, state, created_at, updated_at, resolved_by, resolution_detail, auto_fixed, rollback_verified | §2.3 |
| `BaselineSnapshot` | version, tree_hash(dict), interface_snapshot(dict), import_graph(dict), config_snapshot(dict) | §2.2 |
| `ScanResult` | scan_id, detectors_run(int), total_drift_events(int), new_events, resolved_events, storm_mode_triggered | §2.4 |
| `DriftReport` | module_health_index, top_drift_dimensions, active_drift_count, scan_summary | §5.3 |
| `DriftBudget` | module_id, tier, monthly_budget, consumed, remaining, hard_limit_reached | §2.9 |
| `Runbook` | event_id, metadata, diagnosis, remediation, rollback, references | §6.9 |
| `CascadeEvent` | module_id, trigger_count, repair_loop_events, cascade_lock_until | §6.15 |
| `ForensicsReport` | event_id, timeline, state_diffs, actor_trace, dependency_impact | §6.17 |
| `ConfigConflict` | key_name, env_source_value, yaml_source_value, hardcoded_default_value | §6.21 |
| `BreakingChange` | api_signature, field_path, old_definition, new_definition, impacted_modules | §6.23 |
| `OrphanFile` | file_path, classification(true_orphan/undocumented_asset/stale_artifact), last_modified, suggestion | §2.16 |

使用 `@dataclass` 或 `pydantic.BaseModel`，所有字段带类型注解，时间字段使用 `datetime`，状态字段使用 `Enum`。

### Step 2: 实现 ScanLevel 枚举

```python
from enum import Enum, auto

class ScanLevel(Enum):
    LIGHT = auto()    # "< 5s" SLO
    STANDARD = auto() # "< 30s" SLO
    DEEP = auto()     # "< 5min" SLO
```

### Step 3: 实现 drift_engine.py

核心功能：
1. **`load_detector_registry()`**：读取 `_detector_registry.yaml`，返回 Detector 对象列表
2. **`scan(level: ScanLevel, scope: list[str] | None = None)`**：执行扫描
   - LIGHT：只扫描 git diff 涉及的检测器
   - STANDARD：HIGH severity 检测器
   - DEEP：全部检测器
3. **`_dispatch_detector(detector, files)`**：`asyncio.create_subprocess_exec` 运行检测器脚本，收集 stdout JSON
4. **`_write_drift_events(events)`**：批量 INSERT INTO drift_events（SQLite 事务）
5. **`_build_report(results)`**：汇总 ScanResult → DriftReport

## 验收标准

- `drift_models.py` 包含所有12个数据类，每个类字段与blueprint对应章节一致
- `DriftEvent` 包含全11字段：event_id, module_id, detector_id, drift_dimension, baseline_version, state, created_at, updated_at, resolved_by, resolution_detail, auto_fixed, rollback_verified
- `drift_engine.py` 支持 `scan(level=ScanLevel)`，三个级别行为各异
- 所有类型注解完整，无 `Any` 逃逸
- `_dispatch_detector` 使用 asyncio subprocess pool

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 数据模型字段与blueprint §2.3未对齐 | 逐字段对照 §2.3 drift_events fields 清单，生成字段对齐矩阵 |
| asyncio subprocess 异常处理不完整 | 每个 detector 执行包裹 try/except + timeout(SLO) |

## 回滚指令

`git checkout src/zephyr/drift_detector/drift_models.py src/zephyr/drift_detector/drift_engine.py` 恢复原始版本。
