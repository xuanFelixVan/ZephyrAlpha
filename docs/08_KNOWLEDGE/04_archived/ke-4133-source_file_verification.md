---
module_id: KE-3978----001
title: 2. Source File Verification (§12.1)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2. Source File Verification (§12.1)

2. Source File Verification (§12.1)

| 文件 | 预期 | 验证 |
|------|:---:|------|
| context_assembler.py | ✅ 292 行 | os.path.exists + lines check |
| context_budget_tracker.py | ✅ 227 行 | os.path.exists + lines check |
| context_injector.py | ✅ 升级 | os.path.exists |
| context_rot_model.py | ✅ 新建 | os.path.exists |
| context_evictor.py | ✅ 新建 | os.path.exists |
| doc_compressor.py | ✅ 563 行 | os.path.exists + lines check |
| intent_keyword_mapper.py | ✅ | os.path.exists |
| intent_parser.py | ✅ | os.path.exists |
| pattern_library.py | ✅ | os.path.exists |
| prompt_registry.py | ✅ | os.path.exists |
| system_snapshot.py | ✅ | os.path.exists |
| architecture-context.json | ✅ | os.path.exists |
| task_validator.py | ❌ | 验证不存在 |
| pipeline_orchestrator.py | ❌ | 验证不存在 |
| vector_bridge.py | ❌ | 验证不存在 |
