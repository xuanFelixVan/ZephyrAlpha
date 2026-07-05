# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] zephyr.governance.kb.batch_ingest (re-export shim)
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.kb.pipeline.batch_ingest
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim — 真源在 zephyr.governance.kb.pipeline.batch_ingest（SSoT 收敛 2026-07-06）
# [MODIFY-GUARD] 禁止在此文件定义新符号；变更请到真源 pipeline/batch_ingest.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_batch_ingest | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export shim — 真源在 zephyr.governance.kb.pipeline.batch_ingest（SSoT 收敛 2026-07-06）。

本文件仅重新导出 pipeline/batch_ingest.py 的符号以保证向后兼容。
真源：src/zephyr/governance/kb/pipeline/batch_ingest.py
"""
from zephyr.governance.kb.pipeline.batch_ingest import (  # noqa: F401
    BatchIngestEntry,
    BatchIngestReport,
    BatchIngestor,
)

__all__ = [
    "BatchIngestEntry",
    "BatchIngestReport",
    "BatchIngestor",
]
