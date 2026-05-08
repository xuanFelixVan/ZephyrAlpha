---
module_id: KE-module_blu-2_2_ct-orc-script-001-003
title: 2.2 CT-ORC-SCRIPT-001：任务系统 ↔ 脚本系统
category: module_blueprint
---

# 2.2 CT-ORC-SCRIPT-001：任务系统 ↔ 脚本系统

2.2 CT-ORC-SCRIPT-001：任务系统 ↔ 脚本系统

```yaml
contract: CT-ORC-SCRIPT-001
title: "任务阻塞 + Finding → 任务卡自动创建"
systems:
  - role: producer
    name: script_system
    path: "scripts/governance/"
    blueprint: "MOD-INF-005"
  - role: consumer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-INF-006"

data_flow:
  direction: bidirectional
  script_to_orc:
    trigger: "脚本 exit 2 或 exit 3"
    payload: "FindingCollection { findings[], summary }"
    action: "Orc 将关联任务 status → BLOCKED"
    recovery: "脚本重跑 exit 0 → Orc 将关联任务 status → TODO"
  orc_to_script:
    trigger: "Finding.severity ∈ {CRITICAL, HIGH}"
    payload: "TaskCard { task_id, task_type: OPS, priority: P0/P1 }"
    action: "Script System 自动创建 OPS-{SEQ} 格式追踪任务卡"
    task_id_format: "OPS-{SEQ}"

state_propagation:
  - event: "script.exit_2"
    propagation:
      - target: "orchestrator.active_tasks"
        action: "status → BLOCKED"
        scope: "仅关联任务"
  - event: "script.exit_3"
    propagation:
      - target: "orchestrator.all_active_tasks"
        action: "status → BLOCKED"
        scope: "全部活跃任务（门禁自身故障 = 系统不可信）"
  - event: "finding.created{severity:CRITICAL|HIGH}"
    propagation:
      - target: "orchestrator.task_queue"
        action: "创建 OPS-{SEQ} 修复任务"
        task_fields:
          task_type: "OPS"
          priority: "P0 if CRITICAL else P1"
          parent_finding_id: "{finding.id}"

sla:
  CRITICAL_finding_response: "24h 内创建修复任务"
  HIGH_finding_response: "72h 内创建修复任务"
  gate_crash_recovery: "立即阻断所有活跃任务 + 通知 Owner"

ai_prompt: >
  你是CT-ORC-SCRIPT-001的AI agent。当脚本系统产出Findings时：
  (1) exit 2 → 仅阻断关联任务，不要阻断全局；
  (2) exit 3 → 这是门禁自身故障，必须阻断全部活跃任务+通知Owner——这是唯一触发全局阻断的场景；
  (3) CRITICAL/HIGH severity Finding → 自动创建OPS-{SEQ}任务卡，task_type=OPS，关联parent_finding_id；
  (4) MEDIUM Finding → 不创建任务卡，走CT-SCRIPT-KB-001入库流程；
  (5) 不要绕过CT-*直接import脚本系统内部模块（违反AP1）；
  (6) 任务BLOCKED后必须等待脚本重跑exit 0才能恢复→status: TODO，不要手动改状态。

telemetry:
  metrics:
    - {name: "script_exit_code", type: counter, labels: [exit_code, dimension]}
    - {name: "orc_blocked_tasks", type: gauge, labels: [trigger]}
    - {name: "finding_to_task_latency_s", type: histogram, buckets: [60,300,3600,86400]}
  traces:
    required_spans: ["script_execute", "finding_create", "orc_task_block", "orc_task_create"]
```
