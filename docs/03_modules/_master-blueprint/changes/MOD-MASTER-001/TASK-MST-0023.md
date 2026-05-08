---
task_id: "TASK-MST-0023"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §二十四 边界情况防护——CT-DISK-GUARD-001/CT-NETWORK-PARTITION-001"

title: "实现磁盘空间耗尽防护 + 网络分区容忍——CT-DISK-GUARD-001/CT-NETWORK-PARTITION-001"
description: |
  实现 §二十四 定义的边界情况双防护：
  (1)CT-DISK-GUARD-001 磁盘空间耗尽防护——每次写操作(dlq/sqlite/chromadb)前检查可用空间(<100MB→拒绝)+ ALERT；
  atomic writes: 所有写操作使用 tempfile+os.replace/atomic rename；
  emergency reserve: 保留 200MB 用于 emergency_log + Owner 飞书；
  (2)CT-NETWORK-PARTITION-001 网络分区容忍——每 60s HEAD api.openai.com + api.anthropic.com 检测分区；
  dual_offline > 60s → offline_mode: 暂停LLM任务→QUEUED、所有CT-* LLM调用返回 degraded、本地任务继续；
  recovery: dual_online恢复→FIFO恢复QUEUED任务、分区期间Finding已写入SQLite→无数据丢失。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\disk_guard.py"
    description: "磁盘防护——CT-DISK-GUARD-001——pre_write_check+atomic_writes+emergency_reserve"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\network_partition.py"
    description: "网络分区检测器——CT-NETWORK-PARTITION-001——dual API探测+offline_mode+recovery"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_disk_guard.py"
    description: "磁盘防护单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_network_partition.py"
    description: "网络分区检测器单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\disk_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\network_partition.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_disk_guard.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_network_partition.py"

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
    reason: "§二十四——CT-DISK-GUARD-001 + CT-NETWORK-PARTITION-001 完整定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 10000
timeout_minutes: 45

acceptance_criteria:
  - "disk_guard.py: 每次写 SQLite/ChromaDB/FS 前检查可用空间 → <100MB 拒绝写入+ALERT"
  - "atomic writes: write to .tmp → fsync → os.replace / SQLite WAL atomic commit"
  - "emergency_reserve: 保留 200MB 仅用于 emergency_log+飞书通知 → 禁止被普通写入消耗"
  - "network_partition.py: 每 60s HEAD 双 API → dual_offline>60s → offline_mode"
  - "offline_mode: LLM任务→QUEUED / CT-* LLM→degraded / 本地任务(Script/Gates/HealthCheck)继续"
  - "recovery: dual_online→FIFO恢复QUEUED任务 → offline_duration_minutes 计算"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\disk_guard.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\network_partition.py
  3. 删除新增的测试文件

depends_on: []
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
