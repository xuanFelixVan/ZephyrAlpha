---
module_id: KE-3833
title: 12.1 源文件
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 12.1 源文件

12.1 源文件

| 文件 | 磁盘 | 说明 |
|------|:---:|------|
| `context_assembler.py` | ✅ 292行 | Build阶段——组装上下文 |
| `context_budget_tracker.py` | ✅ 227行 | Token预算三级管理 |
| `context_injector.py` | ✅ 升级 | Inject阶段——加 provenance 溯源字段 |
| `context_rot_model.py` | ✅ 新建 | beta a——n² attention 衰减数学模型 |
| `context_evictor.py` | ✅ 新建 | beta a——三维排序上下文逐出器 |
| `doc_compressor.py` | ✅ 563行 | 完整实现——Immutable Core+不变量校验+三级降级 |
| `intent_keyword_mapper.py` | ✅ | intent→keyword映射表 |
| `intent_parser.py` | ✅ | 意图分类NLP |
| `pattern_library.py` | ✅ | pattern模板库 |
| `prompt_registry.py` | ✅ | prompt注册表 |
| `system_snapshot.py` | ✅ | 系统状态快照 |
| `architecture-context.json` | ✅ | 架构上下文数据 |
| `task_validator.py` | ❌ | beta待实现 |
| `pipeline_orchestrator.py` | ✅ ~6.2KB | 多阶段流水线编排 |
| `vector_bridge.py` | ✅ ~5.6KB | CE↔VMS桥接 |
