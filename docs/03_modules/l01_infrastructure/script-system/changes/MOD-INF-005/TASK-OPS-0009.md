---
task_id: TASK-OPS-0009
module_id: MOD-INF-005
title: "容量估算与 SLA/SLO 指标落地 — §8 容量上限 + 扩展触发 + 6项 SLA/SLO 度量采集"
status: TODO
priority: P1
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - capacity
  - sla
  - slo
  - metrics
description: |
  将蓝图 §8 的容量估算和 SLA/SLO 度量体系落地为可采集和可告警的指标。
  
  覆盖子节：
  - §8.1 当前规模：177 脚本 / 12 维度 / D5=45 / D10=0
  - §8.2 容量上限设计：单维度 ≤50、全局 ≤300、每周Finding ≤500、pre-commit ≤10钩子、全局超时 600s
  - §8.3 扩展触发条件：单维≥8→审查 / 全局≥150→审查 / 扫描≥300s→审查
  - §8.4 SLA/SLO 度量指标 6项：可用性 ≥99% / MTTR ≤24h(CRITICAL)≤72h(HIGH) / 覆盖率 100% / 假阳性率 ≤5% / 门禁阻断率 ≤2% / 脚本健康度 100%

acceptance_criteria:
  - "run_all.py 每次扫描后自动追加 sla_metrics.jsonl——含 timestamp/scan_type/total_findings/critical_count/high_count/scan_duration_s/exit_code"
  - "每周统计脚本可计算6项 SLA/SLO——输出到 meta/sla_weekly_report.json"
  - "容量上限触发时 status.py --json 输出 WARNING"
  - "D10 维度空缺在 status.py 中标记 dimension_vacant"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\_shared\\thresholds.yaml"
  - "D:\\ZephyrAlpha\\scripts\\governance\\status.py"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\sla_metrics.jsonl"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\compute_sla_metrics.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\status.py"

rollback_instructions: "git checkout -- scripts/governance/status.py scripts/governance/meta/compute_sla_metrics.py"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§8.1", "§8.2", "§8.3", "§8.4"]

phase: phase_2_extend
effort_estimate: M
risk_level: LOW
depends_on_task: ["TASK-OPS-0008"]
blocks_task: ["TASK-OPS-0010"]
related_blind_spots: ["B70", "B90", "B91"]
related_risks: []
related_contracts: []
card_type: implementation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed_review
---

# TASK-OPS-0009: 容量估算与 SLA/SLO 指标落地 — §8 容量上限 + SLA采集

## 1. 任务概述

蓝图 §8.4 定义的 6 项 SLA/SLO 指标当前均为"待测量"状态。§34.4 已指出此风险——最小落地方式是 run_all.py 每次扫描后自动追加 JSONL 行 + 每周统计脚本。

## 2. 施工步骤

### Step 1: sla_metrics.jsonl 自动采集
在 run_all.py 中集成：扫描完成后自动追加到 `meta/sla_metrics.jsonl`：
```json
{"timestamp": "2026-05-06T15:30:00+08:00", "scan_type": "full", "total_findings": 47,
 "critical_count": 0, "high_count": 3, "scan_duration_s": 48.2, "exit_code": 1}
```

### Step 2: compute_sla_metrics.py
新建 `D:\ZephyrAlpha\scripts\governance\meta\compute_sla_metrics.py`：
- 读取 sla_metrics.jsonl
- 计算 6 项 SLA/SLO 指标
- 输出到 `meta/sla_weekly_report.json`
- 任一指标低于阈值 → exit 1 警告

### Step 3: status.py 容量告警
status.py --json 输出中增加容量告警：
- 单维度脚本数接近上限 → WARNING
- 全局脚本数接近上限 → WARNING
- 扫描耗时接近 300s → WARNING

## 3. 验收标准
- [ ] run_all.py 每次扫描自动追加 sla_metrics.jsonl
- [ ] compute_sla_metrics.py 可执行且输出结构化 JSON
- [ ] status.py --json 输出容量上限告警
- [ ] 当前 6 项指标从"待测量"→"已测量"（有实际数值）
