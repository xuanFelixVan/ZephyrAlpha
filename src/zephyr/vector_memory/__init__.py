"""Vector Memory Service (VMS) — 过渡期门面层（正式架构表述）
=============================================================

**过渡期（AUDIT-08 冻结表述）**

- **当前 SSOT 实现**：``zephyr.kb.unified_memory_api`` 的 ``UnifiedMemoryAPI`` +
  本包 ``UnifiedVectorMemoryAdapter(VectorMemoryBase)`` 委托至上述 API。
- **用途**：满足蓝图/契约对 ``zephyr.vector_memory`` 包名的引用，避免「点名包 vs 实际实现」割裂。
- **后续演进**：独立 VMS 进程、Chroma 专用 collection、BGE 嵌入等，在 **本包内** 替换委托层；对上层保持 import 面稳定。

**历史病根（归档）**

原计划独立 VMS/Chroma BGE 后端尚未单独进程化时，曾表现为 ``vector_memory/`` 「空壳」审计项；现以门面 + 委托闭环。

本条目的职责
------------
1. **单一入口**：导出 ``UnifiedMemoryAPI`` / ``get_unified_memory_api``，与 RI-02 记忆三件套对齐。
2. **接口骨架**：导出 ``VectorMemoryBase`` / ``EmbeddingEngineBase`` — Phase B 契约对齐。
3. **演进占位**：下表为规划后端，**非**当前包内独立实现。

规划架构（后续在本包内可替换委托）
--------------------------------
- 存储后端: ChromaDB 0.6
- 嵌入模型: BGE-M3 ONNX
- 5 大 Collection: decisions / code_context / lessons / knowledge / runtime_logs
"""

from __future__ import annotations

from zephyr.kb.unified_memory_api import UnifiedMemoryAPI, get_unified_memory_api
from zephyr.vector_memory.delegated_vector_memory import UnifiedVectorMemoryAdapter
from zephyr.vector_memory.interface import (
    EmbeddingEngineBase,
    MemoryEntry,
    VectorMemoryBase,
)

__all__ = [
    "UnifiedMemoryAPI",
    "UnifiedVectorMemoryAdapter",
    "get_unified_memory_api",
    "VectorMemoryBase",
    "EmbeddingEngineBase",
    "MemoryEntry",
]
