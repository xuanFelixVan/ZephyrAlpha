---
task_id: TASK-OPS-0012
module_id: MOD-INF-005
title: "系统运维与自我监控落地 — §13 六项健康自检 + 应急回退 + 版本升级 + 定期演练"
status: TODO
priority: P0
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - self-monitoring
  - health-check
  - emergency-bypass
  - drills
description: |
  将蓝图 §13 的脚本系统运维与自我监控全量落地。
  
  覆盖子节：
  - §13.1 系统健康自检 6 项：run_all.py可执行 / 全脚本可运行 / manifest一致性 / 输出格式合规 / 依赖完整性 / 磁盘空间
  - §13.2 应急回退机制 3 场景：脚本崩溃 / 紧急热修复 / 批量迁移（均通过 git commit --no-verify 绕过）
  - §13.3 版本升级与兼容性：向后兼容 + 弃用公示期 + git revert 回滚
  - §13.4 定期应急演练 3 类：脚本故障/紧急绕过/恢复演练（月/季/季频率）

acceptance_criteria:
  - "validate_script_system_health.py 覆盖 6 项自检并在每次 pre-commit 运行"
  - "validate_emergency_bypass_log.py 能审计所有绕过记录——同一原因≥2次→告警"
  - "version_compatibility_matrix.yaml 记录 run_all.py 与 Plugin Contract 版本兼容关系"
  - "drill_schedule.yaml 定义演练日历——每月/每季自动提醒"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\validate_script_system_health.py"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\validate_emergency_bypass_log.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\drill_schedule.yaml"

rollback_instructions: "git checkout -- scripts/governance/meta/validate_emergency_bypass_log.py scripts/governance/meta/drill_schedule.yaml"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§13.1", "§13.2", "§13.3", "§13.4"]

phase: phase_2_extend
effort_estimate: M
risk_level: MEDIUM
depends_on_task: ["TASK-OPS-0011"]
blocks_task: ["TASK-OPS-0013"]
related_blind_spots: ["B66", "B76", "B100"]
related_risks: ["R2", "R5"]
related_contracts: []
card_type: implementation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed_review
---

# TASK-OPS-0012: 系统运维与自我监控落地 — §13 健康自检 + 应急回退 + 演练

## 1. 任务概述

蓝图 §13 定义了"审计的审计"——脚本系统自身的运维机制。validate_script_system_health.py 已实现，但急诊绕过审计和定期演练机制尚未脚本化。

## 2. 施工步骤

### Step 1: validate_emergency_bypass_log.py
新建 `D:\ZephyrAlpha\scripts\governance\meta\validate_emergency_bypass_log.py`：
- 扫描 Session Log 中所有 `--no-verify` 绕过记录
- 同一原因绕过 ≥2 次 → report HIGH Finding
- 7 天内 Emergency Bypass ≥3 次 → CRITICAL Finding（系统性故障）

### Step 2: drill_schedule.yaml
新建 `D:\ZephyrAlpha\scripts\governance\meta\drill_schedule.yaml`：
- 每月第 1 周：脚本故障演练
- 每季度第 1 个月：紧急绕过演练 + 恢复演练
- 演练后写 Session Log 复盘

### Step 3: 版本兼容管理
在 manifest schema 中新增 compatible_blueprint_version 字段（对标 B83）。

## 3. 验收标准
- [ ] validate_emergency_bypass_log.py 覆盖全部 Session Log
- [ ] drill_schedule.yaml 定义完整演练日历
- [ ] 应急绕过 ≥2 次 → exit 2 阻断
- [ ] 自检 6 项每周自动运行
