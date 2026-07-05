# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] zephyr.governance.kb._backend_protocol (re-export shim)
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.kb.storage._backend_protocol
# [CONSUMERS] zephyr.research.unified_memory_api; zephyr.knowledge.kb.vms_memory_backend
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim — 真源在 zephyr.governance.kb.storage._backend_protocol（SSoT 收敛 2026-07-06）
# [MODIFY-GUARD] 禁止在此文件定义新符号；变更请到真源 storage/_backend_protocol.py
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MemoryBackendError on backend failure; WriteTraceMissing on missing provenance
# [TESTS] tests/test_unified_memory_api.py; tests/test_vms_memory_backend.py
# [A_module] module_id=MOD-DAT__backend_protocol | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export shim — 真源在 zephyr.governance.kb.storage._backend_protocol（SSoT 收敛 2026-07-06）。

本文件仅重新导出 storage/_backend_protocol.py 的符号以保证向后兼容。
真源：src/zephyr/governance/kb/storage/_backend_protocol.py
"""
from zephyr.governance.kb.storage._backend_protocol import (  # noqa: F401
    InMemoryMemoryBackend,
    MemoryBackend,
    MemoryBackendError,
    MemoryRecord,
)

__all__ = [
    "InMemoryMemoryBackend",
    "MemoryBackend",
    "MemoryBackendError",
    "MemoryRecord",
]
