"""
SRC-0042: Re-export shim → 真源在 kb/storage/unified_memory_api.py

本文件仅重新导出 storage/unified_memory_api.py 的符号以保证向后兼容。
所有外部调用方（context_engine, bootstrap, mcp, vector_memory 等）无需修改 import 路径。

创建日期 : 2026-05-10
真源      : src/zephyr/kb/storage/unified_memory_api.py
"""

from zephyr.kb.storage.unified_memory_api import (
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
    "WriteTrace",
    "MemoryRecord",
    "MemoryBackend",
    "ChromaMemoryBackend",
    "InMemoryMemoryBackend",
    "UnifiedMemoryAPI",
    "WriteTraceMissing",
    "MemoryBackendError",
    "UNIFIED_COLLECTION",
    "DEFAULT_EMBEDDING_MODELS",
    "get_unified_memory_api",
    "build_provenance",
]
