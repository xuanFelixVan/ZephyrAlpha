---
doc_type: architecture_view
title: D-KNOWLEDGE 知识管理架构图
version: "1.0"
status: active
date: 2026-06-27
owner: auto-generator
ttl: permanent
---

# 41_d_knowledge / 知识管理 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示知识管理（D-KNOWLEDGE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-27 03:08:24
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 知识管理（D-KNOWLEDGE）的模块分布。共 40 个模块 / 40 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (40 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   architecture_model/layers/b_vector_memory.yaml  [production]   │
│   docs__03_modules___domain_knowledge__knowledge_base__bluepr... │
│   docs__03_modules___domain_knowledge__vector_memory__bluepri... │
│   src/zephyr/governance/vector_memory/__init__.py  [prototype]   │
│   src/zephyr/governance/vector_memory/bm25_index.py  [prototype] │
│   src/zephyr/governance/vector_memory/bridge_layer.py  [proto... │
│   src/zephyr/governance/vector_memory/cache_layer.py  [protot... │
│   src/zephyr/governance/vector_memory/chunk_strategy_router.p... │
│   src/zephyr/governance/vector_memory/collection_manager.py  ... │
│   src/zephyr/governance/vector_memory/collection_schemas.py  ... │
│   src/zephyr/governance/vector_memory/context_ingest.py  [pro... │
│   src/zephyr/governance/vector_memory/cross_collection_retrie... │
│   src/zephyr/governance/vector_memory/delegated_vector_memory... │
│   src/zephyr/governance/vector_memory/design_principles.py  [... │
│   src/zephyr/governance/vector_memory/faiss_collection_manage... │
│   src/zephyr/governance/vector_memory/hybrid_retriever.py  [p... │
│   src/zephyr/governance/vector_memory/in_memory_fake_vms.py  ... │
│   src/zephyr/governance/vector_memory/in_memory_memory_backen... │
│   ...还有 22 个模块 / 22 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 40 个模块 / 40 modules）。

### L1 基础层 / Foundation Layer (40 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | architecture_model/layers/b_vector_memory.yaml | architecture_model/layers/b_vector_me... | production | deprecated |
| 2 | docs/03_modules/_domain_knowledge/knowledge_base/blueprin... | docs__03_modules___domain_knowledge__... | design | planned |
| 3 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | docs__03_modules___domain_knowledge__... | design | planned |
| 4 | src/zephyr/governance/vector_memory/__init__.py | src/zephyr/governance/vector_memory/_... | prototype | generated |
| 5 | src/zephyr/governance/vector_memory/bm25_index.py | src/zephyr/governance/vector_memory/b... | prototype | generated |
| 6 | src/zephyr/governance/vector_memory/bridge_layer.py | src/zephyr/governance/vector_memory/b... | prototype | generated |
| 7 | src/zephyr/governance/vector_memory/cache_layer.py | src/zephyr/governance/vector_memory/c... | prototype | generated |
| 8 | src/zephyr/governance/vector_memory/chunk_strategy_router.py | src/zephyr/governance/vector_memory/c... | prototype | generated |
| 9 | src/zephyr/governance/vector_memory/collection_manager.py | src/zephyr/governance/vector_memory/c... | prototype | generated |
| 10 | src/zephyr/governance/vector_memory/collection_schemas.py | src/zephyr/governance/vector_memory/c... | prototype | generated |
| 11 | src/zephyr/governance/vector_memory/context_ingest.py | src/zephyr/governance/vector_memory/c... | prototype | generated |
| 12 | src/zephyr/governance/vector_memory/cross_collection_retr... | src/zephyr/governance/vector_memory/c... | prototype | generated |
| 13 | src/zephyr/governance/vector_memory/delegated_vector_memo... | src/zephyr/governance/vector_memory/d... | prototype | generated |
| 14 | src/zephyr/governance/vector_memory/design_principles.py | src/zephyr/governance/vector_memory/d... | prototype | generated |
| 15 | src/zephyr/governance/vector_memory/faiss_collection_mana... | src/zephyr/governance/vector_memory/f... | prototype | generated |
| 16 | src/zephyr/governance/vector_memory/hybrid_retriever.py | src/zephyr/governance/vector_memory/h... | prototype | generated |
| 17 | src/zephyr/governance/vector_memory/in_memory_fake_vms.py | src/zephyr/governance/vector_memory/i... | prototype | generated |
| 18 | src/zephyr/governance/vector_memory/in_memory_memory_back... | src/zephyr/governance/vector_memory/i... | prototype | generated |
| 19 | src/zephyr/governance/vector_memory/in_process_vector_mem... | src/zephyr/governance/vector_memory/i... | prototype | generated |
| 20 | src/zephyr/governance/vector_memory/index_health_monitor.py | src/zephyr/governance/vector_memory/i... | prototype | generated |
| 21 | src/zephyr/governance/vector_memory/interface.py | src/zephyr/governance/vector_memory/i... | prototype | generated |
| 22 | src/zephyr/governance/vector_memory/migrate_chroma_to_fai... | src/zephyr/governance/vector_memory/m... | prototype | generated |
| 23 | src/zephyr/governance/vector_memory/ollama_chat.py | src/zephyr/governance/vector_memory/o... | prototype | generated |
| 24 | src/zephyr/governance/vector_memory/ollama_embedding.py | src/zephyr/governance/vector_memory/o... | prototype | generated |
| 25 | src/zephyr/governance/vector_memory/provenance_enforcer.py | src/zephyr/governance/vector_memory/p... | prototype | generated |
| 26 | src/zephyr/governance/vector_memory/retrieval_feedback.py | src/zephyr/governance/vector_memory/r... | prototype | generated |
| 27 | src/zephyr/governance/vector_memory/sqlite_metadata_store.py | src/zephyr/governance/vector_memory/s... | prototype | generated |
| 28 | src/zephyr/governance/vector_memory/vms_errors.py | src/zephyr/governance/vector_memory/v... | prototype | generated |
| 29 | src/zephyr/governance/vector_memory/vms_schemas.py | src/zephyr/governance/vector_memory/v... | prototype | generated |
| 30 | src/zephyr/knowledge/__init__.py | src/zephyr/knowledge/__init__.py | prototype | deprecated |
| 31 | src/zephyr/knowledge/_extensions/__init__.py | src/zephyr/knowledge/_extensions/__in... | prototype | deprecated |
| 32 | src/zephyr/knowledge/api/__init__.py | src/zephyr/knowledge/api/__init__.py | prototype | deprecated |
| 33 | src/zephyr/knowledge/core/__init__.py | src/zephyr/knowledge/core/__init__.py | prototype | deprecated |
| 34 | src/zephyr/knowledge/infrastructure/__init__.py | src/zephyr/knowledge/infrastructure/_... | prototype | deprecated |
| 35 | src/zephyr/knowledge/models/__init__.py | src/zephyr/knowledge/models/__init__.py | prototype | deprecated |
| 36 | src/zephyr/knowledge/services/__init__.py | src/zephyr/knowledge/services/__init_... | prototype | deprecated |
| 37 | tests/test_skill_knowledge_base.py | tests/test_skill_knowledge_base.py | prototype | generated |
| 38 | tests/test_vector_memory_root.py | tests/test_vector_memory_root.py | prototype | deprecated |
| 39 | tests/unit/vector_memory/__init__.py | tests/unit/vector_memory/__init__.py | prototype | deprecated |
| 40 | tests/unit/vector_memory/test_vector_memory.py | tests/unit/vector_memory/test_vector_... | prototype | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 5 条 / 5 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│        依赖关系图 / Dependency Graph (共 5 条 / 5 edges)         │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 1                               │
│   [config_depends]: 5 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (5 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   bm25_index.py → __init__.py                                    │
│   cross_collection_retrieve... → __init__.py                     │
│   interface.py → __init__.py                                     │
│   in_memory_memory_backend.py → __init__.py                      │
│   vms_errors.py → __init__.py                                    │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `41_d_knowledge_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
