---
task_id: "TASK-INF-0217"
source_blueprint: "MOD-INF-011"
source_section: "§12.4 回滚方案 + §12.5 施工完成标准"

title: "回滚方案执行矩阵 + 施工完成标准 11 项产出物清单验证"
description: |
  实现蓝图 §12.4 和 §12.5 的施工收尾:
  1. 回滚方案执行矩阵（§12.4）：为每个 Phase 定义精确的回滚触发条件和操作：
     - Phase 1 回滚：某模块集成失败 → 该模块降级为 skip（noop）+ 其他模块继续
     - Phase 2 回滚：迁移数据损坏 → 从 kb/ 旧 Collection 重新迁移 + BridgeLayer 回退到仅读 kb/
     - Phase 3 回滚：混合检索精度低于纯向量 → 切换为纯向量 + score threshold 收紧
     - Phase 4 回滚：HealthMonitor 错误清除了活跃数据 → 从 snapshot 恢复
  2. 施工完成标准验证器（§12.5）：逐个验证 11 项产出物 list：
     - 对每个产出物的完整绝对路径执行 exists=True + size>0 检查
     - 11 项产出物：in_process_vector_memory.py / embedding_router.py / chunk_strategy_router.py / hybrid_retriever.py / provenance_enforcer.py / index_health_monitor.py / cache_layer.py / bridge_layer.py / vector_bridge.py / retrieval_feedback.py / test_vector_memory.py
  3. 创建 phase_rollback.py 脚本——可针对性回滚任意 Phase
  4. 创建 build_completion_check.py 脚本——验证 11 项产出物完整性
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\vms_phase_rollback.py"
    description: "Phase 级别回滚执行器——rollback_phase(phase_num: int) → 按蓝图 §12.4 的矩阵执行精确回滚"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\vms_build_completion_check.py"
    description: "施工完成标准验证器——逐个检查蓝图 §12.5 的 11 项产出物是否完整存在且非空"

allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\vms_phase_rollback.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\vms_build_completion_check.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "scripts/governance/ 路径合规——治理脚本存放位置"
  - module_id: "GOV-TASK-005"
    section: "全篇"
    reason: "任务关闭三步法——施工完成标准验证是第三步"最终确认""

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§12.4 回滚方案表 + §12.5 施工完成标准清单——所有回滚操作 + 11 项产出物路径真源"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 7000
timeout_minutes: 30

acceptance_criteria:
  - "vms_phase_rollback.py rollback_phase(1) 遍历 Phase 1 产出物 → 全部正确回滚/降级"
  - "vms_phase_rollback.py rollback_phase(2) 回退迁移——切换 BridgeLayer 到 kb_only 模式"
  - "vms_phase_rollback.py rollback_phase(3) 切换 search 模式为 dense_only + score threshold 收紧"
  - "vms_phase_rollback.py rollback_phase(4) 从最新 snapshot 恢复"
  - "vms_build_completion_check.py 遍历 11 项产出物——全部返回 exists=True + size>0 → 输出 COMPLETE"
  - "vms_build_completion_check.py 如有任何产出物缺失 → 输出 INCOMPLETE + 缺失文件列表 + 对应蓝图 phase"

rollback_instructions: |
  1. 如果回滚脚本本身有问题（如回滚了不该回滚的 Phase）→ 手动确认每个 Phase 的回滚效果
  2. 删除构建完成检查脚本——撤销通过删除文件即可（不影响任何源文件）
  3. 回滚操作使用备份还原而非物理删除——Phase 级回滚保留旧文件为 .backup 副本

depends_on:
  - "TASK-INF-0216"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
  - "governance"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-011"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
