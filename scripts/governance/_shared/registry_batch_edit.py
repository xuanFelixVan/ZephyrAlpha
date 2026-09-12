# [BLUEPRINT] MOD-GOV_ALGO_EXTRACTOR | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
# [MODULE] scripts.governance._shared.registry_batch_edit
# [TTL] permanent
# re-export 壳（对标 _shared/file_utils.py 惯例）：真源在 scripts/governance/registry_batch_edit.py
"""registry_batch_edit re-export 壳——真源单一（scripts/governance/registry_batch_edit.py）。

 Usage: from _shared.registry_batch_edit import insert_blocks, verify_pure_insertion
"""

from registry_batch_edit import (  # noqa: F401
    RegistryEditResult,
    insert_blocks,
    verify_pure_insertion,
)

__all__ = ["RegistryEditResult", "insert_blocks", "verify_pure_insertion"]
