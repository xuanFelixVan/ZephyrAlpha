---
task_id: "TASK-INF-0001"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §1 概述 + §3 九子系统"

# ===== 内容 =====
title: "搭建 L12 System Telemetry 模块目录骨架与九子系统初始化"
description: |
  创建所有九个子系统的目录结构和 __init__.py 骨架文件，
  确保模块可被 import。九个子系统：metrics, logs, traces, ai_behavior, archive, profiles, health, alerts, schema。
  每个 __init__.py 包含模块级 docstring 描述职责。
priority: "P0"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\__init__.py"
    description: "根包入口——导出 Telemetry 门面类"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\__init__.py"
    description: "metrics 子系统骨架"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\logs\\__init__.py"
    description: "logs 子系统骨架"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\traces\\__init__.py"
    description: "traces 子系统骨架"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\ai_behavior\\__init__.py"
    description: "ai_behavior 子系统骨架"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\archive\\__init__.py"
    description: "archive 子系统骨架"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\profiles\\__init__.py"
    description: "profiles 子系统骨架——新建"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\health\\__init__.py"
    description: "health 子系统骨架——新建"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\alerts\\__init__.py"
    description: "alerts 子系统骨架——新建"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\schema\\__init__.py"
    description: "schema 子系统骨架——新建"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\**\\__init__.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\*.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "路径防幻觉映射——src/zephyr/l12_system_telemetry/ 为 C 轨 L12 层代码物理位置"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规创建——AI 不得自主决定目录层级"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2 强制"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§1 概述 + §3 九子系统描述——了解每个子系统的职责和目录位置"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
    reason: "§5.1.2 路径映射——确认 l12_system_telemetry 物理目录规则"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 3000
timeout_minutes: 15

# ===== 验收标准 =====
acceptance_criteria:
  - "l12_system_telemetry/ 根目录下 __init__.py 存在且包含模块级 docstring"
  - "全部 9 个子系统目录（metrics/logs/traces/ai_behavior/archive/profiles/health/alerts/schema）均存在"
  - "每个子系统的 __init__.py 包含模块级 docstring 描述职责"
  - "所有路径符合 GOV-DOC-002 §5.1.2 路径映射"
  - "所有文件编码 UTF-8"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\profiles\__init__.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\health\__init__.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\alerts\__init__.py
  4. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\schema\__init__.py
  5. 还原已修改的已有 __init__.py 文件（git checkout）

# ===== 依赖 =====
depends_on: []
blocked_by: []

# ===== 状态 =====
status: "done"

# ===== 五轴标签 =====
tags_fn:
  - "infra"
  - "observability"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-015"

# ===== 门禁 =====
completed_gates: []
blocked_gates: {}

# ===== 产物 =====
artifact_paths: []

# ===== 审计 =====
audit_findings: []

# ===== 知识 =====
ke_entries: []

# ===== AI 自治 =====
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# TASK-INF-0001: 搭建 L12 System Telemetry 模块目录骨架与九子系统初始化

## 目标
创建 L12 System Telemetry 的完整物理目录结构，为九个子系统（metrics/logs/traces/ai_behavior/archive/profiles/health/alerts/schema）各创建 __init__.py 骨架文件，确保模块可被 import 且职责明确。

## 触发条件
- 蓝图 MOD-INF-015 已存在且 §3 已定义九子系统
- GOV-DOC-002 目录结构标准已就绪

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\system-telemetry\blueprint.md` §1 + §3
- `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\directory-structure-standard.md` §5.1.2

### 做
1. 确认 `src/zephyr/l12_system_telemetry/` 根包存在（含 `__init__.py`）
2. 为尚未创建的 4 个子系统创建目录：profiles/health/alerts/schema
3. 为每个新建子系统的 `__init__.py` 写入模块级 docstring（描述职责、参考蓝图对应小节）
4. 检查已有子系统的 `__init__.py` 是否包含足够的职责说明

### 产
- 4 个新建 `__init__.py` 文件（profiles/health/alerts/schema）
- 确认已有 5 个子系统文件完整

### 检
```bash
python -c "from zephyr.l12_system_telemetry import metrics, logs, traces, ai_behavior, archive, profiles, health, alerts, schema; print('ALL_OK')"
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | files | 9 个子系统目录 + __init__.py 全部存在 |
| 2 | build | `python -c "import zephyr.l12_system_telemetry"` 无错误 |
| 3 | lint | 0 errors, 0 warnings |
| 4 | diff | 仅新建 profiles/health/alerts/schema 四个目录及其 __init__.py |

## 风险与缓解
| 风险 | 缓解 |
|------|------|
| 目录已存在 → 覆盖写入 | 检查已有文件内容后再写入，保留现有实现 |
| 违反 GOV-DOC-002 路径规范 | 对照 §5.1.2 路径映射逐个验证 |
