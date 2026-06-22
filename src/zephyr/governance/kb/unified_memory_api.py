# [A_module] module_id=MOD-DAT_unified_memory_api | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §

# [MODULE] zephyr.data.knowledge_management.kb.unified_memory_api

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
SRC-0042: Re-export shim → 真源在 kb/storage/unified_memory_api.py

本文件仅重新导出 storage/unified_memory_api.py 的符号以保证向后兼容。
所有外部调用方（context_engine, bootstrap, mcp, vector-memory 等）无需修改 import 路径。

创建日期 : 2026-05-10
真源      : src/zephyr/kb/storage/unified_memory_api.py
"""

from zephyr.governance.kb.storage.unified_memory_api import (
    DEFAULT_EMBEDDING_MODELS,
    # 常量
    UNIFIED_COLLECTION,
    ChromaMemoryBackend,
    InMemoryMemoryBackend,
    # 后端协议与实现
    MemoryBackend,
    MemoryBackendError,
    MemoryRecord,
    # API 类
    UnifiedMemoryAPI,
    # 数据模型
    WriteTrace,
    # 异常
    WriteTraceMissing,
    build_provenance,
    # 工厂函数
    get_unified_memory_api,
)

__all__ = [
    "DEFAULT_EMBEDDING_MODELS",
    "UNIFIED_COLLECTION",
    "ChromaMemoryBackend",
    "InMemoryMemoryBackend",
    "MemoryBackend",
    "MemoryBackendError",
    "MemoryRecord",
    "UnifiedMemoryAPI",
    "WriteTrace",
    "WriteTraceMissing",
    "build_provenance",
    "get_unified_memory_api",
]
