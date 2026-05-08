---
task_id: "TASK-INF-0011"
title: "崩溃恢复与检查点机制实现（D-023-17）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
blocks: []
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_engine.py"]
acceptance_criteria:
  - "per-detector checkpoint: scan_id/completed_detectors/last_checkpoint_time/scan_start_time → JSONL到data/drift_checkpoints/<scan_id>.json"
  - "每次detector完成后立即fsync写入checkpoint"
  - "on_startup扫描未完成scan_id → 从剩余detector继续执行 → scan完成删除checkpoint"
  - "staleness: checkpoint >24h未恢复 → ORPHANED → 通知Owner"
  - "SQLite事务安全: 每detector结果在单个事务中写入drift_events；进程崩溃→WAL自动回滚"
  - "graceful_shutdown: SIGTERM/SIGINT → 完成当前detector → 写checkpoint → 退出(max_wait=30s)"
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§2.10"]}]
tags: ["drift-detector","crash-recovery","checkpoint","D-023-17"]
---

# TASK-INF-0011: 崩溃恢复与检查点（D-023-17）

## 目标
在 drift_engine.py 中实现 per-detector 检查点机制和 SQLite 事务安全。对标 blueprint §2.10。

## 执行步骤
1. `CheckpointWriter`: 每个detector完成后fsync写入 checkpoint JSON，含scan_id/completed_detectors列表/timestamp
2. `RecoveryManager.on_startup()`: 扫描 data/drift_checkpoints/ → 发现未完成scan → 加载completed列表 → 继续执行
3. 每个detector结果用单个SQLite事务写入drift_events（WAL模式自动回滚）
4. 信号处理：`signal.signal(SIGTERM, graceful_shutdown)` → 30s内完成当前detector+写checkpoint

## 验收标准
- checkpoint写入和恢复功能正常
- 模拟进程崩溃后重启可从断点恢复
- checkpoint >24h标记ORPHANED
