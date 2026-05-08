---
task_id: "TASK-INF-0218"
source_blueprint: "MOD-INF-011"
source_section: "§13 深度交叉审计盲点全注入 R1——10大维度33盲点 (V-VMS-401~433)"

title: "R1 盲点关闭——33 项检索质量/索引管理/数据一致性/性能/氛围编程/安全/运维/集成/成本/测试盲点"
description: |
  关闭蓝图 §13 第一轮审计产生的全部 33 个盲点 (V-VMS-401 ~ V-VMS-433)：
  A. 检索质量与评估 (4): V401 无benchmark / V402 无MMR / V403 无查询改写 / V404 无意图分类
  B. 索引管理 (4): V405 无向量量化 / V406 无HNSW调优 / V407 无新鲜度SLA / V408 无重建自动化
  C. 数据一致性 (4): V409 无去重 / V410 无overlap / V411 无过时检测 / V412 无统计仪表板
  D. 性能与扩展 (3): V413 无批量写入 / V414 无并发压力模型 / V415 无Collection级缓存策略
  E. 氛围编程适配 (4): V416 无按Session成熟度预算 / V417 无时间衰减 / V418 无负反馈闭环 / V419 无跨Collection检索
  F. 安全与治理 (3): V420 无PII检测 / V421 无检索审计链 / V422 无Collection级RBAC
  G. 1人+AI运维 (4): V423 无一键健康检查 / V424 无SQLite自动维护 / V425 无状态恢复摘要 / V426 无迁移零停机SLA
  H. 集成与数据流 (3): V427 无导出/导入API / V428 无模型健康检查 / V429 无引用完整性校验
  I. 成本与资源 (2): V430 无耗时追踪 / V431 无存储增长预测
  J. 测试与验证 (2): V432 无语义搜索CI / V433 无向量完整性校验
  每完成一个盲点关闭：在对应模块文件中添加注释 # closes V-VMS-XXXX
  优先级 P0 (12盲点) 在 Phase 1.5 完成：V401/V402/V405/V409/V411/V416/V417/V419/V420/V423/V424/V425
  优先级 P1 (12盲点) 在 Phase 2-3 并行完成
  优先级 P2 (9盲点) 在 Phase 4+ 运维期完成
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cache_layer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\provenance_enforcer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\retrieval_feedback.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cross_collection_retriever.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"
    description: "追加 closes V401(mmR)/V402(MMR)/V403(查询改写)/V404(意图分类)/V417(时间衰减)/V419(跨Collection检索)/V511(查询超时)/V512(分页)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
    description: "追加 closes V405(量化)/V406(HNSW调优)/V407(新鲜度SLA)/V408(重建自动化)/V423(一键健康)/V424(SQLite维护)/V433(完整性校验)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
    description: "追加 closes V409(去重)/V410(overlap)/V411(过时检测)/V412(统计仪表板)/V413(批量写入)/V414(并发压力模型)/V429(引用完整性)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cache_layer.py"
    description: "追加 closes V415(Collection级缓存) / V430(耗时追踪) / V431(存储增长预测)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\retrieval_feedback.py"
    description: "追加 closes V418(负反馈闭环) / V421(检索审计链)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\provenance_enforcer.py"
    description: "追加 closes V420(PII检测) / V422(RBAC)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
    description: "追加 closes V425(状态恢复摘要) / V426(零停机SLA) / V427(导出/导入API)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
    description: "追加 closes V428(模型健康检查)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
    description: "追加 closes V416(按Session成熟度预算)——search() 中按 session_maturity_level 控制 k 和 collection 范围"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_vector_memory.py"
    description: "追加 closes V432(语义搜索CI)——30-50条基准查询 + recall@5>=0.8 断言"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cache_layer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\provenance_enforcer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\retrieval_feedback.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cross_collection_retriever.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_vector_memory.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2——所有盲点关闭产生的数据模型"
  - module_id: "GOV-TASK-005"
    section: "全篇"
    reason: "关闭三步法——每个盲点关闭三步独立验证"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§13 R1 33盲点——每个盲点的编号/描述/SOD/RPN/触发场景/优先级完整定义 + §13.12 优先级分组"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
  - "M4"
estimated_tokens: 30000
timeout_minutes: 120

acceptance_criteria:
  - "全部 33 个盲点 V-VMS-401 ~ V-VMS-433 在对应模块中有 # closes V-VMS-XXXX 注释"
  - "P0 12盲点全部在 Phase 1.5 前完成代码实现"
  - "V401 关闭：tests/unit/test_vector_memory.py 包含 50 条标准查询 gold set + recall@5 计算"
  - "V402 关闭：hybrid_search 可选 MMR diversity re-ranking 参数 mmr_lambda=0.5"
  - "V405 关闭：index_health_monitor 支持 scalar quantization int8 压缩选项"
  - "V409 关闭：collection_manager.add() 写入前 SHA256 指纹查重"
  - "V411 关闭：source_document_change → 标记旧向量 stale → 自动触发重嵌入"
  - "V416 关闭：InProcessVectorMemory.search() 接受 session_maturity 参数控制结果 token 预算"
  - "V417 关闭：RRF 融合时加入 time_decay = e^(-λ·age_days)"
  - "V419 关闭：CrossCollectionRetriever.search_across() 跨 Collection 联合检索"
  - "V420 关闭：写入前 input_sanitizer 扫描 secrets patterns"
  - "V423 关闭：python -m zephyr.vector_memory health 输出健康面板"
  - "V424 关闭：cron 脚本包含 SQLite WAL checkpoint + VACUUM + ANALYZE"
  - "V425 关闭：vms_status_recovery_summary() 输出离开期间变更摘要"

rollback_instructions: |
  1. 盲点关闭导致功能异常 → 每个盲点有独立 feature flag 可关闭（VMS_FLAG_{V-VMS-XXXX}=disabled）
  2. 逐盲点回滚——单盲点关闭失败不影响其他盲点关闭
  3. 如果 33 盲点全量回滚 → git revert 对应 commit 或还原全部 touch 文件到盲点关闭前版本

depends_on:
  - "TASK-INF-0216"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
  - "data"
  - "governance"
  - "security"
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
