---
task_id: "TASK-INF-0216"
source_blueprint: "MOD-INF-011"
source_section: "§12.3 Phase 3：检索质量闭环 + Phase 4：运维自动化"

title: "Phase 3-4 施工——检索质量闭环(HybridRetriever/Reranker/FLE反馈) + 运维自动化(TTL/Compaction/Snapshot/告警)"
description: |
  执行蓝图 §12.3 Phase 3（检索质量闭环）和 Phase 4（运维自动化）的联合施工：
  Phase 3 检索质量闭环：
  1. HybridRetriever 全功能启用——Vector(HNSW)+BM25+RRF 融合 + score threshold 0.6
  2. 可插拔 reranker 接入（cross-encoder BGE-Reranker-v2-m3 二次精排）
  3. RetrievalFeedback 接入 FLE pipeline——FLE 记录检索反馈信号 + 反馈信号影响检索排序
  4. CrossCollectionRetriever——跨 Collection 联合检索 + 合并排序
  5. 验收：混合检索 top-5 精度 > 纯向量 top-5 + FLE 可记录检索反馈 + RRF 融合正确 + RetrievalTrace 可解释
  Phase 4 运维自动化：
  6. TTL cron 每日检查——自动清理过期 execution_traces(30d) / code_context(90d) / session_snapshots(90d)
  7. Auto-compaction——定期 ChromaDB HNSW 索引压缩
  8. Snapshot 自动备份——定期 > 异常恢复
  9. 异常告警——IndexHealthMonitor 检测到异常 → 通知 Owner
  10. 验收：每日自动 TTL 清理 + compaction + 异常告警 + 30 天无手动维护自愈率 > 95%
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\retrieval_feedback.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cross_collection_retriever.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\vms_snapshot_backup.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"
    description: "Phase 3 全功能版——reranker 插件接口 + RRF 精调 + 检索质量统计"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\retrieval_feedback.py"
    description: "Phase 3 全功能版——FLE hook 回调注册 + 反馈信号写入排序权重"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cross_collection_retriever.py"
    description: "Phase 3 全功能版——跨 Collection 联合检索 + 多源结果合并排序 + API search_across()"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\vms_health_check.py"
    description: "Phase 4 cron 脚本——每日 TTL 清理 + compaction + snapshot 备份 + 健康检查 + 异常告警"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_vector_memory.py"
    description: "Phase 3-4 测试——hybrid_vs_dense_comparison / feedback_integration / cross_collection_search / ttl_cleaning"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\retrieval_feedback.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cross_collection_retriever.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\vms_health_check.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_vector_memory.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"

applicable_rules:
  - module_id: "ADR-0016"
    section: "§3"
    reason: "CrossEncoder (BGE-Reranker-v2-m3) 重排序规范——Phase 3 reranker 集成"
  - module_id: "GOV-TASK-005"
    section: "全篇"
    reason: "关闭三步法——Phase 3-4 各阶段独立关闭验收"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§12.3 Phase 3 + Phase 4 完整定义——检索闭环 + 运维自动化验收标准/G7 检查项"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
  - "M4"
estimated_tokens: 20000
timeout_minutes: 90

acceptance_criteria:
  - "混合检索 top-5 精度 > 纯向量 top-5——在有 ground truth 的 50 条测试集上验证"
  - "RRF 融合正确——fused score 由 dense rank 和 sparse rank 通过公式 Σ(1/(60+rank_i)) 计算"
  - "RetrievalTrace 可解释——包含 score_breakdown / source_collection / embedding_model_version"
  - "RetrievalFeedback FLE hook 正常——FLE 调用 retrieval_feedback.record() → 写入反馈记录"
  - "CrossCollectionRetriever.search_across('旧模式出现过吗？', [lessons, execution_traces, decisions], k=5) → 返回跨 Collection 混合结果"
  - "vms_cron_monitor.py 每日自动 TTL 清理——execution_traces 超过 30d 的数据被清理"
  - "vms_cron_monitor.py 每日 compaction——HNSW 索引压缩"
  - "vms_cron_monitor.py 每日 snapshot 备份——_snapshots/ 下有 timestamped backup"
  - "vms_cron_monitor.py 异常告警——IndexHealthMonitor 检测到异常时输出日志 + 建议动作"

rollback_instructions: |
  1. Phase 3 混合检索精度低于纯向量 → 切换为纯向量模式 + score threshold 收紧 + 关闭 BM25 通道
  2. Phase 4 HealthMonitor 错误清除了活跃数据 → 从 _snapshots/ 恢复最新备份
  3. 还原各文件至 Phase 2 完成后的版本
  4. 禁用 cron 脚本：设置 VMS_CRON_ENABLED=False
  5. 如检索质量退化 → TTL 延长 + Compaction 回滚

depends_on:
  - "TASK-INF-0215"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
  - "data"
  - "observability"
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
