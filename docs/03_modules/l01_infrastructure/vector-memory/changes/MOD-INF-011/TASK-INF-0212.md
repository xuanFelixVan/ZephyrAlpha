---
task_id: "TASK-INF-0212"
source_blueprint: "MOD-INF-011"
source_section: "§10 已知风险与缓解（R0-R15） + §10.1-10.4 四大类风险"

title: "16 项已知风险缓解落地——R0 蓝图漂移 + R1-R9 技术 + R10-R13 治理 + R14-R15 迁移"
description: |
  实现蓝图 §10 定义的 4 大类 16 项风险的缓解策略代码化：
  §10.1 蓝图-代码漂移风险：
  - R0: IndexHealthMonitor.detect_drift()——每次 VMS 启动时比对蓝图 §2 与 client.list_collections()，不一致 → 告警 + 写入 §5 known-drift 登记
  §10.2 技术风险：
  - R1: ChromaDB WAL mode + 写入队列（单写多读）+ 写入幂等（content fingerprint SHA256 判重）
  - R2: 模型预热 + 懒加载 + 512d 快速路径先行响应（已在 TASK-INF-0205 中实现）
  - R3: 混合检索 Vector(HNSW)+BM25+RRF 融合 + Phase 3 cross-encoder reranker + 嵌入模型版本追踪（已在 TASK-INF-0206 中实现）
  - R4: 定期 snapshot 备份 + 启动时完整性校验 + 可从源文件幂等重建（re-index）
  - R5: TTL 机制（execution_traces 30d, code_context/session_snapshots 90d）+ 热冷数据分离索引 + Auto-compaction
  - R6: 每个向量记录 embedding_model_version；升级时全量重嵌入 + 旧 Collection archive
  - R7: content fingerprint（sha256）为缓存 key；模型版本变更 → 自动 invalidate 全量缓存
  - R8: HealthMonitor cron 每日检查 TTL 过期记录数；过期未清理 → 告警 Owner
  - R9: 每次检索返回 RetrievalTrace 含 source_collection/score/rerank_info/embedding_model_version
  §10.3 治理风险：
  - R10: AI 自治级别绑定到 Collection（§2）；human-gated rules 不可 AI 修改；每次 Collection 操作 → CBAC 校验
  - R11: 统一通过 InProcessVectorMemory 单例访问；BridgeLayer 确保所有 IDE 进程共享同一 client 实例
  - R12: 写入前 input_sanitizer.py 扫描 secrets patterns；rules 和 knowledge 人类审查后才能写入
  - R13: 新增 Collection 须经 Owner 审批 + 更新蓝图 §2 + b_vector_memory.yaml SSoT
  §10.4 迁移风险：
  - R14: BridgeLayer 双读阶段（同时检索 kb/ 和 VMS）；迁移完成后 kb/ 标记 deprecated
  - R15: 拆分脚本先 dry-run 输出 topic→Collection 映射表；Owner 审核后执行
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cache_layer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\provenance_enforcer.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
    description: "追加 detect_drift() / snapshot_backup() / integrity_check() / check_ttl_expiry() / monitor_disk_growth()——覆盖 R0/R4/R5/R8"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cache_layer.py"
    description: "追加 invalidate_all_on_model_change() / fingerprint_based_key()——覆盖 R7"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\provenance_enforcer.py"
    description: "追加 cbau_check(collection, operation, ai_session) / ai_autonomy_gate()——覆盖 R10/R12"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
    description: "追加 dual_read_mode() / mark_deprecated_after_migration()——覆盖 R14/R15"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\vms_snapshot_backup.py"
    description: "ChromaDB snapshot 备份脚本——覆盖 R4 定期 snapshot 备份"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cache_layer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\provenance_enforcer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\vms_snapshot_backup.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0031"
    section: "全篇"
    reason: "ChromaDB 最佳实践——snapshot/backup/compaction 操作"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2——RiskMitigationStatus 模型"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§10 已知风险与缓解——4 大类 16 项风险的完整定义 + 缓解策略"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "IndexHealthMonitor.detect_drift() 比对蓝图 §2 Collection 列表与 ChromaDB actual collection → 返回 DriftReport"
  - "IndexHealthMonitor.integrity_check() 验证所有向量的维度与声称一致（V-VMS-433 同时也覆盖）"
  - "IndexHealthMonitor.check_ttl_expiry() 返回每个 Collection 的过期记录数 → 如有过期未清理告警"
  - "CacheLayer.invalidate_all_on_model_change() 检测模型版本变更 → 自动清空全部嵌入缓存"
  - "ProvenanceEnforcer.cbau_check() 拒绝 AI 修改 human-gated rules Collection"
  - "BridgeLayer.dual_read_mode() 同时检索 kb/ 和 VMS → 数据覆盖度 100%"
  - "vms_snapshot_backup.py 可独立执行 → 生成带时间戳的 snapshot 到 data/vector_db/_snapshots/"
  - "每个风险 R0-R15 在其对应模块中有明确的缓解代码路径——可在代码注释中找到 # mitigates R{n}"

rollback_instructions: |
  1. 如果 DriftReport 导致频繁误报告警 → 设置 VMS_DRIFT_CHECK=offline（仅在手动触发时运行）
  2. 还原各模块文件至 TASK-INF-0209 完成后的版本
  3. 删除 D:\ZephyrAlpha\scripts\governance\vms_snapshot_backup.py
  4. TTL 清理过于激进清除了需要的数据 → 延长 TTL 或从 snapshot 恢复

depends_on:
  - "TASK-INF-0209"
  - "TASK-INF-0207"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
  - "governance"
  - "security"
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
