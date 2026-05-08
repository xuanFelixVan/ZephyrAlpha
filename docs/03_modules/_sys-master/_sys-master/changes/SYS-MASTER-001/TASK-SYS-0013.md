---
task_id: "TASK-SYS-0013"
source_blueprint: "SYS-MASTER-001"
source_section: "§18 灾难恢复 + §92 热重启 + §94 硬件容灾"

title: "灾难恢复 RPO≤1h/RTO≤30min + 热重启6步协议(Freeze→Resume) + 硬件5维容灾(SMART/电源/散热/磁盘/内存)体系"
description: |
  将 SYS-MASTER-001 §18 灾难恢复 + §92 热重启 + §94 硬件容灾合并落地。
  §18: RPO ≤ 1小时 / RTO ≤ 30分钟。三级备份策略（全量+增量+WAL）。
  DR Drill 按预定日历执行，每次演练后 Qtest validation。
  §92: 热重启 6 步协议——Step1-Freeze Check(<2s)→Step2-State Reconciliation(<5s)→
  Step3-Connection Recovery(<10s)→Step4-Position Sync(<5s)→Step5-Fast Forward(<5s)→
  Step6-Resume(<3s)。冷启动≤60s vs 热重启≤30s。
  §94: 硬件 5 维容灾——SSD SMART监控/内存 memtest/电源 UPS≥30min/散热 CPU<85°C/磁盘空间自动清理。
  每日 06:30 自动硬件健康检查。
  本卡搭建 dr_manager.py + hot_restart.py + hardware_health.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\dr_manager.py"
    description: "§18 RPO≤1h/RTO≤30min + 3级备份 + DR Drill日历 + Qtest validation"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\hot_restart.py"
    description: "§92 热重启6步——Freeze→Reconcile→Connect→Sync→FastForward→Resume (total≤30s)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\hardware_health.py"
    description: "§94 5维硬件容灾——SMART/内存/电源/散热/磁盘——每日06:30自动检查"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\dr_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\hot_restart.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\hardware_health.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§18 RPO/RTO+DR Drill + §92 HotRestart 6步≤30s + §94 Hardware 5维 SMART检查 06:30"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 20000
timeout_minutes: 55

acceptance_criteria:
  - "dr_manager.py DRPolicy: rpo_minutes=60, rto_minutes=30, backup_tiers[3], drill_calendar + Qtest validation"
  - "hot_restart.py HotRestartProtocol 6 steps: freeze(2s)→reconciliation(5s)→connection(10s)→sync(5s)→fastforward(5s)→resume(3s)——total≤30s"
  - "hardware_health.py Daily06:30 cron: SMART(ReallocatedSectors/WearLevel/Temp)/Memory(last memtest<30d)/Power(UPS>15min)/Thermal(CPU<80°C,GPU<80°C)/Disk(>90%→警告)"
  - "script_manifest.yaml 注册"

rollback_instructions: |
  git rm src/zephyr/governance/dr_manager.py hot_restart.py hardware_health.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0009"
blocked_by: []
status: "created"
tags_fn:
  - "ops"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
