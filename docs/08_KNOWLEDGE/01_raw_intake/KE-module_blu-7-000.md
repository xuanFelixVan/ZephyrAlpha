---
module_id: KE-module_blu-7-000
title: 7. 产出物存放目录
category: module_blueprint
---

# 7. 产出物存放目录

7. 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\vector-memory\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\vector_memory\` | VMS 源码（11 个模块） |
| 过渡期代码 | `D:\ZephyrAlpha\src\zephyr\kb\chromadb_init.py` + `unified_memory_api.py` | 现有实现——Phase 2 后冻结 |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\test_vector_memory.py` | 单元测试 |
| ChromaDB 数据 | `D:\ZephyrAlpha\data\vector_db\` | ChromaDB 持久化目录 |
| 嵌入模型缓存 | `D:\ZephyrAlpha\models\bge-m3\` | BGE-M3 ONNX 模型文件 |
| 轻量模型缓存 | `D:\ZephyrAlpha\models\bge-small-zh-v1.5\` | 512d 轻量嵌入模型 |
| 嵌入缓存 | `D:\ZephyrAlpha\data\vector_db\_embedding_cache\` | Embedding memoization 持久化 |
| 索引快照 | `D:\ZephyrAlpha\data\vector_db\_snapshots\` | ChromaDB snapshot 备份 |

---
