---
task_id: "TASK-INF-0007"
title: "检测触发策略与维护窗口实现（D-023-06）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002","TASK-INF-0006"]
blocks: ["TASK-INF-0028"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_engine.py"  # 追加触发逻辑
acceptance_criteria:
  - "5种触发类型实现：post_commit(LIGHT <5s)、periodic_light(每30min STANDARD)、periodic_deep(每6h DEEP)、on_demand(MCP Tool/Owner手动)、phase_gate(complete触发DEEP+基线)"
  - "maintenance_window: Owner声明窗口冻结→shadow mode(检测不阻断)；自动检测>50 files changed→自动shadow mode 2h"
  - "per-detector per-module 漂移抑制：标记SUPPRESSED含expires_at；过期自动恢复DETECTED"
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest:
  - file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
    sections: ["§2.6"]
tags: ["drift-detector","trigger","maintenance-window","D-023-06"]
compliance_tags: ["GOV-DOC-002"]
risks: []
---

# TASK-INF-0007: 触发策略与维护窗口实现（D-023-06）

## 目标

在 drift_engine.py 中追加 5 种触发策略和维护窗口/shadow mode/漂移抑制机制。对标 blueprint §2.6。

## 执行步骤

### Step 1: 5 种触发类型

| 触发 | 方法 | scope | scan_level | latency |
|------|------|-------|------------|---------|
| post_commit | `scan_on_commit(files)` | affected+依赖 | LIGHT | <5s |
| periodic_light | `scheduled_light()`每30min | global | STANDARD | <30s |
| periodic_deep | `scheduled_deep()`每6h | global | DEEP | <5min |
| on_demand | `scan(level, scope)` | 指定 | 参数决定 | 取决于level |
| phase_gate | `scan_phase_gate(module_id)` | 目标模块 | DEEP | 基线+全量 |

### Step 2: 维护窗口

- `MaintenanceWindow`: start_time, end_time, is_shadow_mode
- shadow mode: 检测但不阻断门禁、不触发告警、结果仅记录
- 自动检测：`git diff --stat HEAD~1 | wc -l > 50` → 自动进入 shadow mode 2h

### Step 3: 漂移抑制

- `suppress(detector_id, module_id, expires_at)`: 标记 SUPPRESSED
- `unsuppress_on_expiry()`: 定时扫描过期的 SUPPRESSED → DETECTED

## 验收标准

- 5种触发类型均可独立执行
- 维护窗口声明生效（shadow mode 不告警不阻断）
- 自动大diff检测触发 shadow mode
- 抑制/过期恢复机制工作正常
