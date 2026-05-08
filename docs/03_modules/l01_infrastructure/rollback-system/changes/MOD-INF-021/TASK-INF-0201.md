---
task_id: "TASK-INF-0201"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 1.1 + §2.1 + §6.2 B1/B3 + 决策 D-021-01 + D-021-04"

title: "数据模型统一决议实施——git-native + SQLite dump 双轨 Checkpoint"
description: |
  实施双轨数据模型：git-native 文件层 checkpoint（决策 D-021-01）+ SQLite dump JSONL 数据库层 checkpoint（决策 D-021-04）。
  废弃 rollback_manager.py 的 DB-only checkpoint 作为独立回滚路径，降级为仅调试用途。
  实现 sqlite_dumper.py——pre-commit hook 中 dump SQLite schema+data 到 JSONL。
  实现 checkpoint_strategy YAML 配置——定义双轨协作协议。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\rollback_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\sqlite_dumper.py"
    description: "SQLite dump 工具——schema+data → JSONL（Merkle 树签名 + HMAC）/ JSONL → 重建 SQLite + 完整性验证"
  - path: "D:\\ZephyrAlpha\\data\\rollback\\rollback_checkpoint_strategy.yaml"
    description: "双轨 Checkpoint 策略声明——文件层+DB层协作协议"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "回滚执行器——整合双轨回滚操作(file_revert + db_rebuild)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\rollback_manager.py"
    description: "降级标记——仅保留为调试场景的手动 DB 快照"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\sqlite_dumper.py"
  - "D:\\ZephyrAlpha\\data\\rollback\\rollback_checkpoint_strategy.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\rollback_manager.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——所有模型基座"
  - module_id: "PS-STD-011"
    section: "MTH-012"
    reason: "涌现式设计——双轨决议后创建文件前先验证决策是否与已有代码一致"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§2.1 双轨 Checkpoint 定义 + §6.2 B1/B3 结构性冲突描述 + D-021-01/D-021-04 决策"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\rollback_manager.py"
    reason: "已有代码——了解 checkpoint()/rollback_to()/list_checkpoints() 现有实现"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 45

acceptance_criteria:
  - "sqlite_dumper.py 实现 dump(schema+data→JSONL) + restore(JSONL→SQLite) + verify(Merkle+HMAC)"
  - "rollback_executor.py 调用 sqlite_dumper 完成双轨回滚"
  - "rollback_checkpoint_strategy.yaml 声明 file_layer(git commit=checkpoint) + db_layer(SQLite dump→JSONL→git track)"
  - "rollback_manager.py 降级标记——docstring 显式声明 '仅调试用途，不用于自动回滚'"
  - "JSONL dump 输出格式：第一行元数据头 + 每行一条记录 + 末尾 Merkle 根"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\sqlite_dumper.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\rollback\rollback_executor.py（如仅含双轨回滚逻辑）
  3. 删除 D:\ZephyrAlpha\data\rollback\rollback_checkpoint_strategy.yaml
  4. 恢复 D:\ZephyrAlpha\src\zephyr\orchestrator\rollback_manager.py 到原始状态（git checkout HEAD~1）
  5. 如有生成的 JSONL 测试文件，删除 data/rollback/db_snapshots/ 下的测试数据

depends_on:
  - "TASK-INF-0200"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-021"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
