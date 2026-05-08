---
task_id: "TASK-INF-0219"
source_blueprint: "MOD-INF-011"
source_section: "§14 第二轮深度交叉审计——7大维度22盲点 (V-VMS-501~522)"

title: "R2 盲点关闭——22 项 ChromaDB运维/嵌入模型工程化/Collection生命周期/查询基础设施/信任校准/故障级联/二阶效应盲点"
description: |
  关闭蓝图 §14 第二轮审计产生的全部 22 个盲点 (V-VMS-501 ~ V-VMS-522)：
  K. ChromaDB运维纵深 (4): V501 Client冲突防护 / V502 版本升级兼容性 / V503 Telemetry隐私 / V504 WAL无限增长
  L. 嵌入模型工程化 (3): V505 Token溢出截断 / V506 L2归一化 / V507 ONNX首次推理冷启动
  M. Collection生命周期 (3): V508 版本化与别名 / V509 软删除与恢复 / V510 访问热度追踪
  N. 查询基础设施 (3): V511 查询超时取消 / V512 检索结果分页 / V513 排序因果可解释性
  O. AI信任校准 (3): V514 可信度衰减标记 / V515 检索结果→AI决策追溯闭环 / V516 分歧信号矛盾检测
  P. 故障级联逃生 (3): V517 紧急只读模式 / V518 优雅劣化L0-L3 / V519 最小恢复路径
  Q. 氛围编程二阶效应 (3): V520 自我实现预言防护 / V521 上下文污染检测 / V522 新鲜度偏见补偿
  每个盲点在对应模块中关闭——代码注释 # closes V-VMS-5XX
  P0 13盲点优先关闭：V501/V502/V504/V505/V507/V511/V514/V515/V517/V518/V519/V520/V521
  P1 7盲点在并行施工中关闭
  P2 2盲点在运维期关闭
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\retrieval_feedback.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
    description: "追加 closes V501(单例lock检测)/V502(compatibility_check)/V517(emergency_readonly)/V518(graceful_degradation L0-L3)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
    description: "追加 closes V505(token溢出截断)/V506(L2归一化到期)/V507(warm-up推理时区)——延迟TASK-INF-0205未完成的实现"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
    description: "追加 closes V508(别名alias)/V509(soft_delete/recycle_bin)/V510(热度预加载)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"
    description: "追加 closes V512(分页offset)/V513(RRF+BM25分项可解释性)/V522(新鲜度偏见补偿)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\retrieval_feedback.py"
    description: "追加 closes V514(可信度衰减标记)/V515(检索→决策可追溯)/V516(矛盾信号检测)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
    description: "追加 closes V504(SQLite WAL checkpoint阈值)/V519(最小恢复路径优先级矩阵)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
    description: "追加 closes V520(同质化趋势扫描)/V521(错误记忆污染半径追踪)"
  - path: "D:\\ZephyrAlpha\\config\\vms\\vms_config.yaml"
    description: "追加 closes V502(ChromaDB version check) / V503(telemetry禁用以confirmed)"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\retrieval_feedback.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
  - "D:\\ZephyrAlpha\\config\\vms\\vms_config.yaml"

forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2——VMS 故障模式/EmergencyMode 枚举"
  - module_id: "ADR-0031"
    section: "全篇"
    reason: "ChromaDB 0.6 源码级运维——dual client(§14.2)/WAL checkpoint"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§14 R2 22盲点——ChromaDB纵深/嵌入工程化/Collection生命周期/查询基础设施/信任校准/故障级联/二阶效应完整定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
  - "M4"
estimated_tokens: 25000
timeout_minutes: 120

acceptance_criteria:
  - "全部 22 个盲点 V-VMS-501 ~ V-VMS-522 在对应模块中有 # closes V-VMS-5XX 注释"
  - "V501 closed: PersistentClient 单例模式——通过文件锁检测已有 client + 禁止创建双实例"
  - "V502 closed: compatibility_check()——检测 ChromaDB 版本兼容性→版本不匹配时禁止启动"
  - "V504 closed: PRAGMA wal_checkpoint(TRUNCATE) 在 cron 中自动执行 + auto_checkpoint阈值"
  - "V505 closed: 超长文本(>8192tokens)→分块分别嵌入取均值 + metadata.truncated=True"
  - "V507 closed: warm-up inference 用已知文本——区分首次/后续推理超时"
  - "V511 closed: search(timeout_ms=2000)——超时后返回 partial=True 标记"
  - "V514 closed: trust_decay: {age_score, provenance_score, collection_confidence}"
  - "V515 closed: 决策可追溯——VMS→检索结果→AI context→Decision D 完整链路"
  - "V517 closed: emergency_readonly(reason)——5触发条件(磁盘<5%/写入风暴>1000/min等)"
  - "V518 closed: graceful_degradation L0-L3——L0正常/L1降k值/L2仅bge-small/L3仅InMemory"
  - "V519 closed: 最小恢复路径——恢复优先级矩阵(rules:42条/lessons:50条/knowledge:20条)"
  - "V520 closed: 定期扫描同质化 trends→触发 Owner 审查"
  - "V521 closed: modelled污染半径——写入 lessons 时标记 verification_status(verified/unverified/disputed)"

rollback_instructions: |
  1. V517 emergency_readonly 误触发 → 手动重置 VMS 状态：python -m zephyr.vector_memory mode reset
  2. V519 最小恢复路径验证——恢复少于阈值条目时告警
  3. 逐盲点回滚——每个盲点有独立 VMS_FLAG_{V-VMS-5XX}=disabled feature flag
  4. compatibility_check 过于严格阻止正常启动 → VMS_SKIP_COMPAT_CHECK=1

depends_on:
  - "TASK-INF-0218"
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
