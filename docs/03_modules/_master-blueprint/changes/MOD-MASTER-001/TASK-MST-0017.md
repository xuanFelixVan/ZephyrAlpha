---
task_id: "TASK-MST-0017"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §十八 Bulkhead + Watchdog + Backup——CT-BULKHEAD-001/CT-WATCHDOG-001/CT-BACKUP-001"

title: "实现 Bulkhead 资源池隔舱 + 三冗余 Watchdog + 备份恢复体系"
description: |
  实现 §十八 定义的运维韧性三层契约：
  (1)CT-BULKHEAD-001 Bulkhead 资源池隔舱——12系统独立资源池(线程数+SQLite连接+内存上限)；
  (2)CT-WATCHDOG-001 三冗余监视者——3个独立watchdog互检→≥2个30分钟无心跳→Panic Mode；
  (3)CT-BACKUP-001 数据备份与恢复——SQLite daily VACUUM INTO + ChromaDB daily zip + 30d/12m/Ny retention。
  Slow call detection: p99 > 5s → 隔离该系统线程 → degraded response → 超时→强制终止。
  Shared pools: SQLite WAL max 5 connections(FIFO 5s timeout) + ChromaDB HTTP max 3 connections(FIFO 3s timeout)。
  Dead man's switch: 每10分钟写入外部heartbeat文件 → Owner cron每分钟检查 → >30min无更新→ALERT。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\bulkhead_manager.py"
    description: "Bulkhead 资源池管理器——12系统独立线程池+内存隔离"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\telemetry\\watchdog.py"
    description: "三冗余 Watchdog——互检+Panic Mode触发+Dead Man's Switch"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\backup_manager.py"
    description: "备份管理器——SQLite VACUUM INTO + ChromaDB zip + integrity check"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_bulkhead_manager.py"
    description: "Bulkhead 管理器单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_watchdog.py"
    description: "Watchdog 单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\bulkhead_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\telemetry\\watchdog.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\backup_manager.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_bulkhead_manager.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_watchdog.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "§十八——CT-BULKHEAD-001/CT-WATCHDOG-001/CT-BACKUP-001 完整定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "bulkhead_manager.py 为 12 系统创建独立资源池（thread_pool/SQLite connections/memory_limit）"
  - "Shared pools: SQLite WAL max 5 connections FIFO 5s timeout + ChromaDB max 3 connections FIFO 3s timeout"
  - "watchdog.py 实现 3 个独立 watchdog 互检 + ≥2个 30min 无心跳 → Panic Mode"
  - "Dead man's switch: 每10分钟写 heartbeat 文件 → Owner cron 检查 → >30min无更新 ALERT"
  - "backup_manager.py 每日 03:00 SQLite VACUUM INTO + 04:00 ChromaDB zip → 备份后 integrity check"
  - "restore 流程: 关闭12系统 → 替换 db/chroma → 重启 → CT-RECONCILE-001 自动修复"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除新增的 3 个源码文件
  2. 删除新增的测试文件
  3. 清理 backup/ 目录下的测试备份文件

depends_on: ["TASK-MST-0015"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-MASTER-001"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
